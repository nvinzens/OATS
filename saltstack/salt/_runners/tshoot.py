import pymongo
from pymongo import MongoClient


#Constants
MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb

def ifdown(host, origin_ip, yang_message, error, tag):
    '''
    Execution function to ping and determine if a state should be invoked.
    '''
    comment = None
    conf = 'No changes'
    success = False
    yang_message = YangMessage(yang_message)
    interface = yang_message.getInterface()
    comment = '"Interface down status on host " + host + " detected.'
    interface_neighbor = __get_interface_neighbor(host, interface)

    # check if error is still present, might have been solved already
    if __ping(host, interface_neighbor):
        return {
            'error': error,
            'tag': tag,
            'comment': 'Error not present anymore. Workflow not executed',
            'changes': '',
            'success': True
        }

    neighbors = __get_neighbors(interface_neighbor)
    device_up = __check_device_connectivity(neighbors, interface_neighbor)
    if device_up:
        # cycle affected interface
        __if_shutdown(host, interface)
        conf = __if_noshutdown(host, interface)
        #check if cycle was successful
        success = __ping(host, interface_neighbor)
        if success:
            comment += ("Config for Interface "
                       + interface + " automatically changed from down to up")
            __post_slack(comment)
        else:
            comment = ("Could not fix down status of " + interface + ' on host'
                       + host + ' .')
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        __post_slack('Interface ' + interface + ' on host '
                     + host + ' down. Neighbor ' + interface_neighbor +
                     ' is down.')
        comment = "Could not restore connectivity - Slack Message sent"

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def __post_slack(message):
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def __ping(from_host, to_host):
    ping_result = None
    if from_host == MASTER:
        ping_result = __salt__['salt.execute'](to_host, 'net.ping', {'127.0.0.1'})
        return ping_result[to_host]['result']
    else:
        ping_result = __salt__['salt.execute'](from_host, 'net.ping', {to_host})
    return ping_result[from_host]['out']['success']['results']

def __if_noshutdown(minion, interface):
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def __if_shutdown(minion, interface):
    template_name = 'shutdown_interface'
    template_source = 'interface ' + interface + '\n  shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def __check_device_connectivity(neighbors, host):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :return: if the host is connected to one of his neighbors or the master: True/False
    '''
    # TODO: uncomment for use in real env, in lab env routers are pingable even if the respective interfaces are down
    connected = False
    #for neighbor in neighbors:
    #    connected = __ping(neighbor, host)
    #    if connected:
    #        return connected
    # TODO: evaluate what it means when master is connected, but none of the neighbors
    connected = __ping(MASTER, host)
    return connected

def __get_interface_neighbor(host, interface):
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            return link['neighbor']

def __get_neighbors(host):
    neighbors = []
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and not link['neighbor'] == MASTER:
            neighbors.append(link['neighbor'])
    return neighbors


class YangMessage(object):
    def __init__(self, yang_message):
        self.yang_message = yang_message

    def getInterface(self):
        return self.yang_message['interfaces']['interface'].popitem()[0]
