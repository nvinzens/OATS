from kafka import KafkaConsumer
from helpers import salt_event
from helpers import utils

consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    print (msg)
    host, timestamp, data = utils.extract_record_data(msg)
    salt_event.send_salt_event(data=data, host=host, timestamp=timestamp)



