import sys
import pymongo
from pymongo import MongoClient
import datetime
import json

MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb

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

def insert_case(evarg, devarg, solarg):

    event = evarg
    device = devarg
    solution = solarg

    case_id = event + device + solution

    new_case = {
        "case_nr": case_id,
        "Event": event,
        "Description": "Event description",
        "Status": "New",
        "created": datetime.datetime.utcnow(),
        "last_updated": datetime.datetime.utcnow(),
        "technician": "not_called",
        "Sender_Device": device,
        "Solution": solution
    }

    try:
        DB.cases.insert_one(new_case)
        print "\nCase inserted successfully\n"

    except Exception, e:
        print str(e)

    return case_id