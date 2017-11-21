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
    optional_arg = ''
    optional_arg = __get_optional_arg(event_msg, error)

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
        interface = event_msg['yang_message']['interfaces']['interface']
        return event_msg['yang_message']['interfaces']['interface'][interface]['state']['oper_status']
    return ''
