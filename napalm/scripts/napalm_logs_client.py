#!/usr/bin/env python
from __future__ import with_statement
import zmq
import napalm_logs.utils
import json




from kafka import KafkaProducer


# listener for napalm-logs messages
server_address = '10.20.1.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')

producer = KafkaProducer(bootstrap_servers='localhost:9092')

# extracts all the relevant bits of data from a napalm-logs message
# and sends it to the salt event bus (after correlating events, if
# needed).
while True:
    raw_object = socket.recv()
    event_msg = napalm_logs.utils.unserialize(raw_object)
    yang_mess = event_msg['yang_message']
    topic = event_msg['error']
    producer.send(topic, json.dumps(yang_mess))
