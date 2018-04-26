from kafka import KafkaConsumer

consumer = KafkaConsumer('ip-sla')
for msg in consumer:
    print (msg)

