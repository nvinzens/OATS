#!/usr/bin/env python
from __future__ import with_statement
import zmq
import napalm_logs.utils
import salt.utils.event
import salt.client
import collections
from expiringdict import ExpiringDict
import time
import threading
from threading import Thread
from oats import oats



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
lock = threading.Lock()


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


def __send_salt_async(yang_message, minion, origin_ip, tag, message_details, error, optional_arg):
    global cache
    # TODO: get OSPF neighbors
    if optional_arg:
        lock.acquire()
        try:
            cache[error] = {}
            cache[error]['counter'] = 1
        finally:
            lock.release()
        print 'Waiting for {0} seconds to gather data.'.format(MAX_AGE)
        time.sleep(MAX_AGE - 1) # -1 to make sure dict is still present
        if cache[error]['counter'] > 1:
            print 'Time passed. OSPF event counter is {0}. Event root cause suspected in OSPF protocol. Sending {1}' \
                  ': {2} event to salt master'.format(cache[error]['counter'], error, optional_arg)
            __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg)
        else:
            print 'Time passed. OSPF event counter is 1. Event root cause suspected in a single INTERFACE_DOWN event. Sending INTERFACE_DOWN' \
                  ' event to salt master'
            __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, 'interface_down')


    else:
        lock.acquire()
        try:
            cache[error]['counter'] += 1
        finally:
            lock.release()



# listener for napalm-logs messages
server_address = '10.20.1.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')
while True:
    global cache
    raw_object = socket.recv()
    event_msg = napalm_logs.utils.unserialize(raw_object)
    yang_mess = event_msg[YANG_MESSAGE]
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg[ERROR]
    handled = False
    # only Events for which an opt_arg can be identified will be sent to the salt master
    opt_arg = __get_optional_arg(event_msg, event_error)

    if event_error == OSPF_NEIGHBOR_DOWN and opt_arg == 'dead_timer_expired':
        handled = True
        if not event_error in cache:
            cache[event_error] = {}
            print 'First dead_timer_expired Event detected: Start collecting Event.'
            thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
                                                            message, event_error, opt_arg))
            thread.daemon = True
            thread.start()
            opt_arg= ''
        else:
            opt_arg = ''
            print 'Additional dead_timer_expired Event detected. Incrementing counter.'
            thread = Thread(target=__send_salt_async, args=(yang_mess, host, ip, event_tag,
                                                            message, event_error, opt_arg))
            thread.daemon = True
            thread.start()
    if opt_arg:
        handled = True
        __send_salt_event(yang_mess, host, ip, event_tag, message, event_error, opt_arg)
    if not handled:
        print 'Got {0} Event: Not marked for troubleshooting, discarding.'.format(event_error)

