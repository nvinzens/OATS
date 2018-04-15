from kafka import KafkaConsumer
from salt_event import send_salt_event

def __extract_data(message):
    host = None
    timestamp = None
    data = None
    for key, value in message._asdict().items():
        if key == 'key':
            host = value
        elif key == 'timestamp':
            timestamp = value
        elif key == 'value':
            data = value
    return host, timestamp, data

consumer = KafkaConsumer('out-discards-events')

for msg in consumer:
    print msg
    host, timestamp, data = __extract_data(msg)
    send_salt_event(data, host, timestamp)



