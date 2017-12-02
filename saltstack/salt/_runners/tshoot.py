import pymongo
from pymongo import MongoClient
import sys
import datetime
import json
import string
import random
import time
from enum import Enum
import salt.config
import salt.utils.event
import oats


# Constants
MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
KEY_LEN = 12
OSPF_NEIGHBOR_DOWN = 'napam/syslog/*/OSPF_NEIGHBOR_DOWN/dead_timer_expired/disabled*'
INTERFACE_CHANGED_DOWN = 'napalm/syslog/*/INTERFACE_CHANGED/down/*'
# TODO: add new events dinamically
EVENT_TAGS = [
    OSPF_NEIGHBOR_DOWN,
    INTERFACE_CHANGED_DOWN
]


def ifdown(host, origin_ip, yang_message, error, tag, interface=None, current_case=None):
    '''
    Function that executes a workflow to fix the error that started an ifdown event
    '''
    # TODO: add optional interface param
    conf = 'No changes'
    success = False
    interface = oats.get_interface(yang_message)
    comment = 'Interface down status on host ' + host + ' detected. '
    if current_case is None:
        current_case = oats.create_case(error, host, status='solution_deployed')
    interface_neighbor = oats.get_interface_neighbor(host, interface, case=current_case)

    neighbors = oats.get_neighbors(interface_neighbor, case=current_case)
    device_up = oats.check_device_connectivity(neighbors, interface_neighbor, case=current_case)

    if device_up:
        # cycle affected interface
        oats.if_shutdown(host, interface, case=current_case)
        conf = oats.if_noshutdown(host, interface, case=current_case)
        # check if cycle was successful
        success = oats.ping(host, interface_neighbor,check_connectivity=True, case=current_case)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove? only useful for debugging
            oats.post_slack(comment, case=current_case)
            oats.close_case(current_case)
        else:
            oats.update_case(current_case, solution=error + 'could not get resolved. Technician needed.', status=oats.Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            oats.post_slack(comment, case=current_case)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        oats.update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=oats.Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor + ' is down.'
        oats.post_slack(comment, case=current_case)
        comment += ' Could not restore connectivity - Slack Message sent.'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def ospf_nbr_down(host, origin_ip, yang_message, error, tag, process_number, collect_for=10, current_case=None):

    conf = 'No changes'
    success = False
    comment = 'OSPF neighbor down status on host {0} detected. Collecting OSPF events for {1} seconds.'.format(host, collect_for)
    counter = 0
    if current_case is None:
        current_case = oats.create_case(error, host, status='solution_deployed')
    # listener for events
    ret = {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }

    return ret






