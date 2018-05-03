from oats import oatsdbhelpers
from oatsnb import oatsnb


def get_n_of_events_and_root_host(error, host, yang_message, current_case=None):
    interface = oatsdbhelpers.get_interface(error, yang_message)
    root_host = oatsnb.get_interface_neighbor(host, interface, case=current_case)
    return len(oatsnb.get_ospf_neighbors(host, case=current_case)), root_host


def extract_record_data(message):
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