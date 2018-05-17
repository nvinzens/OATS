from ncclient import manager
import time
from kafka import KafkaProducer
import json
import xmltodict
from multiprocessing import Process


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
    #print (json_string)


def process_host_config(host_config, config):
    subs = config.get_telemetry_subscriptions()
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