def __post_slack(message):
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def __ping(minion, destination):
    ping_result = __salt__['salt.execute'](minion, 'net.ping', {destination})
    return ping_result[minion]['out']['success']['results']

def __if_noshutdown(minion, interface):
    template_name = 'noshut_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {template_name, template_source}
    return __salt__['salt.execute'](minion, 'net.load_template', {template_name, template_source})

def __check_device_connectivity(neighbors, host):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :return: if the host is connected to one of his neighbors: True/False
    '''
    connected = False
    for neighbor in neighbors:
        connected = __ping(neighbors, host)
        if connected:
            log.debug("Successful ping from " + neighbor + " to " + host + ". Host is running.")
            return connected

def __get_interface_neighbor(host, interface):
    links =  db.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            return link['neighbor']

def __get_neighbors(host):
    neighbors = []
    links = db.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and (link['neighbor'] != 'master'):
            neighbors.append(link['neighbor'])
    return neighbors

class YangMessage(object):
    def __init__(self, yang_message):
        self.yang_message = yang_message

    def getInterface(self):
        return self.yang_message['interfaces']['interface'].popitem()[0]
