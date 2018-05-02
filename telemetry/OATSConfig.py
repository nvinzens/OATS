import yaml
import Host
from TelemetrySubscription import OATSTelemetrySubscription
from Host import OATSHost

class OATSConfig:


    def __init__(self, yaml_file_name):
        file = open(yaml_file_name)
        self.config = yaml.load(file)

    def get_host_configs(self):
        raw_hosts = self.__get_raw_hosts()
        host_configs = []
        for host_config in raw_hosts:
            hostname = self.__get_host(host_config)
            port = self.__get_port(host_config)
            username = self.__get_username(host_config)
            password = self.__get_password(host_config)
            host = OATSHost(hostname, port, username, password)
            host_configs.append(host)
        return host_configs

    def get_telemetry_subs(self):
        raw_subs = self.__get_raw_subs()
        tel_subs = []
        for raw_sub in raw_subs:
            xpath = self.__get_xpath(raw_sub)
            period = self.__get_publish_period(raw_sub)
            kafka_publish_topic = self.__get_kafka_topic(raw_sub)
            evaluate = self.__get_kafka_eval(raw_sub)
            event_thresh_data = self.__get_event_thresh_data(raw_sub)
            sub = OATSTelemetrySubscription(xpath, period, kafka_publish_topic, evaluate, event_thresh_data)
            tel_subs.append(sub)
        return tel_subs

    def __get_raw_hosts(self):
        hosts = []
        for host in self.config['hosts']:
            hosts.append(host)
        return hosts

    def __get_raw_subs(self):
        subs = []
        for sub in self.config['subscriptions']:
            subs.append(sub)
        return subs

    def __get_host(self, host_config):
        return host_config['host']

    def __get_port(self, host_config):
        return host_config['port']

    def __get_username(self, host_config):
        return host_config['username']

    def __get_password(self, host_config):
        return host_config['password']

    def __get_kafka_topic(self, subscription):
        return subscription['subscription']['kafka_publish_topic']

    def __get_publish_period(self, subscription):
        return subscription['subscription']['period']

    def __get_xpath(self, subscription):
        return subscription['subscription']['xpath']


    def __get_kafka_eval(self, subscription):
        return subscription['subscription']['kafka_streams_eval']


    def __get_event_thresh_data(self, subscription):
        return subscription['subscription']['event_threshold_data']



