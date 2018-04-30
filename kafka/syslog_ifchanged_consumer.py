from kafka import KafkaConsumer
from helpers import salt_event
import json

def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''

consumer = KafkaConsumer('INTERFACE_CHANGED')

for msg in consumer:
    event_msg = json.loads(msg.value)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    timestamp = event_msg['timestamp']
    severity = event_msg['severity']

    error = event_msg['error']
    opt_arg = __get_interface_status(yang_mess)
    event_name = 'napalm/syslog/*/' + error + '/' + opt_arg

    salt_event.send_salt_event(data=event_msg, host=host, timestamp=timestamp,
                               type='syslog', event_name=event_name, severity=severity)




