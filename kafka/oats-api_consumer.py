from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
import json
import logging
import logging.config
import yaml

'''
Kafka consumer for consuming from the "oats-api" topic.
The topic is meant to be used as an API to oats.
'''

log_file = open('/etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.kafka')

topic = 'oats-api'
consumer = KafkaConsumer(topic)
logger.info('Starting Kafka consumer for topic [{0}]...'.format(topic))


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