def post_slack(message):
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def ping(from_host, to_host):
    ping_result = None
    if from_host == MASTER:
        ping_result = __salt__['salt.execute'](to_host, 'net.ping', {'127.0.0.1'})
        return ping_result[to_host]['result']
    else:
        ping_result = __salt__['salt.execute'](from_host, 'net.ping', {to_host})
    return ping_result[from_host]['out']['success']['results']

def if_noshutdown(minion, interface):
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def if_shutdown(minion, interface):
    template_name = 'shutdown_interface'
    template_source = 'interface ' + interface + '\n  shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def check_device_connectivity(neighbors, host):
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

def get_interface_neighbor(host, interface):
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            return link['neighbor']

def get_neighbors(host):
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