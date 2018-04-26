from kafka import KafkaConsumer

consumer = KafkaConsumer("oats", bootstrap_servers='localhost:9092', auto_offset_reset='earliest')
for msg in consumer:
    print (msg)

