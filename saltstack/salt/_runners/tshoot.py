import pymongo
from pymongo import MongoClient
import helpers

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
    yang_message = helpers.YangMessage(yang_message)
    interface = yang_message.getInterface()
    comment = "Interface down status on host " + host + " detected. "
    interface_neighbor = helpers.get_interface_neighbor(host, interface)

    # check if error is still present, might have been solved already
    if helpers.ping(host, interface_neighbor):
        return {
            'error': error,
            'tag': tag,
            'comment': 'Error not present anymore. Workflow not executed',
            'changes': '',
            'success': True
        }

    neighbors = helpers.get_neighbors(interface_neighbor)
    device_up = helpers.check_device_connectivity(neighbors, interface_neighbor)
    if device_up:
        # cycle affected interface
        helpers.if_shutdown(host, interface)
        conf = helpers.if_noshutdown(host, interface)
        # check if cycle was successful
        success = helpers.ping(host, interface_neighbor)
        if success:
            success = True
            comment += ("Config for Interface "
                       + interface + " automatically changed from down to up")
            helpers.post_slack(comment)
        else:
            comment = ("Could not fix down status of " + interface + ' on host'
                       + host + ' .')
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        helpers.post_slack('Interface ' + interface + ' on host '
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
