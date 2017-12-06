from oats import oatsdbhelpers
import oatssalthelpers
from multiprocessing.pool import ThreadPool


def ifdown(host, origin_ip, yang_message, error, tag, interface=None, current_case=None):
    '''
    Function that gathers data in the network and executes a workflow according to the data.
    Is triggered by the salt system once an INTERFACE_DOWN event arrives in the salt
    event bus. Will try to fix the error or send a notification if it is unable to
    do so.
    :param host: The host from which the event originated
    :param origin_ip: The hosts IP address
    :param yang_message: Contains event specific data, eg. the affected Interface
    :param error: The error, in this case INTERFACE_DOWN, INTERFACHE_CHANGED/down
    :param tag: The tag used in the syslog message that triggered the event
    :param interface: The affected Interface
    :param current_case: Optional: the current case. Can be passed if the workflow has started
    earlier (eg. in the client that processes the syslog messages).
    :return: error, tag, a comment, configuration changes, success (bool)
    '''
    conf = 'No changes'
    success = False
    interface = oatsdbhelpers.get_interface(error, yang_message)
    comment = 'Interface down status on host ' + host + ' detected. '
    if current_case is None or current_case == 'None':
        current_case = oatsdbhelpers.create_case(error, host, solution='Case created in salt tshoot.ifdown.')
    interface_neighbor = oatsdbhelpers.get_interface_neighbor(host, interface, case=current_case)

    neighbors = oatsdbhelpers.get_neighbors(interface_neighbor, case=current_case)
    device_up = oatssalthelpers.check_device_connectivity(neighbors, interface_neighbor, case=current_case)

    if device_up:
        # cycle affected interface
        oatssalthelpers.if_shutdown(host, interface, case=current_case)
        conf = oatssalthelpers.if_noshutdown(host, interface, case=current_case)
        # check if cycle was successful
        success = oatssalthelpers.ping(host, interface_neighbor, check_connectivity=True, case=current_case)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove, only useful for debugging
            oatssalthelpers.post_slack(comment, case=current_case)
            oatsdbhelpers.close_case(current_case)
        else:
            oatsdbhelpers.update_case(current_case, solution=error + 'could not get resolved. Technician needed.', status=oatsdbhelpers.Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            oatssalthelpers.post_slack(comment, case=current_case)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        oatsdbhelpers.update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=oatsdbhelpers.Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor + ' is down.'
        oatssalthelpers.post_slack(comment, case=current_case)
        comment += ' Could not restore connectivity - Slack Message sent.'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def ospf_nbr_down(host, origin_ip, yang_message, error, tag, process_number, current_case=None):
    '''
    Once this function is called it has already been determined that a specific OSPF
    process needs to be restarted. Most of the data gathering happened in the napalm-logs
    client. Will attempt to restart the ospf process on the affected device. Last step
    is a check to see if all the neighbors triggered OSPF_NEIGHBOR_UP events.
    :param host: The host from which the event originated
    :param origin_ip: The hosts IP address
    :param yang_message: Contains event specific data, eg. the affected Interface
    :param error: The error: in this case OSPF_NEIGHBOR_DOWN
    :param tag: The tag used in the syslog message that triggered the event
    :param process_number: The OSPF process number
    :param current_case: Optional: the current case. Can be passed if the workflow has started
    earlier (eg. in the client that processes the syslog messages)
    :return: error, tag, a comment, the changes to the config, success (bool)
    '''
    pool = ThreadPool(processes=1)
    comment = 'OSPF neighbor down status on host {0} detected.'.format(host)
    if current_case is None or current_case == 'None':
        current_case = oatsdbhelpers.create_case(error, host, solution='Case created in salt tshoot.ospf_nbr_down.')
    interface = oatsdbhelpers.get_interface(error, yang_message)
    interface_neighbor = oatsdbhelpers.get_interface_neighbor(host, interface, case=current_case)
    n_of_neighbors = len(oatsdbhelpers.get_ospf_neighbors(interface_neighbor, case=current_case))
    oatssalthelpers.ospf_shutdown(interface_neighbor, process_number, case=current_case)
    async_result = pool.apply_async(oatssalthelpers.count_event, ('napalm/syslog/*/OSPF_NEIGHBOR_UP/ospf_nbr_up/*',
                                                                     'OSPF_NEIGHBOR_UP', n_of_neighbors, 30, current_case))
    conf = oatssalthelpers.ospf_noshutdown(interface_neighbor, process_number, case=current_case)
    success = async_result.get()
    if success:
        oatsdbhelpers.update_case(current_case, 'Successfully restarted OSPF process on host {0}.'
                                    .format(interface_neighbor), oatsdbhelpers.Status.DONE.value)
        comment += ' OSPF process restarted successfully.'
    else:
        oatsdbhelpers.update_case(current_case, 'Unable to restart OSPF process on host {0}. Host might be offline.'
                                       '. Technician needed.'.format(interface_neighbor), oatsdbhelpers.Status.ONHOLD.value)
    oatssalthelpers.post_slack(comment, case=current_case)

    ret = {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }

    return ret






