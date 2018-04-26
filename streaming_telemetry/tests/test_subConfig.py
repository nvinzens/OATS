import pytest
import sys
sys.path.append("..")
from SubscriptionConfig import SubscriptionConfig


# setup
FILE = 'test_config.yaml'
config = SubscriptionConfig(FILE)
host_configs = config.get_host_configs()
first_host_config = host_configs[0]
second_host_config = host_configs[1]

full_config = [{'username': 'user',
                    'host': '10.20.1.21',
                    'password': 'guest',
                    'port': 830,
                    'subscriptions': [{
                        'subscription': {
                            'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory',
                            'kafka_publish_topic': 'oats',
                            'period': 1000}
                    }, {
                        'subscription': {
                            'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/used-memory',
                            'kafka_publish_topic': 'oats2',
                            'period': 990}
                    }]},
                   {'username': 'user2',
                    'host': '10.20.1.22',
                    'password': 'guest2',
                    'port': 830,
                    'subscriptions': [{
                        'subscription': {
                            'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory',
                            'kafka_publish_topic': 'oats',
                            'period': 1000}
                    }]}]

full_host_config = {'username': 'user2', 'host': '10.20.1.22', 'password': 'guest2', 'port': 830, 'subscriptions': [{'subscription': {
        'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory', 'kafka_publish_topic': 'oats',
        'period': 1000}}]}

subcriptions = \
        [{'subscription': {
        'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory',
        'kafka_publish_topic': 'oats',
        'period': 1000}
    }, {
        'subscription': {
            'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/used-memory',
            'kafka_publish_topic': 'oats2',
            'period': 990}
        }]

first_sub = {'subscription': {
    'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory',
    'kafka_publish_topic': 'oats',
    'period': 1000}}

second_sub = {'subscription': {
    'xpath': '/memory-ios-xe-oper:memory-statistics/memory-statistic/used-memory',
    'kafka_publish_topic': 'oats2',
    'period': 990}}


def test_get_host_configs():
    #test setup
    assert host_configs == full_config


def test_get_host_config():
    #test setup
    assert second_host_config == full_host_config


def test_get_username():
    first_username = 'user'
    second_username = 'user2'
    assert first_username == config.get_username(first_host_config)
    assert second_username == config.get_username(second_host_config)


def test_get_password():
    first_password = 'guest'
    second_password = 'guest2'
    assert first_password == config.get_password(first_host_config)
    assert second_password == config.get_password(second_host_config)


def test_get_host():
    first_host = '10.20.1.21'
    second_host = '10.20.1.22'
    assert first_host == config.get_host(first_host_config)
    assert second_host == config.get_host(second_host_config)


def test_get_port():
    port = 830
    assert port == config.get_port(first_host_config)
    assert port == config.get_port(second_host_config)


def test_get_subscriptions():
    #test setup
    assert subcriptions == config.get_subscriptions(first_host_config)


def test_get_kafka_topic():
    first_topic = 'oats'
    second_topic = 'oats2'
    assert first_topic == config.get_kafka_topic(first_sub)
    assert second_topic == config.get_kafka_topic(second_sub)


def test_get_period():
    first_period = 1000
    second_period = 990
    assert first_period == config.get_publish_period(first_sub)
    assert second_period == config.get_publish_period(second_sub)


def test_get_xpath():
    first_xpath = '/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory'
    second_xpath = '/memory-ios-xe-oper:memory-statistics/memory-statistic/used-memory'
    assert first_xpath == config.get_xpath(first_sub)
    assert second_xpath == config.get_xpath(second_sub)







