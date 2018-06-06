import yaml

from telemetry.model.Host import OATSHost
from telemetry.model.TelemetrySubscription import OATSTelemetrySubscription


class OATSConfig:
    '''
    Reads the oats config file from the given location (default: /etc/oats/config.yaml.
    '''

    def __init__(self, yaml_file_name):
        try:
            f = open(yaml_file_name)
            self.config = yaml.load(f)
        except IOError:
            raise IOError("Could not read OATS configuration file. Missing file at " + yaml_file_name)

    def get_host_configs(self):
        '''
        Returns the host configs as a list.
        :return: the host configs (list)
        '''
        host_configs = []
        try:
            raw_hosts = self.__get_raw_hosts()

            for host_config in raw_hosts:
                hostname = self.__get_host(host_config)
                port = self.__get_port(host_config)
                username = self.__get_username(host_config)
                password = self.__get_password(host_config)
                host = OATSHost(hostname, port, username, password)
                host_configs.append(host)
        except ValueError as e:
            raise e
        except Exception:
            raise ValueError("Exception while reading host configuration."
                             " Check the config file for errors/missing fields for the host(s).")
        return host_configs

    def get_telemetry_subscriptions(self):
        '''
        Returns the subscriptions as a list.
        :return: the subscriptions (list)
        '''
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
        except Exception as e:
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
        try:
            for sub in self.config['subscriptions']:
                subs.append(sub)
        except Exception:
            raise ValueError("Missing <subscriptions> section in config. "
                             "Please prodive atleast one valid subscriptions.")
        return subs

    def __get_host(self, host_config):
        try:
            return host_config['host']
        except KeyError:
            raise ValueError("Missing host config element <host>")

    def __get_port(self, host_config):
        try:
            return host_config['port']
        except KeyError:
            raise ValueError("Missing host config element <port>")

    def __get_username(self, host_config):
        try:
            return host_config['username']
        except KeyError:
            raise ValueError("Missing host config element <username>")

    def __get_password(self, host_config):
        try:
            return host_config['password']
        except KeyError:
            raise ValueError("Missing host config element <password>")

    def __get_correlation_data(self, subscription):
        try:
            return subscription['subscription']['correlate']
        except KeyError:
            raise ValueError("Missing subscription config element <correlate>")

    def __get_event(self, subscription):
        try:
            return subscription['subscription']['event']
        except KeyError:
            raise ValueError("Missing subscription config element <event>")

    def __get_correlate_event(self, subscription):
        try:
            return subscription['subscription']['correlate_event']
        except KeyError:
            raise ValueError("Missing subscription config element <correlate_event>")

    def __get_kafka_topic(self, subscription):
        try:
            return subscription['subscription']['kafka_publish_topic']
        except KeyError:
            raise ValueError("Missing subscription config element <kafka_publish_topic>")

    def __get_publish_period(self, subscription):
        try:
            return subscription['subscription']['period']
        except KeyError:
            raise ValueError("Missing subscription config element <period>")

    def __get_xpath(self, subscription):
        try:
            return subscription['subscription']['xpath']
        except KeyError:
            raise ValueError("Missing subscription config element <xpath>")

    def __get_kafka_eval(self, subscription):
        try:
            return subscription['subscription']['kafka_streams_eval']
        except KeyError:
            raise ValueError("Missing subscription config element <kafka_streams_eval>")

    def __get_jar_location(self, subscription):
        try:
            return subscription['subscription']['kafka_streams_jar_location']
        except KeyError:
            raise ValueError("Missing subscription config element <kafka_streams_jar_location>")

    def __get_event_thresh_data(self, subscription):
        try:
            return subscription['subscription']['event_threshold_data']
        except KeyError:
            raise ValueError("Missing subscription config element <event_threshold_data>")




