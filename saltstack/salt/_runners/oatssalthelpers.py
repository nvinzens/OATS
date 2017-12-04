import oats.oats
import datetime
import time
import string
import random
from enum import Enum
import salt.config
import salt.utils.event


# TODO: add behaviour for calling methods without current_case id
# Constants
MASTER = 'master'
MASTER_IP ='10.20.1.10'


def post_slack(message, case=None):
    '''
    Posts a message to the predefined oats slack channel. The message contains the message param
    + all of the involved solution steps for the current case.
    :param message: the message to post to the channel.
    :param case: case-id for updating the current case
    '''
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    oats.update_case(case, solution='Workflow finished. Case-ID: ' + case, status='technician_called')
    solutions = oats.get_solutions_as_string(case)
    message += "\nExecuted workflow:\n" + solutions
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def ping(source, destination, case=None, check_connectivity=False):
    '''
    Executes a ping from one host to another using the salt-api. If from_host equals 'master' it will
    try to establish a connection from the master to a host to simulate a ping (needed because in current
    lab environment pings don't behave as they would in a real environment).
    :param source: The ping source
    :param destination: The ping destination
    :param case: case-id for updating the current case
    :return: The results of the ping. Will be empty if the ping wasn't successful.
    '''
    if check_connectivity:
        vrf_dest = {'destination': get_vrf_ip(destination), 'vrf': 'mgmt'}
        ping_result = __salt__['salt.execute'](source, 'net.ping', kwarg=vrf_dest)
        oats.update_case(case, solution='Ping from ' + source + ' to ' + destination + '. Result: ' + str(
            bool(ping_result)))
        return ping_result[source]['out']['success']['results']
    else:
        ping_result = __salt__['salt.execute'](source, 'net.ping', {destination})
        oats.update_case(case, solution ='Ping from ' + source + ' to ' + destination + '. Result: ' + str(bool(ping_result)) + ' //always true in lab env')
    return ping_result[source]['out']['success']['results']


def if_noshutdown(host, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
    '''
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name, 'template_source': template_source}
    oats.update_case(case, solution ='Trying to  apply no shutdown to interface ' + interface + '.')
    return __salt__['salt.execute'](host, 'net.load_template', kwarg=config)


def if_shutdown(minion, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
        '''
    template_name = 'shutdown_interface'
    template_source = 'interface {0}\n  shutdown\nend'.format(interface)
    config = {'template_name': template_name,'template_source': template_source}
    oats.update_case(case, solution='Trying to apply shutdown to interface {0}.'.format(interface))
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)


def ospf_shutdown(minion, process_number, case=None):
    template_name = 'shutdown_ospf'
    template_source = 'router ospf {0}\n  shutdown\nend'.format(process_number)
    config = {'template_name': template_name, 'template_source': template_source}
    oats.update_case(case, solution='Trying to apply shutdown to OSPF process {0}.'.format(process_number))
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def ospf_noshutdown(minion, process_number, case=None):
    template_name = 'shutdown_ospf'
    template_source = 'router ospf {0}\n  no shutdown\nend'.format(process_number)
    config = {'template_name': template_name, 'template_source': template_source}
    oats.update_case(case, solution='Trying to apply no shutdown to OSPF process {0}.'.format(process_number))
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def check_device_connectivity(neighbors, host, case=None):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :param case: case-id for updating the current case
    :return: if the host is connected to one of his neighbors or the master (bool)
    '''
    # TODO: uncomment for use in real env, in lab env routers are pingable even if the respective interfaces are down
    connected = False
    for neighbor in neighbors:
        connected = ping(neighbor, host, check_connectivity=True)
        if connected:
            oats.update_case(case, solution='Checking connectivity from {0} to {1}. Result: {2}'.format(neighbor, host, str(bool(connected))))
            return connected
    return connected


def get_interface(error, yang_message):
    # method to get interface can be different for different errors
    if error == 'INTERFACE_DOWN':
        return yang_message['interfaces']['interface'].popitem()[0]
    if error == 'OSPF_NEIGHBOR_DOWN':
        interfaces = yang_message['network-instances']['network-instance']['global']['protocols']['protocol']['ospf']['ospfv2']['areas']['area']['area']
        return interfaces['interfaces']['interface'].popitem()[0]


def wait_for_event(tag, amount, wait=10, case=None):
    opts = salt.config.client_config('/etc/salt/master')

    event = salt.utils.event.get_event(
        'master',
        sock_dir=opts['sock_dir'],
        transport=opts['transport'],
        opts=opts)
    counter = 0
    timeout = time.time() + wait
    oats.update_case(case, solution='Waiting for {0} amount of {1} events'.format(amount, tag))
    while time.time() < timeout:
        if event.get_event(wait=wait, tag=tag):
            counter += 1
    success = counter >= amount
    oats.update_case(case, solution='Result: {0} events. Wait success: {1}'.format(counter, success))
    return success
