#!/usr/bin/env python
from __future__ import with_statement
from oats import oatsdbhelpers
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
import salt_event


# CONSTANTS (move to DB?)
INTERFACE_CHANGED = 'INTERFACE_CHANGED'
OSPF_NEIGHBOR_DOWN = 'OSPF_NEIGHBOR_DOWN'
OSPF_NEIGHBOR_UP = 'OSPF_NEIGHBOR_UP'
AGGREGATE_EVENTS = [OSPF_NEIGHBOR_DOWN]
EVENT_OPTIONAL_ARGS = {OSPF_NEIGHBOR_DOWN: 'dead_timer_expired'}
CACHE_SIZE = 1000
DEFAULT_COUNT_FOR = 10

# cache for recognizing if a given event has occured in a given timeframe
cache = None
lock = threading.Lock()


def aggregate(yang_message, minion, origin_ip, tag, message_details, error,
              salt_id, n_of_events, alternative_id, count_for, current_case):
    '''
    Aggregates the event (given by the error) to other events that occured
    in a given time frame. For every recognized event in the system that
    needs to be aggregated atleast one optional workflow has to exist
    for aggregation to make sense.
    Sends an event to the salt event bus, once aggregation has determined
    which workflow needs to be executed.
    Should be executed asynchronous, since the method will block for
    MAX_AGE time.
    :param yang_message: passed through for the workflow in salt
    :param minion: The host from which the event originated
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
        cache[error]['case'] = current_case
    else:
        # later threads increment counter
        cache[error]['counter'] += 1
        lock.release()
        return
    lock.release()
    print ('{0} event detected: Waiting for {1} seconds to gather event data. Required amount of events: {2}'.
           format(error, count_for, n_of_events))
    # wait for additional events
    time.sleep(count_for)

    if cache[error]['counter'] == n_of_events:
        __print_correlation_result(cache[error]['counter'], error, salt_id)
        salt_event.send_salt_event(yang_message, minion, origin_ip, tag, message_details,
                                   error, salt_id, case=cache[error]['case'])
    else:
        __print_correlation_result(cache[error]['counter'], error, alternative_id)
        salt_event.send_salt_event(yang_message, minion, origin_ip, tag, message_details,
                                   error, alternative_id, case=cache[error]['case'])


def __print_correlation_result(counter, error, optional_arg):
    print ('Time passed. {0} event counter is {1}. Sending {0}:'
           '{2} event to salt master'.format(error, counter, optional_arg))

