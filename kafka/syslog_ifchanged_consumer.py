from kafka import KafkaConsumer
from salt_event import send_salt_event

consumer = KafkaConsumer('INTERFACE_CHANGED')

for msg in consumer:
    print (msg)
    #host, timestamp, data = __extract_data(msg)
    #send_salt_event(data, host, timestamp)



