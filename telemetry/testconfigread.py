from ncclient import manager
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import xmltodict
from OATSConfig import OATSConfig
from multiprocessing import Process, Lock


if __name__ == '__main__':
    config = OATSConfig("/home/nvinzens/Desktop/OATS/config.yaml")
    for sub in config.get_telemetry_subs():
       print sub.root_xpath, sub.name_xpath, sub.data_xpath