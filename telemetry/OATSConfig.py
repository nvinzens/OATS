import yaml
import errno
import os
from TelemetrySubscription import OATSTelemetrySubscription
from Host import OATSHost

class OATSConfig:


    def __init__(self, yaml_file_name):
        try:
            file = open(yaml_file_name)
            self.config = yaml.load(file)
        except IOError:
           raise IOError("Could not read OATS configuration file. Missing file at " + yaml_file_name)

    def get_host_configs(self):
        raw_hosts = self.__get_raw_hosts()
        host_configs = []
        for host_config in raw_hosts:
            try:
                hostname = self.__get_host(host_config)
                port = self.__get_port(host_config)
                username = self.__get_username(host_config)
                password = self.__get_password(host_config)
                host = OATSHost(hostname, port, username, password)
                host_configs.append(host)
            except Exception:
                raise ValueError("Exception while reading host configuration."
                                 " Check the config file for errors/missing fields for the host(s).")
        return host_configs

    def get_telemetry_subscriptions(self):
        tel_subs = []
        try:
            raw_subs = self.__get_raw_subs()
            for raw_sub in raw_subs:
                xpath = self.__get_xpath(raw_sub)
                period = self.__get_publish_period(raw_sub)
                kafka_publish_topic = self.__get_kafka_topic(raw_sub)
                evaluate = self.__get_kafka_eval(raw_sub)
                correlate_event = self.__get_correlate_event(raw_sub)
                # init optional params
                event_thresh_data = None
                jar_location = None
                event = None
                correlation_data = None
                if evaluate:
                    event_thresh_data = self.__get_event_thresh_data(raw_sub)
                    jar_location = self.__get_jar_location(raw_sub)
                    event = self.__get_event(raw_sub)
                if correlate_event:
                    correlation_data = self.__get_correlation_data(raw_sub)
                    event = self.__get_event(raw_sub)
                sub = OATSTelemetrySubscription(xpath, period, kafka_publish_topic, evaluate, correlate_event,
                                                correlate=correlation_data,event=event, jar_location=jar_location,
                                                event_threshold_data=event_thresh_data)
                tel_subs.append(sub)

        except ValueError as e:
            raise e
        except Exception:
            raise ValueError("Exception while reading subscriptions configuraton."
                                 " Check the config file for errors/missing fields for the subscription(s).")
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

    def __get_correlation_data(self, subscription):
        return subscription['subscription']['correlate']

    def __get_event(self, subscription):
        return subscription['subscription']['event']

    def __get_correlate_event(self, subscription):
        return subscription['subscription']['correlate_event']

    def __get_kafka_topic(self, subscription):
        return subscription['subscription']['kafka_publish_topic']

    def __get_publish_period(self, subscription):
        return subscription['subscription']['period']

    def __get_xpath(self, subscription):
        return subscription['subscription']['xpath']

    def __get_kafka_eval(self, subscription):
        return subscription['subscription']['kafka_streams_eval']

    def __get_jar_location(self, subscription):
        return subscription['subscription']['kafka_streams_jar_location']

    def __get_event_thresh_data(self, subscription):
        return subscription['subscription']['event_threshold_data']



