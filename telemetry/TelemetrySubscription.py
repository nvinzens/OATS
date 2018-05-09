

class OATSTelemetrySubscription:

    def __init__(self, xpath, period, kafka_publish_topic, kafka_streams_eval,
                 jar_location=None, event_threshold_data=None):

        self.xpath = xpath
        self.period = period
        self.kafka_publish_topic = kafka_publish_topic
        self.kafka_streams_eval = kafka_streams_eval
        if kafka_streams_eval:
            self.event_threshold = self.__get_threshold(event_threshold_data)
            self.operator = self.__get_operator(event_threshold_data)
            self.kafka_event_topic = self.__get_kafka_topic(event_threshold_data)
            self.event = self.__get_event(event_threshold_data)
            self.correlate_event = self.__get_correlate_event(event_threshold_data)
            if self.correlate_event:
                self.correlate_function, self.correlate_for = self.__get_correlation_data(event_threshold_data)
            self.root_xpath, self.name_xpath, self.data_xpath = self.__get_data_xpaths(event_threshold_data)
            self.jar_location = jar_location


    def __get_correlate_event(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'correlate_event':
                    return data[key]

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

    def __get_correlation_data(self, event_data):
        correlate_func = ''
        correlate_for = -1

        for data in event_data:
            for key in data:
                if key == 'correlate':
                    for d in data[key]:
                        for k in d:
                            if k == 'function':
                                correlate_func = d[k]
                            if k == 'correlation_time':
                                correlate_for = d[k]
        return correlate_func, correlate_for


    def __get_data_xpaths(self, event_data):
        root_xpath = ''
        name_xpath = ''
        data_xpath = ''

        for data in event_data:
            for key in data:
                if key == 'data_xpaths':
                    for d in data[key]:
                        for k in d:
                            if k == 'root_xpath':
                                root_xpath = d[k]
                            if k == 'name_xpath':
                                name_xpath = d[k]
                            if k == 'data_xpath':
                                data_xpath = d[k]
        return root_xpath, name_xpath, data_xpath


    def __get_jar_location(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'kafka_streams_jar_location':
                    return data[key]
