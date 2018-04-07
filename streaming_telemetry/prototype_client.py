from ncclient import manager
from lxml import etree
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
import argparse

#XPATH = "/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory"
XPATH = "/bgp-ios-xe-oper:bgp-state-data/neighbors/neighbor/prefix-activity"
#XPATH = "/bgp-ios-xe-oper:bgp-state-data/prefixes/entry-stats/total-entries"
#XPATH = "/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry/stats/jitter/sd/avg"
TOPIC = 'oats'


def errback(notif):
    pass


def debug_callback(notif):
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    print (etree.tostring(notif.datastore_ele, pretty_print=True).decode('utf-8'))
    print (jsonString)

def callback_kafka_publish(notif):
    # Publishes message to Kafka messaging bus
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)

    #producer.send(TOPIC, jsonString)
    #print (etree.tostring(notif.datastore_ele, pretty_print=True).decode('utf-8'))
    print (jsonString)


if __name__ == '__main__':

    m = manager.connect(host='10.20.1.21',
                        port=830,
                        username='ins',
                        password='ins@lab',
                        allow_agent=False,
                        look_for_keys=False,
                        hostkey_verify=False,
                        unknown_host_cb=True,
                        timeout=25
                        )

    #producer = KafkaProducer(bootstrap_servers='localhost:9092')
    sub = ''
    while True:
        if not sub:
            if 'producer' in locals():
                print ("kafka enabled")
                sub = m.establish_subscription(callback_kafka_publish, errback, xpath=XPATH, period=1000)
            else:
                print ("debug")
                sub = m.establish_subscription(debug_callback, errback, xpath=XPATH, period=1000)
            print (sub.subscription_result)
        time.sleep(9.8)



