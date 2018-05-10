from kafka import KafkaConsumer
from oats_kafka_helpers import EventProcessor
from threading import Thread
from oats_kafka_helpers import oats_correlate
from oats_kafka_helpers import utils
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
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    timestamp = event_msg['timestamp']
    severity = event_msg['severity']
    event_error = event_msg['error']
    event_name = 'syslog/*/' + event_error + 'ospf_nbrs_up'
    n_of_required_events, root_host = utils.get_n_of_events_and_root_host(event_error, host, yang_mess)

    #start aggregation of event
    thread = Thread(target=oats_correlate.aggregate,
                    args=(event_msg, host, timestamp, severity, event_error, 'syslog', event_name,
                          n_of_required_events+3, 'syslog/*/OSPF_NEIGHBOR_UP/no event', 10, False))
    thread.daemon = True
    thread.start()




