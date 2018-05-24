from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
import json
import logging

logger = logging.getLogger('oats')

topic = 'oats-api'
consumer = KafkaConsumer(topic)
logger.info('Starting Kafka consumer for topic [{0}]...'.format(topic))
'''
event = {
        'type': request.json.get('type', 'default_API'),
        'event_name': 'API/' + request.json.get('event_name', 'default_event'),
        'host': request.json.get('host', 'no host provided'),
        'timestamp': request.json.get('timestamp', datetime.datetime.utcnow()),
        'severity': request.json.get('severity', 7),
        'data': request.json.get('payload', {'data': 'no data provided'})
    }
'''

for msg in consumer:
    logger.debug('Got an event from [{0}]. Sending to influx...'.format(topic))
    api_msg = json.loads(msg.value)
    sensor_type = api_msg['type']
    event_name = api_msg['event_name']
    host = api_msg['host']
    timestamp = api_msg['timestamp']
    severity = api_msg['severity']
    data = api_msg['data']

    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 sensor_type=sensor_type, event_name=event_name, severity=severity,
                                 start_tshoot=False)