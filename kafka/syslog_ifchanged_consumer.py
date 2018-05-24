from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
from oats_kafka_helpers import oats_correlate
from threading import Thread
import json
import logging

def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''


logger = logging.getLogger('oats')

topic = 'INTERFACE_CHANGED'
consumer = KafkaConsumer(topic)
logger.info('Starting Kafka consumer for topic [{0}]...'.format(topic))

for msg in consumer:
    logger.debug('Got an event from [{0}]. Marked for Correlation...'.format(topic))

    event_msg = json.loads(msg.value)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    timestamp = event_msg['timestamp']
    severity = event_msg['severity']

    error = event_msg['error']
    opt_arg = __get_interface_status(yang_mess)
    event_name = 'syslog/*/' + error + '/' + opt_arg

    port_flapping_events = { 'syslog/*/INTERFACE_CHANGED/down': 2, 'syslog/*/INTERFACE_CHANGED/up': 2}

    thread = Thread(target=oats_correlate.aggregate_distinct,
                    args=(event_msg, host, timestamp, severity, error, 'syslog', event_name,
                          port_flapping_events, 'syslog/*/INTERFACE_CHANGED/port_flap', 10, True))
    thread.daemon = True
    thread.start()

    #EventProcessor.process_event(data=event_msg, host=host, timestamp=timestamp,
    #                             sensor_type='syslog', event_name=event_name, severity=severity)




