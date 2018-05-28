from ncclient import manager
import time
from kafka import KafkaProducer
import json
import xmltodict
from multiprocessing import Process
import logging

logger = logging.getLogger('oats.main')


def errback(notif):
    pass


def debug_callback(notif):
    #Only used for debugging purposes.
    jsonString = json.dumps(xmltodict.parse(notif.xml), indent=2)
    print (jsonString)


def callback_kafka_publish(notif, topic, host):
    '''
    Publishes the telemetry data to kafka.
    :param notif: Contains the telemetry data as xml.
    :param topic: the topic to produce the message to.
    :param host: the host from which the telemetry data
        is produced.
    :return: None
    '''
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    json_string = json.dumps(xmltodict.parse(notif.xml)).encode('utf-8')
    logger.debug('Sending telemetry data from host [{0}] to kafka topic [{1}].'
                 .format(host, topic))
    producer.send(topic, key=host, value=json_string)
    producer.flush()


def process_host_config(host_config, subscriptions):
    '''
    Processes the host config from the oats config file and starts a
    telemetry subscription for each specified subscription.
    :param host_config: Contains the the host information. See the class file (Host)
        for more information.
    :param config: Contains the whole oats config. See the class file (OATSConfig)
        for more information
    :return: None
    '''
    logger.debug('Processing config of host {0}'.format(host_config.hostname))
    for sub in subscriptions:
        p = Process(target=__create_subscriptions, args=(sub, host_config))
        p.start()


def __create_subscriptions(subscription, host_config):
    '''
    Creates a subscription based on the subscription param to the host
    specified on host_config. Meant to be run in parallel with other
    subsscriptions.
    :param subscription: Contains the subscription details.
    :param host_config: Contains the host details.
    :return: None
    '''
    first = True
    logger.debug('Open netconf session to host {0} on port {1}...'
                 .format(host_config.hostname, host_config.port))
    try:
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
                    logger.debug('Establish telemetry subscription for model [{0}] on host {1}.'
                                 .format(xpath, host_config.hostname))
                    s = m.establish_subscription(callback_kafka_publish, errback, xpath=xpath,
                                                 period=period, topic=topic, host=host_config.hostname)

                    logger.debug('Subscription result: {0}'.format(s.subscription_result))
                if not first:
                    time.sleep((period/100)-0.2)
                first = False
    except Exception:
        logger.exception('Exception while trying to establish netconf subscription.')
        exit(1)
