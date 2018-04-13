from kafka import KafkaConsumer

consumer = KafkaConsumer('out-discards-events')
for msg in consumer:
    print (msg)

