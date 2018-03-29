from ncclient import manager
from lxml import etree
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
from SubscriptionConfig import SubscriptionConfig
from multiprocessing import Process
import multiprocessing as mp
import os
import collections

XPATH = "/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory"
TOPIC = 'oats'
YAML_FILE = 'config.yaml'


def errback(notif):
    pass


def debug_callback(notif):
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    #print (etree.tostring(notif.datastore_ele, pretty_print=True).decode('utf-8'))
    print (jsonString)

def callback_kafka_publish(notif):
    # Publishes message to Kafka messaging bus
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    #producer.send(TOPIC, jsonString)
    print (jsonString)


def __create_subscriptions(host_config):
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

        subs = config.get_subscriptions(host_config)
        counter = 0
        timers = collections.deque()
        while True:
            period = 0
            for sub in subs:
                period = config.get_publish_period(sub)
                xpath = config.get_xpath(sub)
                #if not active_subscriptions[xpath]:

                if counter < len(subs):
                    s = m.establish_subscription(callback_kafka_publish, errback, xpath=xpath,
                                                 period=period)
                    counter = counter + 1
                    timers.append(period)
                #else:
                #    counter = len(subs)
                #    next = timers.popleft()
                #    if period - next >= 0:
                #        time.sleep(next - 0.2)
                #    timers.append(period)
            if counter < len(subs):
                time.sleep((period/100)-0.2)





if __name__ == '__main__':
    # producer = KafkaProducer(bootstrap_servers='localhost:9092')
    config = SubscriptionConfig(YAML_FILE)
    host_configs = config.get_host_configs()
    for host_config in host_configs:
        p = mp.Process(target=__create_subscriptions, args=(host_config,))
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



