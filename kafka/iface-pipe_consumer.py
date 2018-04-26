from kafka import KafkaConsumer

consumer = KafkaConsumer('iface-pipe')
for msg in consumer:
    print (msg)

