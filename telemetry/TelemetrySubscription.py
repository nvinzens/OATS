

class OATSTelemetrySubscription:
    '''
    Contains all the subscription details specified in the OATS config file.
    '''

    def __init__(self, xpath, period, kafka_publish_topic, kafka_streams_eval, correlate_event, correlate=None, event=None,
                 jar_location=None, event_threshold_data=None, ):
        '''
        :param xpath: the yang model to subscribe to as xpath.
        :param period: the subscription period (eg. every 10 seconds).
        :param kafka_publish_topic: the kafka topic to publish the messages to.
        :param kafka_streams_eval: If set a kafka streams client will be started to analyze the data produced by this
            subscription.
        :param correlate_event: If set the event data produced will be correlated with the given function.
        :param correlate: Contains the correlation data.
        :param event: the event name to use.
        :param correlate_function: the correlation function to use, eg. compress.
        :param correlate_for: the amount of time to correlate for.
        :param jar_location: the location of the java jar file which contains the kafka streams client.
        :param event_threshold_data: contains the data used by the kafka streams client.
        :param event_threshold: the threshold used by the kafka streams client to evaluate if an event has occured.
        :param operator: the operator to use to evaluate the threshold, eg. greater_than, smaller_than etc.
        :param kafka_event_topic: the topic to produce the kafka streams events to.
        :param root_xpath: the xpath that leads to the data in the yang model.
        :param name_xpath: the xpath from the root_xpath to the name of the evaluated statistic.
        :param data_xpath: the xpath from the root_xpath to the value of the evaluated statistic.
        '''
        self.xpath = xpath
        self.period = period
        self.kafka_publish_topic = kafka_publish_topic
        self.kafka_streams_eval = kafka_streams_eval
        if kafka_streams_eval:
            self.event_threshold = self.__get_threshold(event_threshold_data)
            self.operator = self.__get_operator(event_threshold_data)
            self.kafka_event_topic = self.__get_kafka_topic(event_threshold_data)
            self.root_xpath, self.name_xpath, self.data_xpath = self.__get_data_xpaths(event_threshold_data)
            self.jar_location = jar_location
        if kafka_streams_eval or correlate_event:
            self.event = event
        self.correlate_event = correlate_event
        if correlate_event:
            self.correlate_function, self.correlate_for = self.__get_correlation_data(correlate)

    def __get_correlate_event(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'correlate_event':
                    return data[key]
        raise ValueError("Missing subscription config element <correlate_event>")

    def __get_threshold(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'value':
                    return data[key]
        raise ValueError("Missing subscription config element <value> under <event_threshold_data>")


    def __get_operator(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'operator':
                    return data[key]
        raise ValueError("Missing subscription config element <operator> under <event_threshold_data>")

    def __get_kafka_topic(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'kafka_event_topic':
                    return data[key]
        raise ValueError("Missing subscription config element <kafka_event_topic> under <event_threshold_data>")

    def __get_correlation_data(self, correlate_data):
        correlate_func = None
        correlate_for = None
        for data in correlate_data:
            try:
                correlate_func = data['function']
            except KeyError:
                raise ValueError("Missing subscription config element <function> under <correlate>")
            try:
                correlate_for = data['correlation_time']
            except KeyError:
                raise ValueError("Missing subscription config element <correlation_time> under <correlate>")
        return correlate_func, correlate_for

    def __get_data_xpaths(self, event_data):
        root_xpath = None
        name_xpath = None
        data_xpath = None

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
        if root_xpath is None:
            raise ValueError("Missing subscription config element <root_xpath> under <data_xpaths>")
        if name_xpath is None:
            raise ValueError("Missing subscription config element <name_xpath> under <data_xpaths>")
        if data_xpath is None:
            raise ValueError("Missing subscription config element <data_xpath> under <data_xpaths>")
        return root_xpath, name_xpath, data_xpath

    def __get_jar_location(self, event_data):
        for data in event_data:
            for key in data:
                if key == 'kafka_streams_jar_location':
                    return data[key]
        raise ValueError("Missing subscription config element <kafka_streams_jar_location>")
