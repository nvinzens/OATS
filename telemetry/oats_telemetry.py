import logging
import logging.config
import logging.handlers
from multiprocessing import Process

import yaml

import kafka_streams
import netconf_telemetry
from telemetry.model.OATSConfig import OATSConfig

'''
OATS main thread that reads the oats config file and starts kafka streams clients
and netconf telemetry subscriptions.
'''

YAML_FILE = '/etc/oats/config.yaml'


def main():
    log_file = open('/etc/oats/logging.yaml')
    log_conf = yaml.load(log_file)
    logging.config.dictConfig(log_conf['logging'])
    logger = logging.getLogger('oats.main')

    logger.info('Starting oats telemetry client...')

    logger.debug('Reading oats configuration from {0}...'.format(YAML_FILE))

    try:
        config = OATSConfig(YAML_FILE)
        subscriptions = config.get_telemetry_subscriptions()
        host_configs = config.get_host_configs()
    except Exception:
        logger.exception('Exception while reading configuration file. Stopping oats telemetry...')
        exit(1)

    # start kafka streams clients and consumers
    for sub in subscriptions:
        if sub.kafka_streams_eval:
            logger.info('Starting kafka streams for [{0}] YANG model...'.format(sub.xpath))
            try:
                kafka_streams.start_kafka_streams(sub)
            except Exception:
                logger.exception('Exception while starting kafka streams. Telemetry data will not be analyzed.')

    # establish telemetry subscriptions
    for host_config in host_configs:
        logger.info("Starting netconf telemetry session(s) for host {0}...".format(host_config.hostname))
        p = Process(target=netconf_telemetry.process_host_config, args=(host_config, subscriptions))
        p.start()


if __name__ == '__main__':
    main()





