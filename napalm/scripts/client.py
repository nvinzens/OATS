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
    yang_message =  event_msg['yang_message']
    minion = event_msg['host']
    origin_ip = event_msg['ip']
    tag = event_msg['message_details']['tag']
    error = event_msg['error']
    optional_arg = __get_optional_arg(event_msg, error)

    #if not (cache.get(error) ==  error and cache.get(optional_arg) == optional_arg):
    print event_msg
    #cache[error] = error
    #cache[optional_arg] = optional_arg

    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
        { 'minion': minion,
            'origin_ip': origin_ip,
            'yang_message': yang_message,
            'tag': tag,
            'error': error
          }
    )


def __get_optional_arg(event_msg, error):
    optional_arg = ''
    if error == INTERFACE_CHANGED:
        yang_message = collections.OrderedDict(event_msg['yang_message'])
        return __get_interface_status(yang_message)
    return {
        INTERFACE_CHANGED: lambda x: __get_interface_status(collections.OrderedDict(event_msg['yang_message'])),
        OSPF_NEIGHBOR_DOWN: lambda  x:
    }[error]


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
