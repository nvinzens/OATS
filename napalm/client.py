#!/usr/bin/env python
import zmq
import napalm_logs.utils

server_address = '192.168.50.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')
while True:
  raw_object = socket.recv()
  if "Interface GigabitEthernet" in raw_object:
      print("INTERFACE STATUS CHANGED")
  else:
    print(napalm_logs.utils.unserialize(raw_object))
