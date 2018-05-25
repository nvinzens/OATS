from kafka import KafkaConsumer
from oats_kafka_helpers import utils
from threading import Thread
from oats_kafka_helpers import oats_correlate
import logging
import logging.config
import yaml

log_file = open('/etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.kafka')

topic = 'out-discards-events'
consumer = KafkaConsumer(topic)
logger.info('Starting Kafka consumer for topic [{0}]...'.format(topic))

for msg in consumer:
    logger.debug('Got an event from [{0}]. Marked for Correlation...'.format(topic))

    host, timestamp, data = utils.extract_record_data(msg)
    thread = Thread(target=oats_correlate.compress,
                    args=(data, host, timestamp, 2, "OUT_DISCARDS_EXCEEDED", 'syslog', "out_discard_event",
                          10, True))
    thread.daemon = True
    thread.start()



