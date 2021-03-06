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
    relevant_data = []
    big_flow = False
    for list in netflow_data['DataSets']:
        list = sorted(list)
        for dict in list:
            if dict['I'] == 1:
                if dict['V'] > 10000:
                    big_flow = True
                    print ("Packets in detected flow: " + str(dict['V']))
            if big_flow:
                if dict['I'] == 7:
                    if dict['V'] > 10000:
                        print ("Source port of flow: " + dict['V'])

                        # delay the flow for a bit to make sure it arrives later than the event it is needed in
                        thread = Thread(target=EventProcessor.process_event,
                                        args=(netflow_data, host, timestamp, 'netflow', event_name, severity),
                                        kwargs={'start_tshoot': True, 'db_write': False, 'delay': 5})
                        thread.daemon = True
                        thread.start()
                        break

                else:
                    continue
                    


