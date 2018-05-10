from kafka import KafkaConsumer
import json
from oats import oatsdbhelpers
from threading import Thread
from oats_kafka_helpers import oats_correlate
from oats_kafka_helpers import utils


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
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    timestamp = event_msg['timestamp']
    severity = event_msg['severity']
    event_error = event_msg['error']
    salt_id = __get_ospf_change_reason(yang_mess)

    # only start aggregation once the dead timer is expired
    if salt_id == 'dead_timer_expired':
        event_name = 'syslog/*/' + event_error + salt_id
        alt_event_name = 'syslog/*/' + event_error + 'interface_down'
        n_of_required_events, root_host = utils.get_n_of_events_and_root_host(event_error, host, yang_mess)

        thread = Thread(target=oats_correlate.aggregate,
                        args=(event_msg, host, timestamp, severity, event_error, 'syslog', event_name,
                              n_of_required_events, alt_event_name, 10, True))
        thread.daemon = True
        thread.start()



