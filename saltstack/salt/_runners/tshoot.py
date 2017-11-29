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

# Global variables
current_case = None

def ifdown(host, origin_ip, yang_message, error, tag):
    '''
    Function that executes a workflow to fix the error that started an ifdown event
    '''
    global current_case
    conf = 'No changes'
    success = False
    yang_message = oats.YangMessage(yang_message)
    interface = yang_message.get_interface()
    comment = 'Interface down status on host ' + host + ' detected. '
    interface_neighbor = oats.get_interface_neighbor(host, interface)
    current_case = oats.create_case(error, host, status='solution_deployed')

    neighbors = oats.get_neighbors(interface_neighbor)
    device_up = oats.check_device_connectivity(neighbors, interface_neighbor)

    if device_up:
        # cycle affected interface
        oats.if_shutdown(host, interface)
        conf = oats.if_noshutdown(host, interface)
        # check if cycle was successful
        success = oats.ping(host, interface_neighbor)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove? only useful for debugging
            oats.post_slack(comment)
            oats.close_case(current_case)
        else:
            oats.update_case(current_case, solution =error + 'could not get resolved. Technician needed.', status=Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            oats.post_slack(comment)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        oats.update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor +' is down.'
        oats.post_slack(comment)
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

