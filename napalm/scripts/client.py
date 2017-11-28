#!/usr/bin/env python
import zmq
import napalm_logs.utils
import salt.utils.event
import salt.client
import collections
from expiringdict import ExpiringDict


# CONSTANTS:
INTERFACE_CHANGED = 'INTERFACE_CHANGED'
OSPF_NEIGHBOR_DOWN = 'OSPF_NEIGHBOR_DOWN'
OSPF_REASON_MESSAGE = 'adjacency-state-change-reason-message'
YANG_MESSAGE = 'yang_message'
ERROR = 'error'
#CACHE_SIZE = 10
#MAX_AGE = 3

# cache for not sending the same event multiple times
# event correlation only looks if in the last MAX_AGE seconds the same event occured
# and if it did, skips it
# can be refined, but needs to get data from the database for that
#cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE)


def __send_salt_event(event_msg):
    global cache
    caller = salt.client.Caller()
    yang_message =  event_msg[YANG_MESSAGE]
    minion = event_msg['host']
    origin_ip = event_msg['ip']
    tag = event_msg['message_details']['tag']
    error = event_msg[ERROR]
    optional_arg = __get_optional_arg(event_msg, error)

    #if not (cache.get(error) ==  error and cache.get(optional_arg) == optional_arg):
    print event_msg
    #cache[error] = error
    #cache[optional_arg] = optional_arg

    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
        { 'minion': minion,
            'origin_ip': origin_ip,
            YANG_MESSAGE: yang_message,
            'tag': tag,
            ERROR: error
          }
    )


def __get_optional_arg(event_msg, error):
    return {
        INTERFACE_CHANGED: __get_interface_status(collections.OrderedDict(event_msg[YANG_MESSAGE])),
        OSPF_NEIGHBOR_DOWN: __get_ospf_change_reason(collections.OrderedDict(event_msg[YANG_MESSAGE]))
    }.get(error, '')



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
        if k == OSPF_REASON_MESSAGE:
            if k[OSPF_REASON_MESSAGE] == 'Dead timer expired':
                return 'dead_timer_expired'
            return ''
        if v:
            return __get_ospf_change_reason(v)
        else:
            return ''

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
    msg = napalm_logs.utils.unserialize(raw_object)
    __send_salt_event(msg)
