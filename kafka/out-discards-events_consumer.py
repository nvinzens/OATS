from kafka import KafkaConsumer
from helpers import EventProcessor
from helpers import utils

consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    host, timestamp, data = utils.extract_record_data(msg)
    EventProcessor.process_event(data=data, host=host, timestamp=timestamp,
                                 type='streaming_telemetry',
                                 event_name='streaming-telemetry/*/out-discard-event',
                                 severity=4)



