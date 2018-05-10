from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
from oats_kafka_helpers import utils
from threading import Thread
from oats_kafka_helpers import oats_correlate


consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    host, timestamp, data = utils.extract_record_data(msg)
    '''
    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 type='streaming-telemetry',
                                 event_name='streaming-telemetry/*/out-discard-event',
                                 severity=4)
    '''

    thread = Thread(target=oats_correlate.compress,
                    args=(data, host, timestamp, 6, "OUT_DISCARDS_EXCEEDED", 'syslog', "out_discard_event",
                          10, True))
    thread.daemon = True
    thread.start()



