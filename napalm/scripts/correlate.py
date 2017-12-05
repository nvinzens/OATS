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
CORRELATE_EVENTS = [OSPF_NEIGHBOR_DOWN]
EVENT_OPTIONAL_ARGS = {OSPF_NEIGHBOR_DOWN: 'dead_timer_expired'}
CACHE_SIZE = 1000
MAX_AGE = 10

# cache for recognizing if a given event has occured in a given timeframe
cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE+3) # +3 to give the function more time to evaluate dict
lock = threading.Lock()


def correlate(yang_message, minion, origin_ip, tag, message_details, error, optional_arg):
    '''
    Correlates the event (given by the error) to other events that occured
    in a given time frame. For every recognized event in the system that
    needs to be correlated atleast one optional workflow has to exist
    for correlation to make sense.
    Sends an event to the salt event bus, once correlation has determined
    which workflow needs to be executed.
    Should be executed asynchronous, since the method will block for
    MAX_AGE time.
    :param yang_message: passed through for the workflow in salt
    :param minion: The host from which the event originated
    :param origin_ip: The hosts IP address
    :param tag: The event tag
    :param message_details: passed through for the workflow in salt
    :param error: The event that is correlated
    :param optional_arg: decides which workflow gets executed.
    eg. 'dead_timer_expired' will execute tshoot.ospf_nbr_down
    :return: None
    '''
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
    current_case = oatsdbhelpers.create_case(error, minion, solution='Case started in napalm-logs correlation client.',
                                    status='solution_deployed')
    interface = oatsdbhelpers.get_interface(error, yang_message)
    root_host = oatsdbhelpers.get_interface_neighbor(minion, interface, case=current_case)
    n_of_required_events = __get_n_of_required_events(error, root_host, yang_message, current_case)
    print ('{0} event detected: Waiting for {1} seconds to gather event data. Required amount of events: {2}'.
           format(error, MAX_AGE, n_of_required_events))
    time.sleep(MAX_AGE)
    if cache[error]['counter'] == n_of_required_events:
        __print_correlation_result(cache[error]['counter'], error, optional_arg)
        salt_event.send_salt_event(yang_message, minion, origin_ip, tag, message_details,
                                   error, optional_arg, case=current_case)
    else:
        optional_arg = __get_optional_arg(error)
        __print_correlation_result(cache[error]['counter'], error, optional_arg)
        salt_event.send_salt_event(yang_message, root_host, origin_ip, tag, message_details,
                                   error, optional_arg, case=current_case)


def __print_correlation_result(counter, error, optional_arg):
    print ('Time passed. {0} event counter is {1}. Sending {0}: '
           '{2} event to salt master'.format(error, counter, optional_arg))


def __get_n_of_required_events(error, host, yang_message, case):
    if error == OSPF_NEIGHBOR_DOWN:
        return len(oatsdbhelpers.get_ospf_neighbors(host, case=case))
    return 0


def __get_optional_arg(error):
    '''
    Returns an optional arg for the non primary workflow
    of an event.
    Needs to be extended for every new event that is used
    by the system.
    :param error: The event for which to return an optional_arg
    :return: the optional argument (str) or an empty string
    '''
    if error == OSPF_NEIGHBOR_DOWN:
        # TODO: temporarily disabled
        return 'interface_down/disabled'
    return ''