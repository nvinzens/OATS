#!/usr/bin/env python

import salt.client
import json


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
        __get_interface_status(event_msg)
    return ''

def __get_interface_status(dict):
    return_key = next(iter(dict))
    if return_key == 'oper_status':
        return dict[return_key]
    for key, value in dict:
        if isinstance(value, dict):
           return __get_interface_status(dict)

