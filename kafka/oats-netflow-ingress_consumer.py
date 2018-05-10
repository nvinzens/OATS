from kafka import KafkaConsumer
from kafka import KafkaProducer
from oats_kafka_helpers import EventProcessor
import json
from threading import Thread

consumer = KafkaConsumer('oats-netflow-ingress')

for msg in consumer:
    netflow_data = json.loads(msg.value)
    host = netflow_data['AgentID']
    timestamp = netflow_data['Header']['UNIXSecs']
    type = 'netflow'
    event_name = 'netflow/*/high_traffic'
    severity = 3

    for list in netflow_data['DataSets']:
        for dict in list:
            if dict['I'] == 1:
                if dict['V'] > 10000:
                    print ("Packets in detected flow: " + str(dict['V']))
                    # delay the flow for a bit to make sure it arrives later than the event it is needed in
                    thread = Thread(target=EventProcessor.process_event,
                                    args=(netflow_data, host, timestamp, 'netflow', event_name, severity),
                                    kwargs={'start_tshoot': True, 'db_write': False, 'delay': 13})
                    thread.daemon = True
                    thread.start()
                    


