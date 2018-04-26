from oats import oatsdbhelpers


def get_n_of_events_and_root_host(error, host, yang_message, current_case=None):
    interface = oatsdbhelpers.get_interface(error, yang_message)
    root_host = oatsdbhelpers.get_interface_neighbor(host, interface, case=current_case)
    return len(oatsdbhelpers.get_ospf_neighbors(host, case=current_case)), root_host
