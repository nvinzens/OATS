import yaml
import Host
import TelemetrySubscription

class OATSConfigReader:


    def __init__(self, yaml_file_name):
        file = open(yaml_file_name)
        self.config = yaml.load(file)

    def get_host_configs(self):
        hosts = []
        for host in self.config['hosts']:
            hosts.append(host)
        return hosts

    def get_subscriptions(self, host_config):
        subs = []
        for sub in self.config['subscriptions']:
            subs.append(sub)
        return subs

    def get_host(self, host_config):
        return host_config['host']

    def get_port(self, host_config):
        return host_config['port']

    def get_username(self, host_config):
        return host_config['username']

    def get_password(self, host_config):
        return host_config['password']

    def get_kafka_topic(self, subscription):
        return subscription['subscription']['kafka_publish_topic']

    def get_publish_period(self, subscription):
        return subscription['subscription']['period']

    def get_xpath(self, subscription):
        return subscription['subscription']['xpath']



