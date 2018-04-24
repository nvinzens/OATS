from kafka import KafkaConsumer
import json
from oats import oatsdbhelpers
from threading import Thread
from helpers import correlate


def __get_n_of_events(error, yang_message, current_case=None):
    interface = oatsdbhelpers.get_interface(event_error, yang_mess)
    root_host = oatsdbhelpers.get_interface_neighbor(host, interface, case=current_case)
    return len(oatsdbhelpers.get_ospf_neighbors(host, case=current_case))

consumer = KafkaConsumer('OSPF_NEIGHBOR_DOWN')

for msg in consumer:
    event_msg = json.loads(msg.value)
    print (event_msg)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']

    current_case = oatsdbhelpers.create_case(event_error, host, solution='Case started in kafka event consumer.')

    n_of_required_events = __get_n_of_events(event_error, yang_mess, current_case=current_case)

    thread = Thread(target=correlate.aggregate,
                    args=(yang_mess, host, ip, event_tag, message, event_error, "dead_timer_expired",
                          n_of_required_events, "interface_down", 10, current_case))
    thread.daemon = True
    thread.start()



