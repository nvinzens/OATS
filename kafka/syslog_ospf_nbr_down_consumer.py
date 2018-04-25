from kafka import KafkaConsumer
import json
from oats import oatsdbhelpers
from threading import Thread
from helpers import correlate
from helpers import utils


def __get_ospf_change_reason(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v['adjacency-state-change-reason-message'] == 'Dead timer expired':
                return 'dead_timer_expired'
            return ''
        if v:
            return __get_ospf_change_reason(v)
        else:
            return ''

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
    salt_id = __get_ospf_change_reason(yang_mess)

    if salt_id == "dead_timer_expired":
        current_case = oatsdbhelpers.create_case(event_error, host, solution='Case started in kafka event consumer.')
        n_of_required_events, root_host = utils.get_n_of_events_and_root_host(event_error, host, yang_mess, current_case=current_case)

        thread = Thread(target=correlate.aggregate,
                        args=(yang_mess, host, ip, event_tag, message, event_error, salt_id,
                              n_of_required_events, "interface_down", 10, current_case))
        thread.daemon = True
        thread.start()



