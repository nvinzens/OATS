#!/usr/bin/env python
from __future__ import with_statement
import salt.utils.event
import salt.client


def send_salt_event(data, host, timestamp, type, event_name, severity, case=None):
    '''
    Sends all the given data to the salt event bus.
    The data is used by different workflows in the salt system.
    :param data: data for the workflow
    :param host: the host from which the event originated
    :param origin_ip: the hosts IP address
    :param tag: the event tag
    :param message_details: more data
    :param error: the event
    :param opt_arg: directly used in the final event-tag. decides which workflow is triggered
    :param case: the optional oatsdb case-id
    :return: None
    '''
    caller = salt.client.Caller()
    caller.sminion.functions['event.send'](
        event_name,
        {'data': data,
         'host': host,
         'timestamp': timestamp,
         'type': type,
         'severity': severity,
         'case': case
         }
    )