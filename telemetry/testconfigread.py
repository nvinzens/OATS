from ncclient import manager
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
from OATSConfig import SubscriptionConfig
from multiprocessing import Process, Lock


if __name__ == '__main__':
    config = SubscriptionConfig("/home/nvinzens/Desktop/OATS/config.yaml")
    host_configs = config.get_host_configs()
    subs = config.get_subscriptions(config)
    #print host_configs
    print subs