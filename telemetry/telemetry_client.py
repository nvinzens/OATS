from ncclient import manager
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
from SubscriptionConfig import SubscriptionConfig
from multiprocessing import Process, Lock

YAML_FILE = 'config.yaml'

def errback(notif):
    pass


def debug_callback(notif):
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    print (jsonString)


def callback_kafka_publish(notif, topic, host):
    # Publishes message to Kafka topic
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    json_string = json.dumps(xmltodict.parse(notif.xml)).encode('utf-8')
    producer.send(topic, key=host, value=json_string)
    producer.flush()
    print (json_string)


def __process_host(host_config):
    subs = config.get_subscriptions(host_config)
    for sub in subs:
        p = Process(target=__create_subscriptions, args=(sub, host_config))
        p.start()


def __create_subscriptions(subscription, host_config):
    first = True
    host = config.get_host(host_config)
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
                                             period=period, topic=topic, host=host)

                print (s.subscription_result)
            if not first:
                time.sleep((period/100)-0.2)
            first = False



if __name__ == '__main__':
    config = SubscriptionConfig(YAML_FILE)
    host_configs = config.get_host_configs()
    for host_config in host_configs:
        p = Process(target=__process_host, args=(host_config,))
        p.start()




