#!/usr/bin/env python
from __future__ import with_statement
from oatspsql import oatspsql
from oatsinflux import oatsinflux
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
import EventProcessor
import logging.config
import yaml

log_file = open('/etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.kafka.helpers')


# cache for recognizing if an event has occured in a given timeframe
CACHE_SIZE = 1000
cache = None


def aggregate_identical(data, host, timestamp, severity, error, sensor_type,
                        event_name, n_of_events=None, alternative_event_name=None, correlate_for=None, use_oats_case=False):
    '''
    Takes identical events and aggregates them. The first event will start the aggregation
    for the given amount of time. Each time an additional event of the same kind reaches
    this function a counter will incremented. Once the time passed, the counter is evaluated.
    If the counter is the same as the number stated in n_of_events an event with the event name
    "event_name" is generated. Else an event with the event name "alternative_event_name" is
    generated.
    :param data: the data of the event.
    :param host: the host from which the event originated.
    :param timestamp: the events timestamp.
    :param severity: the events severity.
    :param error: the events error eg. OSPF_NEIGHBOR_DOWN.
    :param sensor_type: the sensor which detected the event eg. syslog.
    :param event_name: the event name that is used when aggregation is successful.
    :param n_of_events: the needed amount of events for the aggregation to be successful.
    :param alternative_event_name: the alternative name if the aggregation is not successful.
    :param correlate_for: the amount of time to aggregate for.
    :param use_oats_case: if set will generate an oats case in psql.
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
    Takes distinct events and aggregates them. The first event will start the aggregation
    for the given amount of time. Each time an additional event that is given by distinct_events
     reaches this function a counter will incremented. Once the time passed, the counter is evaluated.
    If the counter is the same as the number stated in distinct_events an event with the event name
    "aggregation_event_name" is generated. Else an event with the event name "event_name" is
    generated.
    Note: the events do not have to be distinct, but for aggregation of identical events the use of
    aggregate_identical is suggested.
    :param data: the data of the event.
    :param host: the host from which the event originated.
    :param timestamp: the events timestamp.
    :param severity: the events severity.
    :param error: the events error eg. OSPF_NEIGHBOR_DOWN.
    :param sensor_type: the sensor which detected the event eg. syslog.
    :param event_name: the events event name.
    :param distinct_events: dict of the form { event_name: x_amount_of_events, event_name2: y_amount_of_events }
        eg. { 'syslog/*/INTERFACE_CHANGED/down': 2, 'syslog/*/INTERFACE_CHANGED/up': 2}
    :param aggregation_event_name: the event name to use if the aggregation is successful
    :param correlate_for: the amount of time to aggregate for.
    :param use_oats_case: if set will generate an oats case in psql.
    :return: None
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
    '''
    Takes event of the same kind and compresses them. Once the first event reaches this function
    it will stop the propagation of the same kind of function for the given amount of time.
    Once the time is passed it will send the first event to the salt master.
    :param data: the data of the event.
    :param host: the host from which the event originated.
    :param timestamp: the events timestamp.
    :param severity: the events severity.
    :param error: the events error eg. OSPF_NEIGHBOR_DOWN.
    :param sensor_type: the sensor which detected the event eg. syslog.
    :param event_name: the events event name.
    :param correlate_for: the amount of time to compress for.
    :param use_oats_case: if set will generate an oats case in psql.
    :return: None
    '''
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

