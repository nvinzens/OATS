

class OATSTelemetrySubscription:

    def __init__(self, xpath, period, kafka_publish_topic, kafka_streams_eval, event_threshold_data):
        self.xpath = xpath
        self.period = period
        self.kafka_publish_topic = kafka_publish_topic
        self.kafka_streams_eval = kafka_streams_eval
        if kafka_streams_eval:
            self.event_threshold = self.__get_threshold(event_threshold_data)
            self.operator = self.__get_operator(event_threshold_data)
            self.kafka_event_topic = self.__get_kafka_topic(event_threshold_data)
            self.event = self.__get_event(event_threshold_data)
            self.data_xpaths = self.__get_data_xpaths(event_threshold_data)

    def __get_threshold(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'value':
                    return data[key]


    def __get_operator(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'operator':
                    return data[key]

    def __get_kafka_topic(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'kafka_event_topic':
                    return data[key]

    def __get_event(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'event':
                    return data[key]

    def __get_data_xpaths(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'data_xpaths':
                    return data[key]
