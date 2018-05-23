from oats import oatsdbhelpers
from oatspsql import oatspsql
from oatsinflux import oatsinflux
from oatsnb import oatsnb
import oatssalthelpers
from multiprocessing.pool import ThreadPool
import time


def ifdown(host, yang_message, error, tag, current_case=None):
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
        current_case = oatspsql.create_case(error, host, solution='Case created in salt: `tshoot.ifdown`.')
    interface_neighbor = oatsnb.get_interface_neighbor(host, interface, case=current_case)

    neighbors = oatsnb.get_neighbors(interface_neighbor, case=current_case)
    device_up = oatssalthelpers.check_device_connectivity(neighbors, interface_neighbor, case=current_case)

    if device_up:
        # cycle affected interface
        timeout = time.time() + 10
        up_counter = 0
        down_counter = 0
        while True:
            if oatssalthelpers.wait_for_event('syslog/*/INTERFACE_CHANGED/up', 3, ):
                up_counter += 1
            if oatssalthelpers.wait_for_event('syslog/*/INTERFACE_CHANGED/down', 3):
                down_counter += 1
            if time.time() > timeout:
                break
        if up_counter >= 2 and down_counter >= 2:
            error = 'PORT_FLAPPING'
            oatspsql.update_case(current_case, solution='Port Flapping detected. Trying to fix...')
        oatssalthelpers.if_shutdown(host, interface, case=current_case)
        conf = oatssalthelpers.if_noshutdown(host, interface, case=current_case)
        # check if cycle was successful
        success = oatssalthelpers.ping(host, interface_neighbor, check_connectivity=True, case=current_case)
        if success:
            success = True
            comment += ('Problem on Interface `'
                       + interface + '` automatically resolved.')
            # TODO: remove, only useful for debugging
            oatssalthelpers.post_slack(comment, case=current_case)
            oatspsql.close_case(current_case)
        else:
            oatspsql.update_case(current_case, solution=error + 'could not get resolved. Technician needed.', status=oatspsql.Status.ONHOLD.value)
            comment = ('Could not fix down status of `' + interface + '` on host'
                       + host + ' .')
            oatssalthelpers.post_slack(comment, case=current_case)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        oatspsql.update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=oatspsql.Status.ONHOLD.value)
        comment += 'Interface `' + interface + '` on host '+ host + ' down. Neighbor ' + interface_neighbor + ' is down.'
        oatssalthelpers.post_slack(comment, case=current_case)
        comment += ' Could not restore connectivity - Slack Message sent.'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def ospf_nbr_down(host, yang_message, error, tag, process_number, current_case):
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
        current_case = oatspsql.create_case(error, host, solution='Case created in salt: `tshoot.ospf_nbr_down`.')
    interface = oatsdbhelpers.get_interface(error, yang_message)
    interface_neighbor = oatsnb.get_interface_neighbor(host, interface, case=current_case)
    n_of_neighbors = len(oatsnb.get_ospf_neighbors(interface_neighbor, case=current_case))
    oatssalthelpers.ospf_shutdown(interface_neighbor, process_number, case=current_case)
    async_result = pool.apply_async(
        oatssalthelpers.wait_for_event, ('syslog/*/OSPF_NEIGHBOR_UP/ospf_nbrs_up', 120, current_case)
    )
    conf = oatssalthelpers.ospf_noshutdown(interface_neighbor, process_number, case=current_case)
    success = async_result.get()
    if success:
        oatspsql.update_case(current_case, 'Successfully restarted OSPF process on host {0}.'
                                    .format(interface_neighbor), oatspsql.Status.DONE.value)
        comment += ' OSPF process restarted successfully.'
    else:
        oatspsql.update_case(current_case, 'Unable to restart OSPF process on host {0}. Host might be offline.'
                                       '. Technician needed.'.format(interface_neighbor), oatspsql.Status.ONHOLD.value)
    slack_post = oatssalthelpers.post_slack(comment, case=current_case)

    ret = {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'slack-post-status:': slack_post,
        'success': success
    }

    return ret


def out_discards_exceeded(data, host, timestamp, current_case):
    if current_case is None or current_case == 'None':
        current_case = oatspsql.create_case("OUT_DISCARDS_EXCEEDED", host, solution='Case created in salt: `tshoot.out_discards_exceeded`.')

    # TODO: determine source of traffic (async)
    #flow_data = oatssalthelpers.wait_for_event("netflow/*/high_traffic", 20, current_case)['data']['data']
    #flow_host = flow_data['AgentID']
    #flow_source_port = oatssalthelpers.get_netflow_data_from_type_field(flow_data['DataSets'], 7)
    # src_port = 7, in_bytes = 1

    src_flow = None
    src_flow_port = 0
    # timeout while loop after 20secs
    timeout = time.time() + 60
    while src_flow is None:
        flows = oatsinflux.get_type_data('netflow', timestamp, 'netflow/*/data', 30, host=host)
        src_flow = oatssalthelpers.get_src_flow(flows, 15000)
        time.sleep(1)
        if time.time() > timeout:
            break

    if src_flow_port is 0:
        src_flow_port = src_flow['7']

    comment = "Discarded pakets on host {0} on egress interface `{1}` exceeds threshhold. " \
              "Source port of traffic: `{2}`.\n".format(host, data['name'], src_flow_port)
    if src_flow_port == 0:
        comment += 'Could not determine source of traffic, possible DDoS attack detected' \
                   ' because traffic source port is `port 0`.'

    slack_status = oatssalthelpers.post_slack(comment, case=current_case)

    ret = {
        'error': 'OUT_DISCARDS',
        'comment': comment,
        'changes': 'conf',
        'slack-post-status:': slack_status,
        'success': bool(src_flow_port)
    }
    return ret







