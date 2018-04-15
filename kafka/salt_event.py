#!/usr/bin/env python
from __future__ import with_statement
import salt.utils.event
import salt.client


def send_salt_event(data, host, timestamp):
    '''
    Sends all the given data to the salt event bus.
    The data is used by different workflows in the salt system.
    '''
    caller = salt.client.Caller()
    caller.sminion.functions['event.send'](
        'kafka/streaming-telemetry/*/out-discard-event/',
            {'data': data,
            'host': host,
             'timestamp': timestamp
             }
        )