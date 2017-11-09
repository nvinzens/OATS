import json


def workflow(origin_interface, origin_host):
    '''
    Execution function to ping and determine if a state should be invoked.
    '''
    destination = '192.168.50.12'
    comment = 'Connectivity restored'
    ping_result = __salt__['net.ping'](destination)
    # determine if should run the state
    successful_ping = ping_result['out']['success']['results']
    if not successful_ping:
        __post_slack_ifdown(origin_interface, origin_host)
        comment = "Could not restore connectivity - Slack Message sent"

    return {
        'comment': comment,
        'result': None,
        'id': 'dummy',
        'changes': {},
        'ping result': ping_result['out']['success']['packet_loss'],
        'ping failed:': successful_ping
    }


def __post_slack_ifdown(origin_interface, origin_host):
    channel = '#testing'
    message = ('Interface ' + origin_interface + 'on host '
    + origin_host + ' down')
    user = 'Interface Shutdown Reactor'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    __salt__['slack.post_message'](channel=channel, message=message, from_name=user, api_key=api_key,)
