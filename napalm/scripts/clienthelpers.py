import correlate


def get_optional_arg(msg, error):
    '''
    Gets the optional_arg string out of
    a given yang-message and returns it.
    Every error has a different suitable
    optional_arg parameter.
    Needs to be extended for every new
    error/event.
    :param msg: the message from napalm-logs.
    :param error: the error, so it can be determined where the optional_arg can be gotten
    :return: the optional_arg (str), empty string if error is not part of the system yet.
    '''
    yang_message = msg['yang_message']
    if error == correlate.INTERFACE_CHANGED:
        return __get_interface_status(yang_message)
    if error == correlate.OSPF_NEIGHBOR_DOWN:
        return __get_ospf_change_reason(yang_message)
    if error == correlate.OSPF_NEIGHBOR_UP:
        return 'ospf_nbr_up'
    else:
        return ''


def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''


def __get_ospf_change_reason(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v['adjacency-state-change-reason-message'] == 'Dead timer expired':
                return 'dead_timer_expired'
            return ''
        if v:
            return __get_ospf_change_reason(v)
        else:
            return ''

