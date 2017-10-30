#!/usr/bin/env python
import zmq
import napalm_logs.utils
import salt.utils.event
from salt_events import send_ifdown_event

server_address = '192.168.50.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')
while True:
  raw_object = socket.recv()
  print(napalm_logs.utils.unserialize(raw_object))
  if "Interface GigabitEthernet2, changed state to administratively down" in raw_object:
      print("INTERFACE STATUS CHANGED")
      send_ifdown_event('router1', 'GigabitEthernet2')
  #else:
    #print(napalm_logs.utils.unserialize(raw_object))
