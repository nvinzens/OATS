#!/usr/bin/env python

import salt.client
import json


def send_salt_event(event_msg):
    caller = salt.client.Caller()
    origin_ip = event_msg['ip']
    tag = event_msg['message_details']['tag']
    error = event_msg['error']

    caller.sminion.functions['event.send'](
      'napalm/syslog/*/INTERFACE_DOWN/*',
      {'origin_ip': origin_ip,
        'tag': tag,
        'error': error
       }
    )