import netconf_telemetry
import kafka_streams
from OATSConfig import OATSConfig
from multiprocessing import Process
import logging
import logging.handlers


YAML_FILE = '/etc/oats/config.yaml'


def main():
    logger = logging.getLogger('oats')
    logger.setLevel(logging.DEBUG)

    # limit logfile to 50MBytes
    fh = logging.handlers.RotatingFileHandler('/var/log/oats/logs', maxBytes=52428800)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    logger.info('Starting oats telemetry client...')

    logger.debug('Reading oats configuration from {0}...'.format(YAML_FILE))

    try:
        config = OATSConfig(YAML_FILE)
        subscriptions = config.get_telemetry_subscriptions()
        host_configs = config.get_host_configs()
    except Exception as e:
        logger.exception('Exception while reading configuration file. Stopping oats telemetry...')
        exit(1)

    # start kafka streams clients and consumers
    for sub in subscriptions:
        if sub.kafka_streams_eval:
            logger.info('Starting kafka streams for {0} YANG model...'.format(sub.xpath))
            kafka_streams.start_kafka_streams(sub)

    # establish telemetry subscriptions
    for host_config in host_configs:
        logger.info("Starting netconf telemetry session(s) for host {0}...".format(host_config.hostname))
        p = Process(target=netconf_telemetry.process_host_config, args=(host_config, config))
        p.start()


if __name__ == '__main__':
    main()





