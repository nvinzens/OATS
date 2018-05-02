from ncclient import manager
import time
from kafka import KafkaProducer
import subprocess
import json
import xmltodict
from OATSConfig import OATSConfig
from multiprocessing import Process, Lock

YAML_FILE = '/home/OATS/config.yaml'

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


def __process_host_config(host_config, config):
    subs = config.get_telemetry_subs()
    for sub in subs:
        p = Process(target=__create_subscriptions, args=(sub, host_config))
        p.start()


def __create_subscriptions(subscription, host_config):
    first = True
    with manager.connect(host=host_config.hostname,
                         port=host_config.port,
                         username=host_config.username,
                         password=host_config.password,
                         allow_agent=False,
                         look_for_keys=False,
                         hostkey_verify=False,
                         unknown_host_cb=True,
                         timeout=100
                         ) as m:
        period = subscription.period
        xpath = subscription.xpath
        topic = subscription.kafka_publish_topic
        while True:
            if first:
                s = m.establish_subscription(callback_kafka_publish, errback, xpath=xpath,
                                             period=period, topic=topic, host=host_config.hostname)

                print (s.subscription_result)
            if not first:
                time.sleep((period/100)-0.2)
            first = False



if __name__ == '__main__':
    config = OATSConfig(YAML_FILE)
    host_configs = config.get_host_configs()
    for host_config in host_configs:
        p = Process(target=__process_host_config, args=(host_config, config))
        p.start()
    # TODO: start kafka-streams clients
    subscriptions = config.get_telemetry_subs()
    for sub in subscriptions:
        if sub.kafka_streams_eval:
            p = Process(target=subprocess.call, args=([
                'java', '-jar', 'temp.jar', sub.kafka_publish_topic,
                sub.kafka_event_topic, sub.event_threshold, sub.operator,
                sub.root_xpath, sub.name_xpath, sub.data_xpath
            ]))

    # TODO: start kafka-streams consumers
    #for subcription in config.get_telemetry_subs():
     #   pass




