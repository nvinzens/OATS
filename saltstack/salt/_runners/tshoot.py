from oats import oatsdbhelpers
from oatspsql import oatspsql
from oatsinflux import oatsinflux
from oatsnb import oatsnb
import oatssalthelpers
from multiprocessing.pool import ThreadPool
from threading import Thread
import time


def ifdown(host, yang_message, error, tag, current_case=None):
    '''
    Function that gathers data in the network and executes a workflow according to the data.
    Is triggered by the salt system once an INTERFACE_DOWN event arrives in the salt
    event bus. Will try to fix the error or send a notification if it is unable to
    do so.
    :param host: the host that started this workflow.
    :param yang_message: the yang data.
    :param error: the events error.
    :param tag: the events tag.
    :param current_case: the current oats case id.
    :return: error, tag, a comment, configuration changes, success (bool).
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
        oatssalthelpers.if_shutdown(host, interface, case=current_case)
        conf = oatssalthelpers.if_noshutdown(host, interface, case=current_case)
        # check if cycle was successful
        success = oatssalthelpers.ping(host, interface_neighbor, check_connectivity=True, case=current_case)
        if success:
            success = True
            comment += ('Config for Interface `'
                       + interface + '` automatically changed from down to up')
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
    process needs to be restarted. Most of the data gathering happened earlier.
    Will attempt to restart the ospf process on the affected device. Last step
    is a check to see if all the neighbors triggered OSPF_NEIGHBOR_UP events.
    :param host: the host that started this workflow.
    :param yang_message: the yang data.
    :param error: the events error.
    :param tag: the events tag.
    :param current_case: the current oats case id.
    :return: error, tag, a comment, configuration changes, the slack post satus (bool), success (bool).
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
    '''
    Function that loads a policy onto a device affected by a high amount of discarded packets.
    The policy throttles the traffic from one IP to another with a certain port number.
    The source-, destination-IP and port number are gathered by evaluating netflow data.
    After a certain amount of time the policy is removed again.
    :param data: contains the affected interface and the value of discarded packets.
    :param host: the affected host.
    :param timestamp: the timestamp of the event.
    :param current_case: the current oats case-id
    :return: error, comment, changes, slack-post-status(bool), success(bool)
    '''
    if current_case is None or current_case == 'None':
        current_case = oatspsql.create_case("OUT_DISCARDS_EXCEEDED", host, solution='Case created in salt: `tshoot.out_discards_exceeded`.')

    src_flow = None
    # timeout while loop after 20secs
    timeout = time.time() + 60
    comment = ''
    while src_flow is None:
        flows = oatsinflux.get_type_data('netflow', timestamp, 'netflow/*/data', 30, host=host)
        src_flow = oatssalthelpers.get_src_flow(flows, 15000)
        time.sleep(1)
        if time.time() > timeout:
            break
    if src_flow is not None:
        dst_flow_port = src_flow['11']
        interface = data['name']
        src_ip_address = src_flow['8']
        dst_ip_address = src_flow['12']
        oatspsql.update_case(current_case,
                             solution='Found responsible flow: src_ip = `{0}`, dst_ip = `{1}`, port_number = `{2}`'
                             .format(src_ip_address, dst_ip_address, dst_flow_port))
        minion = oatsnb.get_hostname(host)
        oatssalthelpers.apply_policy(minion, 8000, interface, src_ip_address, dst_ip_address, dst_flow_port)
        oatssalthelpers.remove_policy(minion, interface, src_ip_address, dst_ip_address, dst_flow_port)
        comment = "Discarded packets on host {0} on egress interface `{1}` exceeded threshhold. " \
                  "Destination port of traffic: `{2}`.\n".format(host, data['name'], dst_flow_port)
        comment+= "Applied traffic throttlinc policy for 120 seconds.\n"
    else:
        comment += 'Could not determine source of traffic, possible DDoS attack detected' \
                   ' because traffic source port is `port 0`.'

    slack_status = oatssalthelpers.post_slack(comment, case=current_case)

    ret = {
        'error': 'OUT_DISCARDS',
        'comment': comment,
        'changes': 'conf',
        'slack-post-status:': slack_status,
        'success': bool(dst_flow_port)
    }
    return ret


def port_flap(host, yang_message, error, tag, current_case=None):
    '''
    Workflow for fixing port flapping, similarly to the ifdown function.
    :param host: the from which the event originated.
    :param yang_message: the yang data.
    :param error: the events error.
    :param tag: the events tag.
    :param current_case: the current oats case id.
    :return: error, tag, comment, success (bool)
    '''
    conf = 'No changes'
    success = False
    interface = oatsdbhelpers.get_interface(error, yang_message)
    comment = 'Port Flapping on  ' + host + ' detected. '
    if current_case is None or current_case == 'None':
        current_case = oatspsql.create_case(error, host, solution='Case created in salt: `tshoot.port_flap`.')
    interface_neighbor = oatsnb.get_interface_neighbor(host, interface, case=current_case)

    #neighbors = oatsnb.get_neighbors(interface_neighbor, case=current_case)
    #device_up = oatssalthelpers.check_device_connectivity(neighbors, interface_neighbor, case=current_case)

    oatssalthelpers.if_shutdown(host, interface, case=current_case)
    conf = oatssalthelpers.if_noshutdown(host, interface, case=current_case)
    success = oatssalthelpers.ping(host, interface_neighbor, check_connectivity=True, case=current_case)
    if success:
        success = True
        comment += ('Resolved Port Flapping on Interface`' + interface + '`.')
        oatssalthelpers.post_slack(comment, case=current_case)
        oatspsql.close_case(current_case)
    else:
        oatspsql.update_case(current_case, solution='Port flapping could not get resolved. Technician needed.', status=oatspsql.Status.ONHOLD.value)
        comment = ('Could not fix port flapping status of `' + interface + '` on host'
                    + host + ' .')
        oatssalthelpers.post_slack(comment, case=current_case)
        success = False
        oatspsql.update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=oatspsql.Status.ONHOLD.value)
        oatssalthelpers.post_slack(comment, case=current_case)

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }






