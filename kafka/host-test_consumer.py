from kafka import KafkaConsumer

consumer = KafkaConsumer('host-test')
for msg in consumer:
    print (msg)

