#!/usr/bin/env python
from __future__ import with_statement
from oats import oats
from expiringdict import ExpiringDict
import time
import threading
import salt_event


# CONSTANTS (move to DB?)
INTERFACE_CHANGED = 'INTERFACE_CHANGED'
OSPF_NEIGHBOR_DOWN = 'OSPF_NEIGHBOR_DOWN'
OSPF_NEIGHBOR_UP = 'OSPF_NEIGHBOR_UP'
CORRELATE_EVENTS = [OSPF_NEIGHBOR_DOWN]
EVENT_OPTIONAL_ARGS = {OSPF_NEIGHBOR_DOWN: 'dead_timer_expired'}
CACHE_SIZE = 1000
MAX_AGE = 10

# cache for not sending the same event multiple times
# event correlation only looks if in the last MAX_AGE seconds the same event occured
# and if it did, skips it
# can be refined, but needs to get data from the database for that
cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE+3) # +3 to give the function more time to evaluate dict
lock = threading.Lock()


def correlate(yang_message, minion, origin_ip, tag, message_details, error, optional_arg):
    global cache
    lock.acquire()
    if error not in cache:
        # first thread populates dict
        cache[error] = {}
        cache[error]['counter'] = 1
    else:
        # later threads increment counter
        cache[error]['counter'] += 1
        lock.release()
        return
    lock.release()
    current_case = oats.create_case(error, minion, status='solution_deployed')
    n_of_required_events = __get_n_of_required_events(error, minion, yang_message, current_case)
    print ('Waiting for {0} seconds to gather {1} event data. Required amount of events: {2}'.
           format(MAX_AGE, error, n_of_required_events))
    time.sleep(MAX_AGE)
    if cache[error]['counter'] == n_of_required_events:
        __print_correlation_result(cache[error]['counter'], error, optional_arg)
        salt_event.send_salt_event(yang_message, minion, origin_ip, tag, message_details,
                                   error, optional_arg, case=current_case)
    else:
        optional_arg = __get_optional_arg(error)
        __print_correlation_result(cache[error]['counter'], error, optional_arg)
        salt_event.send_salt_event(yang_message, minion, origin_ip, tag, message_details,
                                   error, optional_arg, case=current_case)


def __print_correlation_result(counter, error, optional_arg):
    print ('Time passed. {0} event counter is {1}. Sending {0}: '
           '{2} event to salt master'.format(error, counter, optional_arg))


def __get_n_of_required_events(error, minion, yang_message, case):
    if error == OSPF_NEIGHBOR_DOWN:
        interface = oats.get_interface(error, yang_message)
        root_host = oats.get_interface_neighbor(minion, interface, case=case)
        return len(oats.get_ospf_neighbors(root_host, case=case))
    return 0


def __get_optional_arg(error):
    if error == OSPF_NEIGHBOR_DOWN:
        return 'interface_down'
    return ''