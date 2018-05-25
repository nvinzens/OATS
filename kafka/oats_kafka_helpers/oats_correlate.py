#!/usr/bin/env python
from __future__ import with_statement
from oatspsql import oatspsql
from oatsinflux import oatsinflux
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
import EventProcessor
import logging
import logging.config
import yaml

log_file = open('etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.kafka.helpers')

CACHE_SIZE = 1000

# cache for recognizing if an event has occured in a given timeframe
cache = None


def aggregate_identical(data, host, timestamp, severity, error, sensor_type,
                        event_name, n_of_events=None, alternative_event_name=None, correlate_for=None, use_oats_case=False):
    '''
    Aggregates the event (given by the error) to other events that occured
    in a given time frame. For every recognized event in the system that
    needs to be aggregated atleast one optional workflow has to exist
    for aggregation to make sense.
    Sends an event to the salt event bus, once aggregation has determined
    which workflow needs to be executed.
    Should be executed asynchronous, since the method will block for
    MAX_AGE time.
    :param data: passed through for the workflow in salt
    :param host: The host from which the event originated
    :param origin_ip: The hosts IP address
    :param tag: The event tag
    :param message_details: passed through for the workflow in salt
    :param error: The event that is correlated
    :param salt_identifier: decides which workflow gets executed.
    eg. 'dead_timer_expired' will execute tshoot.ospf_nbr_down
    :return: None
    '''
    oatsinflux.write_event(host, timestamp, sensor_type, event_name, severity, data)
    cache_id = 'aggregate' + event_name
    lock = threading.Lock()
    lock.acquire()
    current_case = None
    if cache is None or cache_id not in cache or error not in cache[cache_id]:
        # first thread initializes and populates dict
        logger.debug('Starting aggregation of [{0}] events'.format(event_name))
        __init_cache(error, cache_id, correlate_for)
    else:
        logger.debug('Additional [{0}] event detected. Incrementing counter...'
                     .format(event_name))
        # later threads increment counter
        cache[cache_id][error]['counter'] += 1
        lock.release()
        return
    lock.release()
    if use_oats_case:
        current_case = __create_db_case(error, host, 'aggregate')
        oatspsql.update_case(current_case,
                             solution='Waiting for {0} seconds to aggregate events.'
                                      ' Required amount of events: {1}'.format(correlate_for, n_of_events))

    # wait for additional events
    time.sleep(correlate_for)
    logger.debug('Aggregation finished. Event counter for event [{0}] is: {1}.'
                 .format(event_name, cache[cache_id][error]['counter']))
    if cache[cache_id][error]['counter'] == n_of_events:
        if use_oats_case:
            __update_db_case(current_case, cache[cache_id][error]['counter'], event_name)
        logger.debug('Aggregation successful.'
                     .format(event_name))
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     sensor_type=sensor_type, event_name=event_name, severity=severity,
                                     case=current_case, influx_write=False)
    else:
        if use_oats_case:

            __update_db_case(current_case, cache[cache_id][error]['counter'], event_name)
        logger.debug('Aggregation not successful.'
                     .format(alternative_event_name))
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     sensor_type=sensor_type, event_name=alternative_event_name, severity=severity,
                                     case=current_case, influx_write=False)


def aggregate_distinct(data, host, timestamp, severity, error, sensor_type,
                       event_name, distinct_events, aggregation_event_name=None,
                       correlate_for=None, use_oats_case=False):
    '''

    :param data:
    :param host:
    :param timestamp:
    :param severity:
    :param error:
    :param sensor_type:
    :param event_name:
    :param distinct_events: dict of the form { event_name: amount_of_events }
    :param n_of_events:
    :param alternative_event_name:
    :param correlate_for:
    :param use_oats_case:
    :return:
    '''
    oatsinflux.write_event(host, timestamp, sensor_type, event_name, severity, data)
    cache_id = 'aggregate_distinct' + error
    lock = threading.Lock()
    lock.acquire()
    if not 'event_names' in locals():
        event_names = []
    current_case = None

    if cache is None or cache_id not in cache or host+event_name not in cache[cache_id]:
        logger.debug('Starting aggregation of distinct events...')
        # first thread initializes and populates dict
        __init_cache(host+event_name, cache_id, correlate_for,host=host, additional_events=distinct_events.keys())
        event_names.append(host+event_name)
    else:
        logger.debug('Additional (distinct) event detected, incrementing counter...')
        # later threads increment counter
        cache[cache_id][host+event_name]['counter'] += 1
        event_names.append(host+event_name)
        lock.release()
        return
    lock.release()
    if use_oats_case:
        current_case = __create_db_case(error, host, 'aggregate')
        oatspsql.update_case(current_case,
                             solution='Waiting for {0} seconds to aggregate distinct events.'.format(correlate_for))

    # wait for additional events
    time.sleep(correlate_for)
    success = True
    for event in event_names:
        if not cache[cache_id][event]['counter'] >= distinct_events[event[3:]]:
            success = False
            break
    if success:
        if use_oats_case:
            oatspsql.update_case(current_case,
                                 solution='Aggregation successful: sending `{0}` event to salt master.'
                                 .format(aggregation_event_name))
        logger.debug('Aggregation successful.'
                     .format(aggregation_event_name))
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     sensor_type=sensor_type, event_name=aggregation_event_name, severity=severity,
                                     case=current_case, influx_write=False)
    else:
        if use_oats_case:
            oatspsql.update_case(current_case,
                                 solution='Aggregation not successful: sending `{0}` event to salt master.'
                                 .format(event_name))
        logger.debug('Aggregation not successful.'
                     .format(event_name))
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     sensor_type=sensor_type, event_name=event_name, severity=severity,
                                     case=current_case, influx_write=False)


def compress(data, host, timestamp, severity, error, sensor_type,
             event_name, correlate_for=10, use_oats_case=False):
    oatsinflux.write_event(host, timestamp, sensor_type, event_name, severity, data)
    cache_id = 'compress' + event_name
    lock = threading.Lock()
    lock.acquire()
    current_case = None
    if cache is None or cache_id not in cache or error not in cache[cache_id]:
        # first thread initializes and populates dict
        logger.debug('Starting compression of [{0}] events...'.format(event_name))
        __init_cache(error, cache_id, correlate_for)
    else:
        # later threads increment counter
        cache[cache_id][error]['counter'] += 1
        lock.release()
        return
    lock.release()
    if use_oats_case:
        current_case = __create_db_case(error, host, 'compress')
        oatspsql.update_case(current_case,
                             solution='Waiting for {0} seconds to compress {1} events.'.format(correlate_for, event_name))

    # compress events
    time.sleep(correlate_for)
    logger.debug('Compression finished, amount of compressed [{0}] events: {1}.'
                 .format(event_name, cache[cache_id][error]['counter']))
    if use_oats_case:
        __update_db_case(current_case, cache[cache_id][error]['counter'], event_name)
    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 sensor_type=sensor_type, event_name=event_name, severity=severity,
                                 case=current_case, influx_write=False)


def __init_cache(error, cache_id, count_for=10, host=None, additional_events=None):
    global cache
    if not cache:
        cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=count_for + 3)
    if cache_id not in cache:
        cache[cache_id] = {}
    if additional_events is not None:
        for event in additional_events:
            if not host+event in cache[cache_id]:
                cache[cache_id][host+event] = {}
                cache[cache_id][host+event]['counter'] = 0
    cache[cache_id][error] = {}
    cache[cache_id][error]['counter'] = 1


def __update_db_case(current_case, counter, event_name):
    oatspsql.update_case(current_case,
                         solution='Time passed: `{0}` event counter is {1}. Sending `{0}`'
                                  ' event to salt master'.format(event_name, counter))


def __create_db_case(error, host, function_name):
    return oatspsql.create_case(error, host,
                                solution='Case started in kafka event consumer: `correlate.' + function_name + '`')

