#!/usr/bin/env python
from __future__ import with_statement
import salt.utils.event
import salt.client




def send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, case=None):
    '''
    Sends all the given data to the salt event bus.
    The data is used by different workflows in the salt system.
    :param yang_message: data for the workflow
    :param minion: the host from which the event originated
    :param origin_ip: the hosts IP address
    :param tag: the event tag
    :param message_details: more data
    :param error: the event
    :param optional_arg: directly used in the final event-tag. decides which workflow is triggered
    :param case: the optional oatsdb case-id
    :return: None
    '''
    caller = salt.client.Caller()
    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg,
            {'minion': minion,
            'origin_ip': origin_ip,
            'yang_message': yang_message,
            'tag': tag,
             'error': error,
             'message_details': message_details,
             'case': case
             }
        )