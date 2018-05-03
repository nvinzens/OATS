#!/usr/bin/env python
from __future__ import with_statement
from oats import oatsdbhelpers
from oatspsql import oatspsql
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
import EventProcessor


CACHE_SIZE = 1000

# cache for recognizing if an event has occured in a given timeframe
cache = None
current_case = None
lock = threading.Lock()


def aggregate(data, host, timestamp, severity, error,
              salt_id, n_of_events, alternative_id, count_for, use_oats_case):
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
    global cache
    lock.acquire()

    if cache is None or error not in cache:
        # first thread initializes and populates dict
        cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=count_for + 3)
        cache[error] = {}
        cache[error]['counter'] = 1
        if use_oats_case:
            global current_case
            current_case = oatspsql.create_case(error, host, solution='Case started in kafka event consumer:'
                                                                           ' aggregate.correlate().')
    else:
        # later threads increment counter
        cache[error]['counter'] += 1
        lock.release()
        return
    lock.release()
    if use_oats_case:
        oatspsql.update_case(current_case,
                                  solution='Waiting for {0} seconds to aggregate events.'
                                           ' Required amount of events: {1}'.format(count_for, n_of_events))
    # wait for additional events
    time.sleep(count_for)

    if cache[error]['counter'] == n_of_events:
        if use_oats_case:
            __update_db_case(cache[error]['counter'], error, salt_id)
        event_name = 'napalm/syslog/*/' + error + '/' + salt_id
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     type='syslog', event_name=event_name, severity=severity,
                                     case=current_case)
    else:
        if use_oats_case:
            __update_db_case(cache[error]['counter'], error, alternative_id)
        event_name = 'napalm/syslog/*/' + error + '/' + alternative_id
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     type='syslog', event_name=event_name, severity=severity,
                                     case=current_case)


def __update_db_case(counter, error, identifier):
    oatspsql.update_case(current_case,
                              solution='Time passed. {0} event counter is {1}. Sending {0}:'
                                       '{2} event to salt master'.format(error, counter, identifier))


