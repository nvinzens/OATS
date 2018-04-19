#!/usr/bin/env python
from __future__ import with_statement
import salt.utils.event
import salt.client
import yaml


class SaltEventConfig:

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
        for sub in host_config['subscriptions']:
            subs.append(sub)
        return subs

    def get_host(self, host_config):
        return host_config['host']

    def get_port(self, host_config):
        return host_config['port']

    def get_username(self, host_config):
        return host_config['username']

    def get_password(self, host_con fig):
        return host_config['password']

    def get_kafka_topic(self, subscription):
        return subscription['subscription']['kafka_publish_topic']

    def get_publish_period(self, subscription):
        return subscription['subscription']['period']

    def get_xpath(self, subscription):
        return subscription['subscription']['xpath']


def send_salt_event(yang_message, minion, origin_ip, tag, message_details, error, optional_arg, case=None):
    '''
    Sends all the given data to the salt event bus.
    The data is used by different workflows in the salt system.
    :param yang_message: data for the workflow
    :param minion: the host from which the event originated
    :param origin_ip: the hosts IP address
    :param tag: the event tag
    :param message_details: more data
    :param error: the event
    :param optional_arg: directly used in the final event-tag. decides which workflow is triggered
    :param case: the optional oatsdb case-id
    :return: None
    '''
    caller = salt.client.Caller()
    caller.sminion.functions['event.send'](
        'napalm/syslog/*/' + error + '/' + optional_arg,
            {'minion': minion,
            'origin_ip': origin_ip,
            'yang_message': yang_message,
            'tag': tag,
             'error': error,
             'message_details': message_details,
             'case': case
             }
        )