from kafka import KafkaConsumer
from helpers import EventProcessor
from helpers import utils

consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    print (msg)
    host, timestamp, data = utils.extract_record_data(msg)
    EventProcessor.process_event(data=data, host=host, timestamp=timestamp)



