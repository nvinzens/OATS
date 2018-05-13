import pytest
import sys
sys.path.append("..")
from OATSConfig import OATSConfig


# setup
FILE = 'test_configs/min_config.yaml'


def test_get_host_configs():
    config = OATSConfig(FILE)
    host_configs = config.get_host_configs()

    first_host = '10.20.1.22'
    first_port = 999
    first_user = 'user'
    first_pw = 'pw'

    second_host = '10.20.1.21'
    second_user = 'user2'
    second_pw = 'pw2'
    second_port = 1000

    assert first_host == host_configs[0].hostname
    assert first_port == host_configs[0].port
    assert first_user == host_configs[0].username
    assert first_pw == host_configs[0].password

    assert second_host == host_configs[1].hostname
    assert second_port == host_configs[1].port
    assert second_user == host_configs[1].username
    assert second_pw == host_configs[1].password


def test_get_telemetry_subscriptions():
    config = OATSConfig(FILE)
    subscriptions = config.get_telemetry_subscriptions()

    first_xpath = '/if:interfaces-state/interface/statistics/out-discards'
    first_period = 1000
    first_kafka_publish_topic = 'interfaces-out-discards'
    first_kafka_streams_eval = False
    first_correlate_event = False


    second_xpath = '/if:interfaces-state/interface/statistics/in-discards'
    second_period = 100
    second_kafka_publish_topic = 'interfaces-in-dicards'
    second_kafka_streams_eval = False
    second_correlate_event = False

    assert first_xpath == subscriptions[0].xpath
    assert first_period == subscriptions[0].period
    assert first_kafka_publish_topic == subscriptions[0].kafka_publish_topic
    assert first_kafka_streams_eval == subscriptions[0].kafka_streams_eval
    assert first_correlate_event == subscriptions[0].correlate_event

    assert second_xpath == subscriptions[1].xpath
    assert second_period == subscriptions[1].period
    assert second_kafka_publish_topic == subscriptions[1].kafka_publish_topic
    assert second_kafka_streams_eval == subscriptions[1].kafka_streams_eval
    assert second_correlate_event == subscriptions[1].correlate_event




