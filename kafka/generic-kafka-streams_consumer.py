from kafka import KafkaConsumer
import argparse
from helpers import EventProcessor
from helpers import utils



def consume_kafka(topic, event_name):
    consumer = KafkaConsumer(topic)
    print ("Started kafka consumer for topic {0} and event_name {1}".format(topic, event_name))
    for msg in consumer:
        print (msg)
        host, timestamp, data = utils.extract_record_data(msg)
        EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                     type='streaming-telemetry',
                                     event_name=event_name,
                                     severity=4)


if __name__ == '__main__':
    # TODO: add option for correlation
    parser = argparse.ArgumentParser(description='Start OATS kafka event consumer')
    parser.add_argument('-t', '--topic', help='the kafka topic you want to consume from', required=True)
    parser.add_argument('-e', '--event_name', help='the event name used by oats', required=True)
    args = vars(parser.parse_args())
    consume_kafka(args['topic'], args['event_name'])

