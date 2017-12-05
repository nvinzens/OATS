#!/usr/bin/env python
from __future__ import with_statement
from oats import oats
import zmq
import napalm_logs.utils
import salt.utils.event
import salt.client
import collections
from expiringdict import ExpiringDict
import time
import threading
from threading import Thread
import correlate
import salt_event




# CONSTANTS:
#no cache needed?
CACHE_SIZE = 1000
MAX_AGE = 10

# cache for not sending the same event multiple times
# event correlation only looks if in the last MAX_AGE seconds the same event occured
# and if it did, skips it
# can be refined, but needs to get data from the database for that
cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE+3) # +3 to give the function more time to evaluate dict


def __get_optional_arg(msg, error):
    yang_message = msg['yang_message']
    if error == correlate.INTERFACE_CHANGED:
        return __get_interface_status(yang_message)
    if error == correlate.OSPF_NEIGHBOR_DOWN:
        return __get_ospf_change_reason(yang_message)
    if error == correlate.OSPF_NEIGHBOR_UP:
        return 'ospf_nbr_up'
    else:
        return ''


def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''


def __get_ospf_change_reason(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v['adjacency-state-change-reason-message'] == 'Dead timer expired':
                return 'dead_timer_expired'
            return ''
        if v:
            return __get_ospf_change_reason(v)
        else:
            return ''


# def __send_salt_async(yang_message, minion, origin_ip, tag, message_details, error, optional_arg):
#     global cache
#     # first thread populates dict
#     lock.acquire()
#     if not cache[error]:
#         cache[error] = {}
#         cache[error]['counter'] = 1
#     # later threads increment counter
#     else:
#         cache[error]['counter'] += 1
#     # TODO: get OSPF neighbors
#     lock.release()
#     if optional_arg:
#         current_case = oats.create_case(error, minion, status='solution_deployed')
#         # make sure cache gets initialized before other threads try to access it)
#         interface = oats.get_interface(error, yang_message)
#         root_host = oats.get_interface_neighbor(minion, interface, case=current_case)
#         n_of_neighbors = len(oats.get_ospf_neighbors(root_host, case=current_case))
#         print 'Waiting for {0} seconds to gather data.'.format(MAX_AGE)
#         time.sleep(MAX_AGE) # -1 to make sure dict is still present
#         if cache[error]['counter'] == n_of_neighbors:
#             print 'Time passed. OSPF event counter is {0}. Event root cause suspected in OSPF protocol. Sending {1}' \
#                   ': {2} event to salt master'.format(cache[error]['counter'], error, optional_arg)
#             __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, case=current_case)
#         else:
#             print 'Time passed. OSPF event counter is {0}. Event root cause suspected in a single INTERFACE_DOWN event. Sending INTERFACE_DOWN' \
#                   ' event to salt master'.format(cache[error]['counter'])
#             __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, 'interface_down', case=current_case)



# listener for napalm-logs messages
server_address = '10.20.1.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')
while True:
    raw_object = socket.recv()
    event_msg = napalm_logs.utils.unserialize(raw_object)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']
    handled = False
    # only Events for which an opt_arg can be identified will be sent to the salt master
    opt_arg = __get_optional_arg(event_msg, event_error)
    if event_error in correlate.CORRELATE_EVENTS and opt_arg == correlate.EVENT_OPTIONAL_ARGS[event_error]:
        handled = True
        thread = Thread(target=correlate.correlate, args=(yang_mess, host, ip, event_tag, message, event_error, opt_arg))
        thread.daemon = True
        thread.start()
        opt_arg = ''  # marks the event as processed
        # if not event_error in cache:
        #     cache[event_error] = {}
        #     print 'First dead_timer_expired Event detected: Start collecting Event.'
        #     thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
        #                                                     message, event_error, opt_arg))
        #     thread.daemon = True
        #     thread.start()
        #     opt_arg= ''
        # else:
        #     opt_arg = ''
        #     print 'Additional dead_timer_expired Event detected. Incrementing counter.'
        #     thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
        #                                                     message, event_error, opt_arg))
        #     thread.daemon = True
        #     thread.start()
    if opt_arg:
        handled = True
        print ('Got {0}: {1} Event: Sending to salt master.'.format(event_error, opt_arg))
        salt_event.send_salt_event(yang_mess, host, ip, event_tag, message, event_error, opt_arg)
    if not handled:
        print ('Got {0} Event: Not marked for troubleshooting, discarding.'.format(event_error))

