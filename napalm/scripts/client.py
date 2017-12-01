#!/usr/bin/env python
import zmq
import napalm_logs.utils
import salt.utils.event
import salt.client
import collections
from expiringdict import ExpiringDict
import time
from threading import Thread


# CONSTANTS:
INTERFACE_CHANGED = 'INTERFACE_CHANGED'
OSPF_NEIGHBOR_DOWN = 'OSPF_NEIGHBOR_DOWN'
YANG_MESSAGE = 'yang_message'
ERROR = 'error'
CACHE_SIZE = 1000
MAX_AGE = 11

# cache for not sending the same event multiple times
# event correlation only looks if in the last MAX_AGE seconds the same event occured
# and if it did, skips it
# can be refined, but needs to get data from the database for that
cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE)


def __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg):
    global cache
    caller = salt.client.Caller()

    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
        { 'minion': minion,
            'origin_ip': origin_ip,
            YANG_MESSAGE: yang_message,
            'tag': tag,
            ERROR: error,
            'message_details': message_details
          }
    )




def __get_optional_arg(event_msg, error):
    yang_message = event_msg[YANG_MESSAGE]
    if error == INTERFACE_CHANGED:
        return __get_interface_status(yang_message)
    if error == OSPF_NEIGHBOR_DOWN:
        return __get_ospf_change_reason(yang_message)
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
    global cache
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v['adjacency-state-change-reason-message'] == 'Dead timer expired':
                return 'dead_timer_expired'
            return ''
        if v:
            return __get_ospf_change_reason(v)
        else:
            return ''


def __send_salt_async(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, first):
    global cache
    # TODO: get OSPF neighbors
    if first:
        cache[OSPF_NEIGHBOR_DOWN] = {}
        cache[OSPF_NEIGHBOR_DOWN]['counter'] = 1
        timeout = time.time() + MAX_AGE - 1 # -1 to avoid exceptions
        while time.time() < timeout:
            continue
        if cache[OSPF_NEIGHBOR_DOWN]['counter'] > 1:
            print cache[OSPF_NEIGHBOR_DOWN]['counter']
            __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg)

    else:
        cache[OSPF_NEIGHBOR_DOWN]['counter'] += 1



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
    print event_msg
    yang_mess = event_msg[YANG_MESSAGE]
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg[ERROR]
    opt_arg = __get_optional_arg(event_msg, event_error)
    if event_error == OSPF_NEIGHBOR_DOWN and opt_arg == 'dead_timer_expired':
        if  not cache:
            print 'First dead_timer_expired Event detected: Start collecting Event.'
            thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
                                                            message, event_error, opt_arg, True))
            thread.daemon = True
            thread.start()
        else:
            print 'Additional dead_timer_expired Event detected. Incrementing counter.'
            thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
                                                            message, event_error, opt_arg, False))
            thread.daemon = True
            thread.start()
    if event_msg:
        __send_salt_event(yang_mess, host, ip, event_tag, message, event_error, opt_arg)
    else:
        continue

