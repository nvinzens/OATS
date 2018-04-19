from kafka import KafkaConsumer
from kafka.helpers import salt_event

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
    event_msg = msg['value']
    print (event_msg)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']
    opt_arg = __get_interface_status(yang_message=yang_mess)
    salt_event.send_salt_event(yang_mess, host, ip, event_tag, message, event_error, opt_arg)




