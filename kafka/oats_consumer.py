from kafka import KafkaConsumer

consumer = KafkaConsumer('oats')
for msg in consumer:
    print (msg)

