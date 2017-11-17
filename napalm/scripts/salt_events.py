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

    caller.sminion.functions['event.send'](
      'napalm/syslog/*/INTERFACE_DOWN/*',
      { 'minion': minion,
        'origin_ip': origin_ip,
        'yang_message': yang_message,
        'tag': tag,
        'error': error
       }
    )