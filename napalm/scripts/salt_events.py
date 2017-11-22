#!/usr/bin/env python

import salt.client
import collections
from expiringdict import ExpiringDict

# cache for not sending the same event multiple times
cache = ExpiringDict(max_len=10, max_age_seconds=10)

def send_salt_event(event_msg):
    caller = salt.client.Caller()
    yang_message =  event_msg['yang_message']
    minion = event_msg['host']
    origin_ip = event_msg['ip']
    tag = event_msg['message_details']['tag']
    error = event_msg['error']
    optional_arg = __get_optional_arg(event_msg, error)

    if not (cache.contains(error) and cache.contains(optional_arg)):
        cache['error'] = error
        cache['optional_arg'] = error

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
    if error == 'INTERFACE_CHANGED':
        yang_message = collections.OrderedDict(event_msg['yang_message'])
        return __get_interface_status(yang_message)
    return ''

def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''
