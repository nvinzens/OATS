from kafka import KafkaConsumer
import json
import msgpack

consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m))
consumer.subscribe(['streams-pipe-output'])

for msg in consumer:
    for key, value in msg._asdict().items():
        print (key)
        print (value)
