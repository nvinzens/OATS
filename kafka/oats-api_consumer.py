from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
import json

consumer = KafkaConsumer('oats-api')
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
    api_msg = json.loads(msg.value)
    sensor_type = api_msg['type']
    event_name = api_msg['event_name']
    host = api_msg['host']
    timestamp = api_msg['timestamp']
    severity = api_msg['severity']
    data = api_msg['data']

    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 sensor_type=sensor_type, event_name=event_name, severity=severity)