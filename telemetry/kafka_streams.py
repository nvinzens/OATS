import subprocess
from multiprocessing import Process
import logging

logger = logging.getLogger('oats.main')


def start_kafka_streams(subscription):
    logger.info('Start kafka streams proccess for consuming from kafka topic {0} and producing to {1}.'
                .format(subscription.kafka_publish_topic, subscription.kafka_event_topic))
    try:
        kstreams_process = Process(target=subprocess.call,
                                   args=([
                                                'java', '-jar', subscription.jar_location,
                                                subscription.kafka_publish_topic,
                                                subscription.kafka_event_topic, str(subscription.event_threshold),
                                                subscription.operator,
                                                subscription.root_xpath, subscription.name_xpath, subscription.data_xpath
                                        ],))
        kstreams_process.start()
    except Exception:
        logger.exception("Exception while trying to start kafka streams process."
                         " There may be an error in the configuration file.")

    if subscription.correlate_event:
        logger.info('Starting kafka consumer process for consuming from topic {0} and using correlate function {1}.'
                    .format(subscription.kafka_event_topic, subscription.correlate_function))
        kconsumer_process = Process(target=subprocess.call, args=(['python',
                                                                   '/home/OATS/kafka/generic-kafka-streams_consumer.py',
                                                                   '-t', subscription.kafka_event_topic,
                                                                   '-e', subscription.event,
                                                                   '-cf', subscription.correlate_function,
                                                                   '-ct', str(subscription.correlate_for)],))
    else:
        logger.info('Starting kafka consumer process for consuming from topic {0}.'
                    .format(subscription.kafka_event_topic))
        kconsumer_process = Process(target=subprocess.call, args=(['python',
                                                                   '/home/OATS/kafka/generic-kafka-streams_consumer.py',
                                                                   '-t', subscription.kafka_event_topic,
                                                                   '-e', subscription.event],))
    kconsumer_process.start()