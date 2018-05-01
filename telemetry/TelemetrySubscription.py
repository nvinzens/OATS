

class TelemetrySubscription:

    def __init__(self, xpath, period, kafka_publish_topic, kafka_streams_eval, event_threshold):
        self.xpath = xpath
        self.period = period
        self.kafka_publish_topic = kafka_publish_topic
        self.kafka_streams_eval = kafka_streams_eval
        # TODO: get fields from event_threshold
