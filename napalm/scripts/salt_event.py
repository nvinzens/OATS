#!/usr/bin/env python
from __future__ import with_statement
import salt.utils.event
import salt.client




def send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, case=None):
    caller = salt.client.Caller()
    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
            {'minion': minion,
            'origin_ip': origin_ip,
            'yang_message': yang_message,
            'tag': tag,
             'error': error,
             'message_details': message_details,
             'case': case
             }
        )