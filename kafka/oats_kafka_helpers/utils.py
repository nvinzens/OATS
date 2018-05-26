from oats import oatsdbhelpers
from oatsnb import oatsnb


def get_n_of_events_and_root_host(error, host, yang_message, current_case=None):
    '''
    Gets the number of needed events and the root_host.
    :param error: the error of the event.
    :param host: the host from which the event originated.
    :param yang_message: the syslog yang message.
    :param current_case: the current oats case id
    :return: the amount of needed events and the root_host.
        The root host is the root of the event eg. the one on
        which the OSPF process died.
    '''
    interface = oatsdbhelpers.get_interface(error, yang_message)
    root_host = oatsnb.get_interface_neighbor(host, interface, case=current_case)
    return len(oatsnb.get_ospf_neighbors(host, case=current_case)), root_host


def extract_record_data(message):
    '''
    Extracts the host, timestamp and data fields out of a kafka message.
    :param message: the kafka message.
    :return: host, timestamp, data
    '''
    host = None
    timestamp = None
    data = None
    for key, value in message._asdict().items():
        if key == 'key':
            host = value
        elif key == 'timestamp':
            timestamp = value
        elif key == 'value':
            data = value
    return host, timestamp, data