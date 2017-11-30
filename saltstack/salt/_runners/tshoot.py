import pymongo
from pymongo import MongoClient
import sys
import datetime
import json
import string
import random
from enum import Enum
import oats

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
    interface = __utils__['oats.get_interface'](yang_message)
    comment = 'Interface down status on host ' + host + ' detected. '
    current_case = __utils__['oats.create_case'](error, host, status='solution_deployed')
    interface_neighbor = __utils__['oats.get_interface_neighbor'](host, interface, case=current_case)

    neighbors = __utils__['oats.get_neighbors'](interface_neighbor, case=current_case)
    device_up = __utils__['oats.check_device_connectivity'](neighbors, interface_neighbor, case=current_case)

    if device_up:
        # cycle affected interface
        __utils__['oats.if_shutdown'](host, interface, case=current_case)
        conf = __utils__['oats.if_noshutdown'](host, interface, case=current_case)
        # check if cycle was successful
        success = __utils__['oats.ping'](host, interface_neighbor, case=current_case)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove? only useful for debugging
            __utils__['oats.post_slack'](comment, case=current_case)
            __utils__['oats.close_case'](current_case)
        else:
            __utils__['oats.update_case'](current_case, solution =error + 'could not get resolved. Technician needed.', status=Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            __utils__['oats.post_slack'](comment, case=current_case)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        __utils__['oats.update_case'](current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor +' is down.'
        __utils__['oats.post_slack'](comment, case=current_case)
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

