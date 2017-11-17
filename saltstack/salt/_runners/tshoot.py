

def ifdown(origin_interface, origin_host):
    '''
    Execution function to ping and determine if a state should be invoked.
    '''
    comment = ''
    destination = '172.16.12.1'
    success = False
    conf = ''
    pingable = __ping('R11', destination)
    if pingable:
        conf = __if_noshutdown(origin_interface)
        success = True
        comment = ("Config on " + origin_host + " for Interface " + origin_interface
                     + " changed from down to up")
        __post_slack(comment)
    if not pingable:
        success = False
        __post_slack('Interface ' + origin_interface + ' on host '
                   + origin_host + ' down')
        comment = "Could not restore connectivity - Slack Message sent"

    return {
        'comment': comment,
        'changes': conf,
        'success': success
    }


def __post_slack(message):
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    __salt__['salt.cmd'](fun='slack.post_message', masterchannel=channel, message=message, from_name=user, api_key=api_key)


def __ping(minion, destination):
    ping_result = __salt__['salt.execute'](minion, 'net.ping', {destination})
    print (ping_result)
    return ping_result[minion]['out']['success']['results']

def __if_noshutdown(minion, interface):
    interface_name = interface
    template_name = '/srv/saltstack/template/noshut_interface.jinja'
    return __salt__['salt.execute'](minion, 'net.load_template', {'template_name': template_name, 'interface_name': interface_name})