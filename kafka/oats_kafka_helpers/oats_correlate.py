#!/usr/bin/env python
from __future__ import with_statement
from oatspsql import oatspsql
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
import EventProcessor


CACHE_SIZE = 1000

# cache for recognizing if an event has occured in a given timeframe
cache = None


def aggregate(data, host, timestamp, severity, error, sensor_type,
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
    cache_id = 'aggregate' + event_name
    lock = threading.Lock()
    lock.acquire()
    current_case = None
    if cache is None or cache_id not in cache or error not in cache[cache_id]:
        # first thread initializes and populates dict
        __init_cache(error, cache_id, correlate_for)
    else:
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

    if cache[cache_id][error]['counter'] == n_of_events:
        if use_oats_case:
            __update_db_case(current_case, cache[cache_id][error]['counter'], event_name, event_name)
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     type=sensor_type, event_name=event_name, severity=severity,
                                     case=current_case)
    else:
        if use_oats_case:

            __update_db_case(current_case, cache[cache_id][error]['counter'], event_name, alternative_event_name)

        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     type=sensor_type, event_name=alternative_event_name, severity=severity,
                                     case=current_case)


def compress(data, host, timestamp, severity, error, sensor_type,
             event_name, correlate_for=10, use_oats_case=False):
    cache_id = 'compress' + event_name
    lock = threading.Lock()
    lock.acquire()
    current_case = None
    if cache is None or cache_id not in cache or error not in cache[cache_id]:
        # first thread initializes and populates dict
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
                             solution='Waiting for {0} seconds to compress events.'.format(correlate_for))

    # compress events
    time.sleep(correlate_for)

    if use_oats_case:
        __update_db_case(current_case, cache[cache_id][error]['counter'], event_name, event_name)
    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 type=sensor_type, event_name=event_name, severity=severity,
                                 case=current_case)


def __init_cache(error, cache_id, count_for=10):
    global cache
    cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=count_for + 3)
    cache[cache_id] = {}
    cache[cache_id][error] = {}
    cache[cache_id][error]['counter'] = 1


def __update_db_case(current_case, counter, event_name, identifier):
    oatspsql.update_case(current_case,
                         solution='Time passed: {0} event counter is {1}. Sending {0}:'
                                  '{2} event to salt master'.format(event_name, counter, identifier))


def __create_db_case(error, host, function_name):
    return oatspsql.create_case(error, host,
                                solution='Case started in kafka event consumer: correlate.' + function_name)

