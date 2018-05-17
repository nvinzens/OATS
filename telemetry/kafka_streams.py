import subprocess
from multiprocessing import Process


def start_kafka_streams(subscription):
    kstreams_process = Process(target=subprocess.call,
                               args=([
                                            'java', '-jar', subscription.jar_location,
                                            subscription.kafka_publish_topic,
                                            subscription.kafka_event_topic, str(subscription.event_threshold),
                                            subscription.operator,
                                            subscription.root_xpath, subscription.name_xpath, subscription.data_xpath
                                    ],))
    kstreams_process.start()

    if subscription.correlate_event:
        kconsumer_process = Process(target=subprocess.call, args=(['python',
                                                                   '/home/OATS/kafka/generic-kafka-streams_consumer.py',
                                                                   '-t', subscription.kafka_event_topic,
                                                                   '-e', subscription.event,
                                                                   '-cf', subscription.correlate_function,
                                                                   '-ct', str(subscription.correlate_for)],))
    else:
        kconsumer_process = Process(target=subprocess.call, args=(['python',
                                                                   '/home/OATS/kafka/generic-kafka-streams_consumer.py',
                                                                   '-t', subscription.kafka_event_topic,
                                                                   '-e', subscription.event],))
    kconsumer_process.start()