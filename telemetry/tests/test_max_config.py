import pytest
import sys
sys.path.append("..")
from OATSConfig import OATSConfig


# setup
FILE = 'test_configs/max_config.yaml'


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
    first_thresh_value = 100000
    first_thresh_operator = 'greater_than'
    first_thresh_name_xpath = '/name'
    first_correlate_event = True
    first_correlate_function = 'compress'
    first_correlate_for = 10

    second_xpath = '/if:interfaces-state/interface/statistics/out-discards'
    second_period = 100
    second_thresh_value = 5
    second_thresh_operator = 'smaller_than'
    second_thresh_name_xpath = '/test'
    second_correlate_event = False

    third_xpath = '/if:interfaces-state/interface/statistics/in-discards'
    third_kafka_streams_eval = False
    third_correlate_event = True
    third_correlate_function = 'aggregate'
    third_correlate_for = 5

    assert first_xpath == subscriptions[0].xpath
    assert first_period == subscriptions[0].period
    assert first_thresh_value == subscriptions[0].event_threshold
    assert first_thresh_operator == subscriptions[0].operator
    assert first_thresh_name_xpath == subscriptions[0].name_xpath
    assert first_correlate_event == subscriptions[0].correlate_event
    assert first_correlate_function == subscriptions[0].correlate_function
    assert first_correlate_for == subscriptions[0].correlate_for

    assert second_xpath == subscriptions[1].xpath
    assert second_period == subscriptions[1].period
    assert second_thresh_value == subscriptions[1].event_threshold
    assert second_thresh_operator == subscriptions[1].operator
    assert second_thresh_name_xpath == subscriptions[1].name_xpath
    assert second_correlate_event == subscriptions[1].correlate_event

    assert third_xpath == subscriptions[2].xpath
    assert third_kafka_streams_eval == subscriptions[2].kafka_streams_eval
    assert third_correlate_event == subscriptions[2].correlate_event
    assert third_correlate_function == subscriptions[2].correlate_function
    assert third_correlate_for == subscriptions[2].correlate_for



