import sys
import pymongo
from pymongo import MongoClient
import datetime
import json
import string
import random

MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
KEY_LEN = 12

def base_str():
    return string.letters+string.digits

def key_gen():
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)

def get_interface_neighbor(host, interface):
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            return link['neighbor']

def get_neighbors(host):
    neighbors = []
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and not link['neighbor'] == MASTER:
            neighbors.append(link['neighbor'])
    return neighbors

def create_case(error, host, solution=None, description=None, status='new'):
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
        DB.cases.insert_one(new_case)
        print '\nCase inserted successfully\n'

    except Exception, e:
        print str(e)

    return case_id

def update_case(case_id, solution, status=None):
    if status:
        DB.cases.update_one(
            {'case_nr': case_id},
            {
                '$set': {
                    'Status': status,
                },
                '$push':{
                    'Solution': [solution]
                }
            }
        )
    else:
        DB.cases.update_one(
            {'case_nr': case_id},
            {
                '$push': {
                    'Solution': [solution]
                }
            }
        )
    return case_id

def close_case(case_id):
    DB.cases.update_one(
        {'case_nr': case_id},
        {
            '$set': {
                'Status': 'resolved',
            }
        }
    )
    return case_id

def take_case(case_id, technician):
    DB.cases.update_one(
        {'case_nr': case_id},
        {
            '$set': {
                'Status': 'technician_on_case',
                'technician': technician,
            }
        }
    )
    return case_id