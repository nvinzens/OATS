from kafka import KafkaConsumer

consumer = KafkaConsumer('streams-pipe-output')
for msg in consumer:
    print (msg)

