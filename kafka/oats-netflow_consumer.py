from kafka import KafkaConsumer

consumer = KafkaConsumer('oats-netflow')
for msg in consumer:
    print (msg)

