
def ifdown(minion, origin_ip, yang_message, error, tag):
    '''
    Execution function to ping and determine if a state should be invoked.
    '''
    comment = ''
    yang_message = YangMessage(yang_message)
    interface = yang_message.getInterface()
    destination = '172.16.12.1'
    success = False
    conf = ''
    pingable = __ping('R11', destination)
    if pingable:
        conf = __if_noshutdown(minion, interface)
        success = True
        comment = ("Config on " + minion + " for Interface " + interface
                     + " changed from down to up")
        __post_slack(comment)
    if not pingable:
        success = False
        __post_slack('Interface ' + interface + ' on host '
                   + minion + ' down')
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
            return connected

class YangMessage(object):
    def __init__(self, yang_message):
        self.yang_message = yang_message

    def getInterface(self):
        return self.yang_message['interfaces']['interface'].popitem()[0]
