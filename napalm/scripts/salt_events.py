#!/usr/bin/env python

import salt.client
import collections


def send_salt_event(event_msg):
    caller = salt.client.Caller()
    yang_message =  event_msg['yang_message']
    minion = event_msg['host']
    origin_ip = event_msg['ip']
    tag = event_msg['message_details']['tag']
    error = event_msg['error']
    optional_arg = __get_optional_arg(event_msg, error)
    print(optional_arg)

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
        dict = collections.OrderedDict(event_msg)
        return __get_interface_status(dict)
    return ''

def __get_interface_status(dict):
    amount = sum(len(v) for v in dict.itervalues())
    key = dict.popitem()[0]
    if key == 'oper_status':
        return dict[key]
    if amount == 1:
        return ''
    else:
        __get_interface_status(dict)
