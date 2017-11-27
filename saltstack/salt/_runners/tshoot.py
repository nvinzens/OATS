import pymongo
from pymongo import MongoClient
import sys
import datetime
import json
import string
import random

# Constants
MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
KEY_LEN = 12

# Global variables
current_case = None

class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'

def ifdown(host, origin_ip, yang_message, error, tag):
    '''
    Function that executes a workflow to fix the error that started an ifdown event
    '''
    global current_case
    conf = 'No changes'
    success = False
    yang_message = YangMessage(yang_message)
    interface = yang_message.get_interface()
    comment = 'Interface down status on host ' + host + ' detected. '
    interface_neighbor = _get_interface_neighbor(host, interface)
    current_case = create_case(error, host, status='solution_deployed')

    # check if error is still present, might have been solved already
    if _ping(host, interface_neighbor):
        close_case(current_case)
        return {
            'error': error,
            'tag': tag,
            'comment': 'Error not present anymore. Workflow not executed',
            'changes': conf,
            'success': True
        }

    neighbors = _get_neighbors(interface_neighbor)
    device_up = _check_device_connectivity(neighbors, interface_neighbor)

    if device_up:
        # cycle affected interface
        _if_shutdown(host, interface)
        conf = _if_noshutdown(host, interface)
        # check if cycle was successful
        # uncomment for use in real env
        #success = _ping(host, interface_neighbor)
        success = _ping(MASTER, interface_neighbor)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            # TODO: remove? only useful for debugging
            _post_slack(comment)
            close_case(current_case)
        else:
            update_case(current_case, solution =error + 'could not get resolved. Technician needed.', status=Status.ONHOLD.value)
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            _post_slack(comment)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        update_case(current_case, solution ='Device ' + interface_neighbor + ' is unreachable. Technician needed.', status=Status.ONHOLD.value)
        comment += 'Interface ' + interface + ' on host '+ host + ' down. Neighbor ' + interface_neighbor +' is down.'
        _post_slack(comment)
        comment += ' Could not restore connectivity - Slack Message sent.'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def create_case(error, host, solution=None, description=None, status=Status.NEW.value):
    '''
    Creates a new case in the oatsdb, Code dependant on type of database
    Calls the function key_gen to creat a case ID
    :param Error: The Error which lead to this case
    :param Host: The Origin Host of the Error
    :param Solution: The Workflow Steps which are already done, optional
    :param Description: Short Description of the Problem, optional
    :param Status: How far in the resolving of the Problem the case is, default Value is 'new'
    :return: ID of the Case in the Database
    '''
    event = error
    device = host
    if not solution:
        solution = 'Case created without initial automated solution'
    if not description:
        description = event

    case_id = _key_gen()

    new_case = {
        'case_nr': case_id,
        'Event': event,
        'Description': description,
        'Status': status,
        'created': datetime.datetime.utcnow(),
        'last_updated': datetime.datetime.utcnow(),
        'technician': 'not_called',
        'Sender_Device': device,
        'Solution': [solution]
    }

    try:
        DB.cases.insert_one(new_case)
        print '\nCase inserted successfully\n'

    except Exception, e:
        print str(e)

    return case_id


def update_case(case_id, solution, status=None):
    #TODO: validate if status ist in list of states else throw exception
    '''
    Updates a case in the oatsdb with the steps that have been completed, Code dependant on type of database
    :param case_id: ID of the Case in the Database
    :param Solution: The Workflow Steps which are already done
    :param Status: How far in the resolving of the Problem the case is, optional
    :return: ID of the Case in the Database
    '''
    if status:
        DB.cases.update_one(
            {'case_nr': case_id},
            {
                '$set': {
                    'Status': status,
                    'last_updated': datetime.datetime.utcnow(),
                },
                '$push':{
                    'Solution': solution
                }
            }
        )
    else:
        DB.cases.update_one(
            {'case_nr': case_id},
            {
                '$set': {
                    'last_updated': datetime.datetime.utcnow(),
                },
                '$push': {
                    'Solution': solution
                }
            }
        )
    return case_id


def close_case(case_id):
    '''
    Changes the state of a case in the database to resolved, Code dependant on type of database
    :param case_id: ID of the Case in the Database
    :return: ID of the Case in the Database
    '''
    DB.cases.update_one(
        {'case_nr': case_id},
        {
            '$set': {
                'last_updated': datetime.datetime.utcnow(),
                'Status': Status.DONE.value,
            }
        }
    )
    return case_id


def take_case(case_id, technician):
    '''

    :param case_id: ID of the Case in the Database
    :param Solution: The Workflow Steps which are already done
    :param Status: How far in the resolving of the Problem the case is, optional
    :return: ID of the Case in the Database
    '''
    DB.cases.update_one(
        {'case_nr': case_id},
        {
            '$set': {
                'last_updated': datetime.datetime.utcnow(),
                'Status': Status.TECH.value,
                'technician': technician,
            }
        }
    )
    return case_id


def get_solutions_as_string(case_id):
    solution = DB.cases.find({'case_nr': case_id})
    solution_list = []
    for sol in solution:
        for solprint in sol['Solution']:
            solution_list.append('\n')
            solution_list.append('- ' + solprint)
    solution_strings = ''.join(solution_list)

    return solution_strings


def _post_slack(message):
    '''
    Posts a message to the predefined oats slack channel. The message contains the message param
    + all of the involved solution steps for the current case.
    :param message: the message to post to the channel.
    '''
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    update_case(current_case, solution='Workflow finished. Case-ID: ' + current_case, status='technician_called')
    solutions = get_solutions_as_string(current_case)
    message += "\nExecuted workflow:\n" + solutions
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def _ping(from_host, to_host):
    '''
    Executes a ping from one host to another using the salt-api. If from_host equals 'master' it will
    try to establish a connection from the master to a host to simulate a ping (needed because in current
    lab environment pings don't behave as they would in a real environment).
    :param from_host: The ping source
    :param to_host: The ping destination
    :return: The results of the ping. Will be empty if the ping wasn't successful.
    '''
    if from_host == MASTER:
        ping_result = __salt__['salt.execute'](to_host, 'net.ping', {'127.0.0.1'})
        update_case(current_case, solution='Ping from ' + from_host + ' to ' + to_host + '. Result: ' + str(
            bool(ping_result)))
        return ping_result[to_host]['result']
    else:
        ping_result = __salt__['salt.execute'](from_host, 'net.ping', {to_host})
        update_case(current_case, solution ='Ping from ' + from_host + ' to ' + to_host + '. Result: ' + str(bool(ping_result)) + ' //always true in lab env')
    return ping_result[from_host]['out']['success']['results']


def _if_noshutdown(host, interface):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
    '''
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case(current_case, solution ='Trying to  apply no shutdown to interface ' + interface + '.')
    return __salt__['salt.execute'](host, 'net.load_template', kwarg=config)


def _if_shutdown(minion, interface):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
        '''
    template_name = 'shutdown_interface'
    template_source = 'interface ' + interface + '\n  shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case(current_case, solution='Trying to apply shutdown to interface ' + interface + '.')
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)


def _check_device_connectivity(neighbors, host):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :return: if the host is connected to one of his neighbors or the master (bool)
    '''
    # TODO: uncomment for use in real env, in lab env routers are pingable even if the respective interfaces are down
    connected = False
    #for neighbor in neighbors:
    #    connected = __ping(neighbor, host)
    #    if connected:
    #        return connected
    # TODO: evaluate what it means when master is connected, but none of the neighbors
    connected = _ping(MASTER, host)
    update_case(current_case, solution ='Checking connectivity to ' + host + '. Result: ' + str(bool(connected)))
    return connected


def _get_interface_neighbor(host, interface):
    '''
    Get the neighbor of the specified host that is connected to it via the specified interface (via oats db).
    :param host: The host
    :param interface: The interface
    :return: The interface neighbor.
    '''
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            update_case(current_case, {'TODO DICT': 'FOR SOLUTION'})
            return link['neighbor']


def _get_neighbors(host):
    '''
    Get all the neighbors of the host (via oats db).
    :param host: The host
    :return: All the hosts neighbors (as list)
    '''
    neighbors = []
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and not link['neighbor'] == MASTER:
            neighbors.append(link['neighbor'])
    update_case(current_case, 'Get neighbors of ' + host + ' from oats database.')
    return neighbors


def _base_str():
    return string.letters+string.digits


def _key_gen():
    keylist = [random.choice(_base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)


class YangMessage(object):
    def __init__(self, yang_message):
        self.yang_message = yang_message

    def get_interface(self):
        return self.yang_message['interfaces']['interface'].popitem()[0]
