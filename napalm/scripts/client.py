#!/usr/bin/env python
import zmq
import napalm_logs.utils
import salt.utils.event
from salt_events import send_salt_event

server_address = '10.20.1.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')
while True:
  raw_object = socket.recv()
  msg = napalm_logs.utils.unserialize(raw_object)
  print (msg)
  send_salt_event(msg)
  #else:
    #print(napalm_logs.utils.unserialize(raw_object))
