from kafka import KafkaConsumer
from oats import oatsdbhelpers
from helpers import salt_event
from threading import Thread
from helpers import correlate
from helpers import utils
import json

def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''

consumer = KafkaConsumer('OSPF_NEIGHBOR_UP')

for msg in consumer:
    event_msg = json.loads(msg.value)
    print (event_msg)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']
    salt_id = 'ospf_nbrs_up'

    current_case = oatsdbhelpers.create_case(event_error, host, solution='Case started in kafka event consumer.')
    n_of_required_events = utils.get_n_of_events(event_error, host, yang_mess, current_case=current_case)

    thread = Thread(target=correlate.aggregate,
                    args=(yang_mess, host, ip, event_tag, message, event_error, salt_id,
                          n_of_required_events+3, "no event", 10, current_case))
    thread.daemon = True
    thread.start()




