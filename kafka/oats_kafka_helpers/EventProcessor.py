#!/usr/bin/env python
from __future__ import with_statement
from oatsinflux import oatsinflux
import salt.utils.event
import salt.client
import logging.config
import yaml

log_file = open('/etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.kafka.helpers')


def process_event(data, host, timestamp, sensor_type, event_name, severity, case=None,
                  start_tshoot=True, influx_write=True):
    '''
    Takes all the given event data and sends it to the salt master if start_tshoot is set.
    Will also write the data to influx if influx_write is set.
    :param data: The data to append to the event. Is different for every sensor type.
    :param host: The host from which the event originates from eg. "10.20.1.21".
    :param timestamp: The timestamp of the event as given by the device.
    :param sensor_type: The sensor which detected the event
        eg. syslog, streaming-telemetry, netflow, oats-api.
    :param event_name: the event name which decides which workflow gets executed in salt.
        Check the salt master configuration for examples.
    :param severity: The severity of the event, ranges from 0-7
        with 0 indicating the worst kind of event (critical).
    :param case: optional, the oats case ID.
    :param start_tshoot: If set the function sends the event to the salt master
    :param influx_write: If set the function sends the event to influx
    :return: None
    '''
    if start_tshoot:
        logger.debug('Sending {0} event to salt master...'.format(event_name))
        caller = salt.client.Caller()
        try:
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
        except Exception:
            logger.debug('Exception while sending event to salt master. Salt master might be down.')


    # write all events to influx
    if influx_write:
        oatsinflux.write_event(host, timestamp, sensor_type, event_name, severity, data)