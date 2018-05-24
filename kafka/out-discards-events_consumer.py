from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
from oats_kafka_helpers import utils
from threading import Thread
from oats_kafka_helpers import oats_correlate


consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    host, timestamp, data = utils.extract_record_data(msg)
    thread = Thread(target=oats_correlate.compress,
                    args=(data, host, timestamp, 2, "OUT_DISCARDS_EXCEEDED", 'syslog', "out_discard_event",
                          10, True))
    thread.daemon = True
    thread.start()



