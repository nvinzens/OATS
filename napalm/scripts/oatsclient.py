#!/usr/bin/env python
from __future__ import with_statement
import zmq
import napalm_logs.utils
from threading import Thread
import clienthelpers
import aggregate
import salt_event


# listener for napalm-logs messages
server_address = '10.20.1.10'
server_port = 49017
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                          port=server_port))
socket.setsockopt(zmq.SUBSCRIBE,'')

# extracts all the relevant bits of data from a napalm-logs message
# and sends it to the salt event bus (after correlating events, if
# needed).
while True:
    raw_object = socket.recv()
    event_msg = napalm_logs.utils.unserialize(raw_object)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']
    handled = False
    # only Events for which an opt_arg can be identified will be sent to the salt master
    opt_arg = clienthelpers.get_optional_arg(event_msg, event_error)
    if event_error in aggregate.AGGREGATE_EVENTS and opt_arg == aggregate.EVENT_OPTIONAL_ARGS[event_error]:
        handled = True
        thread = Thread(target=aggregate.aggregate, args=(yang_mess, host, ip, event_tag, message, event_error, opt_arg))
        thread.daemon = True
        thread.start()
        opt_arg = ''  # marks the event as processed
    if opt_arg:
        handled = True
        print ('Got {0}:{1} Event: Sending to salt master.'.format(event_error, opt_arg))
        salt_event.send_salt_event(yang_mess, host, ip, event_tag, message, event_error, opt_arg)
    if not handled:
        print ('Got {0} Event: Not marked for troubleshooting, discarding.'.format(event_error))

