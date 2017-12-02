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

def get_ospf_neighbors(host, case=None, test=False):
    '''
    Get all the OSPF neighbors of the host (via oats db).
    :param host: The host
    :param case: case-id for updating the current case
    :return: All the hosts OSPF neighbors (as list)
    '''
    ospf_neighbors = []
    if test:
        db_network = DB.test
    else:
        db_network = DB.network
    links = db_network.find_one({'host_name': host})['connections']
    for link in links:
        if link['ospf_area'] and link['ospf_area']!='None':
            ospf_neighbors.append(link['neighbor'])
    if case:
        update_case(case, 'Get OSPF neighbors of ' + host + ' from oats database.')
    return ospf_neighbors

def get_solutions_as_string(case_id, test=False):
    '''
    Get the applied solutions of a Case as string (via oats db).
    :param case_id: The case
    :return: List of applied solutions as string with \n inbetween.
    '''
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

def get_vrf_ip(host, test=False):
    if test:
        db_network = DB.test
    else:
        db_network = DB.network
    links = db_network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] == MASTER:
            return link['ip']

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
            if case:
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
    if case:
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


def get_interface(error, yang_message):
    # method to get interface can be different for different errors
    if error == 'INTERFACE_DOWN':
        return yang_message['interfaces']['interface'].popitem()[0]
    if error == 'OSPF_NEIGHBOR_DOWN':
        interfaces = yang_message['network-instances']['network-instance']['global']['protocols']['protocol']['ospf']['ospfv2']['areas']['area']['area']
        return interfaces['interfaces']['interface'].popitem()[0]