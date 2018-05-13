import pytest
import sys
sys.path.append("..")
from OATSConfig import OATSConfig


def test_get_config_without_port():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_port.yaml')
        host_configs = config.get_host_configs()
    assert "Missing host config element <port>" in str(e.value)


def test_get_without_hosts():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_hosts.yaml')
        host_configs = config.get_host_configs()
    assert "Exception while reading host configuration. " \
           "Check the config file for errors/missing fields for the host(s)." in str(e.value)


def test_get_config_without_xpath():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_xpath.yaml')
        subs = config.get_telemetry_subscriptions()
    assert "Missing subscription config element <xpath>" in str(e.value)


def test_get_config_without_thresh_value():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_thresh_value.yaml')
        subs = config.get_telemetry_subscriptions()
    assert "Missing subscription config element <value> under <event_threshold_data>" in str(e.value)


def test_get_config_without_correlate_func():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_correlate_func.yaml')
        subs = config.get_telemetry_subscriptions()
    assert "Missing subscription config element <function> under <correlate>" in str(e.value)


def test_get_config_without_data_xpath():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_data_xpath.yaml')
        subs = config.get_telemetry_subscriptions()
    assert "Missing subscription config element <data_xpath> under <data_xpaths>" in str(e.value)


def test_get_config_without_event():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_event.yaml')
        subs = config.get_telemetry_subscriptions()
    assert "Missing subscription config element <event>" in str(e.value)


def test_get_without_subs():
    with pytest.raises(ValueError) as e:
        config = OATSConfig('test_configs/config_no_subs.yaml')
        host_configs = config.get_telemetry_subscriptions()
    assert "Missing <subscriptions> section in config. Please prodive atleast one valid subscriptions." in str(e.value)


def test_no_valid_file():
    with pytest.raises(IOError) as e:
        config = OATSConfig('test_configs/no_file.yaml')
    assert "Could not read OATS configuration file. Missing file at test_configs/no_file.yaml" in str(e.value)

