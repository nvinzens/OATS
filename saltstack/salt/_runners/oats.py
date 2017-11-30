import sys
import pymongo
from pymongo import MongoClient
import datetime
import json
import string
import random
from enum import Enum

# TODO: add behaviour for calling methods without current_case id
# Constants
MASTER = 'master'
MASTER_IP ='10.20.1.10'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
KEY_LEN = 12

class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'

def base_str():
    return string.letters+string.digits

def key_gen():
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)

def create_case(error, host, solution=None, description=None, status=Status.NEW.value, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.cases
    event = error
    device = host
    if not solution:
        solution = 'Case created without automated Solution'
    if not description:
        description = event

    case_id = key_gen()

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
        db_cases.insert_one(new_case)
        print '\nCase inserted successfully\n'

    except Exception, e:
        print str(e)

    return case_id

def update_case(case_id, solution, status=None, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.cases
    if status == Status.ONHOLD.value or status==Status.WORKING.value or status==Status.TECH.value or status==Status.DONE.value :
        db_cases.update_one(
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
        db_cases.update_one(
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

def close_case(case_id, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.cases
    db_cases.update_one(
        {'case_nr': case_id},
        {
            '$set': {
                'last_updated': datetime.datetime.utcnow(),
                'Status': Status.DONE.value,
            }
        }
    )
    return case_id

def take_case(case_id, technician, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.cases
    db_cases.update_one(
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

def get_solutions_as_string(case_id, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.cases
    solution = db_cases.find({'case_nr': case_id})
    solution_list = []
    for sol in solution:
        for solprint in sol['Solution']:
            solution_list.append('\n')
            solution_list.append(solprint)
    solution_strings = ''.join(solution_list)

    return solution_strings

def post_slack(message, case=None):
    '''
    Posts a message to the predefined oats slack channel. The message contains the message param
    + all of the involved solution steps for the current case.
    :param message: the message to post to the channel.
    :param case: case-id for updating the current case
    '''
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    update_case(case, solution='Workflow finished. Case-ID: ' + case, status='technician_called')
    solutions = get_solutions_as_string(case)
    message += "\nExecuted workflow:\n" + solutions
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def ping(source, destination, case=None, check_connectivity=False):
    '''
    Executes a ping from one host to another using the salt-api. If from_host equals 'master' it will
    try to establish a connection from the master to a host to simulate a ping (needed because in current
    lab environment pings don't behave as they would in a real environment).
    :param source: The ping source
    :param destination: The ping destination
    :param case: case-id for updating the current case
    :return: The results of the ping. Will be empty if the ping wasn't successful.
    '''
    if check_connectivity:
        ping_result = __salt__['salt.execute'](source, 'net.ping', {get_vrf_ip(destination)}, vrf='mgmt')
        update_case(case, solution='Ping from ' + source + ' to ' + destination + '. Result: ' + str(
            bool(ping_result)))
        return ping_result[get_vrf_ip(source)]['out']['success']['results']
    else:
        ping_result = __salt__['salt.execute'](source, 'net.ping', {destination})
        update_case(case, solution ='Ping from ' + source + ' to ' + destination + '. Result: ' + str(bool(ping_result)) + ' //always true in lab env')
    return ping_result[source]['out']['success']['results']


def get_vrf_ip(host, test=False):
    if test:
        db_network = DB.test
    else:
        db_network = DB.network
    links = db_network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] == MASTER:
            return link['ip']

def if_noshutdown(host, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
    '''
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case(case, solution ='Trying to  apply no shutdown to interface ' + interface + '.')
    return __salt__['salt.execute'](host, 'net.load_template', kwarg=config)


def if_shutdown(minion, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
        '''
    template_name = 'shutdown_interface'
    template_source = 'interface ' + interface + '\n  shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case(case, solution='Trying to apply shutdown to interface ' + interface + '.')
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)


def check_device_connectivity(neighbors, host, case=None):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :param case: case-id for updating the current case
    :return: if the host is connected to one of his neighbors or the master (bool)
    '''
    # TODO: uncomment for use in real env, in lab env routers are pingable even if the respective interfaces are down
    connected = False
    for neighbor in neighbors:
        connected = ping(neighbor, host, check_connectivity=True)
        if connected:
            return connected
    # TODO: evaluate what it means when master is connected, but none of the neighbors
    connected = ping(MASTER_IP, host)
    update_case(case, solution ='Checking connectivity to ' + host + '. Result: ' + str(bool(connected)))
    return connected


def get_interface_neighbor(host, interface, case=None, test=False):
    '''
    Get the neighbor of the specified host that is connected to it via the specified interface (via oats db).
    :param host: The host
    :param interface: The interface
    :param case: case-id for updating the current case
    :return: The interface neighbor.
    '''
    if test:
        db_network = DB.test
    else:
        db_network = DB.network
    links = db_network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            update_case(case, 'Get interface neighbor of interface ' + interface + ' on host ' + host + '.')
            return link['neighbor']


def get_neighbors(host, case=None, test=False):
    '''
    Get all the neighbors of the host (via oats db).
    :param host: The host
    :param case: case-id for updating the current case
    :return: All the hosts neighbors (as list)
    '''
    if test:
        db_network = DB.test
    else:
        db_network = DB.network
    neighbors = []
    links = db_network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and not link['neighbor'] == MASTER:
            neighbors.append(link['neighbor'])
    update_case(case, 'Get neighbors of ' + host + ' from oats database.')
    return neighbors

def show_cases_of_last_day(test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.network
    last_day = datetime.now() - timedelta(hours=24)
    cases = db_cases.find({'last_updated':{'$gt':last_day}})
    print '\nList of cases updated in the last 24 hours:\n'
    for cas in cases:
        print 'Case Nr: ' + cas['case_nr']
        print 'Case Event: ' + cas['Event']
        print 'Case Description: ' + cas['Description']
        print 'Case Status: ' + cas['Status']

def numb_open_cases(status=None, test=False):
    if test:
        db_cases = DB.test
    else:
        db_cases = DB.network
    new_cases = db_cases.find({'Status': 'new'}).count()
    auto_cases = db_cases.find({'Status': 'solution_deployed'}).count()
    techreq_cases = db_cases.find({'Status': 'technician_needed'}).count()
    tech_cases = db_cases.find({'Status': 'technician_on_case'}).count()

    open_cases = new_cases + auto_cases + techreq_cases + tech_cases

    if status == Status.NEW.value:
        print '\nNumber of Cases with Status new: ' + str(new_cases)
    elif status == Status.WORKING.value:
        print '\nNumber of Cases with Status "solution_deployed": ' + str(auto_cases)

    elif status == Status.ONHOLD.value:
        print '\nNumber of Cases with Status "technician_needed": ' + str(techreq_cases)
    elif status == Status.TECH.value:
        print '\nNumber of Cases with Status "technician_on_case": ' + str(tech_cases)

    return open_cases

def show_open_cases_nr(test=False):
    try:
        if test:
            db_cases = DB.test
        else:
            db_cases = DB.network
        new_case_col = db_cases.find({'Status':'new'})
        auto_cases_col = db_cases.find({'Status': 'solution_deployed'})
        techreq_cases_col = db_cases.find({'Status': 'technician_needed'})
        tech_cases_col = db_cases.find({'Status': 'technician_on_case'})

        print '\nCases with Status new:'
        for cas in new_case_col:
            print '\n' + cas['case_nr']
        print '\nCases with Status solution_deployed:'
        for aucas in auto_cases_col:
            print '\n' + aucas['case_nr']
        print '\nCases with Status technician_needed:'
        for techcol in techreq_cases_col:
            print '\n' + techcol['case_nr']
        print '\nCases with Status technician_on_case:'
        for techcol in tech_cases_col:
            print '\n' + techcol['case_nr']

    except Exception, e:
        print str(e)


def get_interface(yang_message):
    return yang_message['interfaces']['interface'].popitem()[0]
