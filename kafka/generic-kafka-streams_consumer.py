from kafka import KafkaConsumer
import argparse
from oats_kafka_helpers import EventProcessor
from oats_kafka_helpers import utils
from oatsinflux import oatsinflux
from threading import Thread
import oats_kafka_helpers


def consume_kafka(topic, event_name, correlation_function=None, correlation_time=None):
    consumer = KafkaConsumer(topic)
    print ("Started kafka consumer for topic {0} and event_name {1}".format(topic, event_name))
    for msg in consumer:
        print (msg)
        host, timestamp, data = utils.extract_record_data(msg)
        sensor_type = 'streaming-telemetry'
        if correlation_function is None:
            severity = 5
            EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                         type=sensor_type,
                                         event_name=event_name,
                                         severity=severity)
        else:
            severity = 3
            oatsinflux.write_event(host, timestamp, type, event_name, severity, data)
            # load correlation function by name
            func = getattr(oats_kafka_helpers, correlation_function)
            thread = Thread(target=func,
                            args=(data, host, timestamp, severity, 'KAFKA_STREAMS_EVENT', sensor_type, event_name),
                            kwargs={'correlate_for': correlation_time, 'use_oats_case': True})
            thread.daemon = True
            thread.start()


if __name__ == '__main__':
    # TODO: add option for correlation
    parser = argparse.ArgumentParser(description='Start OATS kafka event consumer')
    parser.add_argument('-t', '--topic', help='the kafka topic you want to consume from', required=True)
    parser.add_argument('-e', '--event_name', help='the event name used by oats', required=True)
    parser.add_argument('-cf', '--correlation-function',
                        help='optional: the function to use for correlating', required=False)
    parser.add_argument('-ct', '--correlation-time', type=int,
                        help='optional: the amount of time to correlate for', required=False)
    args = vars(parser.parse_args())
    consume_kafka(args['topic'], args['event_name'],
                  correlation_function=args['correlation_function'], correlation_time=args['correlation_time'])

