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
from oatssalthelpers import oats


def __send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, case=None):
    global cache
    caller = salt.client.Caller()
    print 'Sending Event {0} to salt event bus. Optional_arg: {1}'.format(error, optional_arg)
    if case:
        caller.sminion.functions['event.send'](
            'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
            { 'minion': minion,
                'origin_ip': origin_ip,
                'yang_message': yang_message,
                'tag': tag,
                'error': error,
                'message_details': message_details,
                'case': case
          })
    else:
        caller.sminion.functions['event.send'](
            'napalm/syslog/*/' + error + '/' + optional_arg + '/*',
            {'minion': minion,
             'origin_ip': origin_ip,
             'yang_message': yang_message,
             'tag': tag,
             'error': error,
             'message_details': message_details
             })