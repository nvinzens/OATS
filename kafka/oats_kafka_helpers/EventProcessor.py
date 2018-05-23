#!/usr/bin/env python
from __future__ import with_statement
from oatsinflux import oatsinflux
import salt.utils.event
import salt.client
import time


def process_event(data, host, timestamp, sensor_type, event_name, severity, case=None,
                  start_tshoot=True, influx_write=True, delay=0):
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
    print ('Sending ' + event_name)
    if start_tshoot:
        if delay:
            time.sleep(delay)
        caller = salt.client.Caller()
        caller.sminion.functions['event.send'](
            event_name,
            {'data': data,
             'host': host,
             'timestamp': timestamp,
             'type': sensor_type,
             'severity': severity,
             'case': case
             }
        )

     # write all events to influx
    if influx_write:
        oatsinflux.write_event(host, timestamp, sensor_type, event_name, severity, data)