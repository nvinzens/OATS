from ncclient import manager
from lxml import etree
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
from SubscriptionConfig import SubscriptionConfig
from multiprocessing import Process, Lock
import collections

#XPATH = "/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry/stats/jitter/sd/avg"
TOPIC = None
YAML_FILE = 'config.yaml'
#PRODUCER = None

def errback(notif):
    pass


def debug_callback(notif):
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    #print (etree.tostring(notif.datastore_ele, pretty_print=True).decode('utf-8'))
    print (jsonString)


def callback_kafka_publish(notif, topic):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    # Publishes message to Kafka messaging bus
    #print (topic)
    print ("")
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2).encode('utf-8') + topic
    #producer.send(topic, jsonString)
    #producer.flush()
    print (jsonString)


def __process_host(host_config):
    subs = config.get_subscriptions(host_config)
    for sub in subs:
        p = Process(target=__create_subscriptions, args=(sub, len(subs)))
        p.start()



def __create_subscriptions(subscription, n_of_subs):
    first = True
    with manager.connect(host=config.get_host(host_config),
                         port=config.get_port(host_config),
                         username=config.get_username(host_config),
                         password=config.get_password(host_config),
                         allow_agent=False,
                         look_for_keys=False,
                         hostkey_verify=False,
                         unknown_host_cb=True,
                         timeout=100
                         ) as m:
        while True:
            period = config.get_publish_period(subscription)
            xpath = config.get_xpath(subscription)
            topic = config.get_kafka_topic(subscription)

            if first:
                s = m.establish_subscription(callback_kafka_publish, errback, xpath=xpath,
                                             period=period, topic=topic)
                first = False
            if not first:
                time.sleep((period/100)-0.2)



if __name__ == '__main__':
    config = SubscriptionConfig(YAML_FILE)
    host_configs = config.get_host_configs()
    for host_config in host_configs:
        p = Process(target=__process_host, args=(host_config,))
        p.start()

    '''sub = ''
    while True:
        if not sub:
            if 'producer' in locals():
                print ("kafka enabled")
                sub = m.establish_subscription(callback_kafka_publish, errback, xpath=XPATH, period=1000)
            else:
                print ("debug")
                sub = m.establish_subscription(debug_callback, errback, xpath=XPATH, period=1000)
        time.sleep(9.8)'''



