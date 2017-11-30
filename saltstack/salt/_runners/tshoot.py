import pymongo
from pymongo import MongoClient
import sys
import datetime
import json
import string
import random
from enum import Enum
from oats import oats


# Constants
MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
KEY_LEN = 12


def ifdown(host, origin_ip, yang_message, error, tag):
    '''
    Function that executes a workflow to fix the error that started an ifdown event
    '''
    conf = 'No changes'
    success = False
    interface = __salt__['salt.cmd'](fun='oats.get_interface', yang_message=yang_message)
    comment = 'Interface down status on host ' + host + ' detected. '
    current_case = __salt__['salt.cmd'](fun='oats.create_case', error=error, host=host, status='solution_deployed')
    interface_neighbor = __salt__['salt.cmd'](fun='oats.get_interface_neighbor',host=host, interface=interface, case=current_case)

    neighbors = __salt__['salt.cmd'](fun='oats.get_neighbors', host=interface_neighbor, case=current_case)
    device_up = __salt__['salt.cmd'](fun='oats.check_device_connectivity', neighbors=neighbors, host=interface_neighbor, case=current_case)

    if device_up:
        # cycle affected interface
        __salt__['salt.cmd'](fun='oats.if_shutdown', host=host, interface=interface, case=current_case)
        conf = __salt__['salt.cmd'](fun='oats.if_noshutdown', host=host, interface=interface, case=current_case)
        # check if cycle was successful
        success = __salt__['salt.cmd'](fun='oats.ping', source=host, destination=interface_neighbor, case=current_case)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove? only useful for debugging
            __salt__['salt.cmd'](fun='oats.post_slack', message=comment, case=current_case)
            __salt__['salt.cmd'](fun='oats.close_case', case_id=current_case)
        else:
            __salt__['salt.cmd'](fun='oats.update_case', case_id=current_case, solution=error +
                                                    'could not get resolved. Technician needed.', status=oats.Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            __salt__['salt.cmd'](fun='oats.post_slack', comment=comment, case=current_case)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        __salt__['salt.cmd'](fun='oats.update_case', case_id=current_case, solution ='Device ' + interface_neighbor +
                                                    ' is unreachable. Technician needed.', status=oats.Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor + ' is down.'
        __salt__['salt.cmd'](fun='oats.post_slack', comment=comment, case=current_case)
        comment += ' Could not restore connectivity - Slack Message sent.'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def ospf_nbr_down(host, origin_ip, yang_message, error, tag):
    conf = 'No changes'
    success = False

