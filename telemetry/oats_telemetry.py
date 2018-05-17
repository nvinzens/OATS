import netconf_telemetry
import kafka_streams
from OATSConfig import OATSConfig
from multiprocessing import Process


YAML_FILE = '/home/OATS/config.yaml'


if __name__ == '__main__':
    config = OATSConfig(YAML_FILE)

    # start kafka streams clients and consumers
    subscriptions = config.get_telemetry_subscriptions()
    for sub in subscriptions:
        if sub.kafka_streams_eval:
            kafka_streams.start_kafka_streams(sub)

    # establish telemetry subscriptions
    host_configs = config.get_host_configs()
    for host_config in host_configs:
        p = Process(target=netconf_telemetry.process_host_config, args=(host_config, config))
        p.start()





