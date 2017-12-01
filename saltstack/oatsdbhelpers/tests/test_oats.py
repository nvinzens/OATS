from oats import oats
import sys
import pymongo
from pymongo import MongoClient
import datetime
import json
import string
import random

DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb

def case_setup():
    new_case = {
        'case_nr': '1234',
        'Event': 'Testevent',
        'Description': 'Test description',
        'Status': 'Test status',
        'created': datetime.datetime.utcnow(),
        'last_updated': datetime.datetime.utcnow(),
        'technician': '',
        'Sender_Device': 'Test device',
        'Solution': ['Test solution']
    }
    try:
        DB.test.insert_one(new_case)
        print '\nTest Setup successful\n'

    except Exception, e:
        print str(e)

def net_setup():
    new_device = {
        'host_name': 'TEST',
        'ip_address': '127.0.0.1',
        'MAC_address': '00:00:00:00:00:01',
        'Class': 'TEST_CLASS',
        'Role': 'TEST_ROLE',
        'connections': [
            {'interface': 'TestIF1', 'ip': '127.0.0.2', 'neighbor': 'MASTER'},
            {'interface': 'TestIF2', 'ip': '127.0.0.3', 'neighbor': 'TEST2'}
        ]
    }
    try:
        DB.test.insert_one(new_device)
        print '\nTest Setup successful\n'

    except Exception, e:
        print str(e)

def teardown():
    try:
        DB.test.delete_many({})
        print '\nTest Teardown successful\n'

    except Exception, e:
        print str(e)

#Test for KeyID generator
def test_key_gen():
    key1 = oats.key_gen()
    key2 = oats.key_gen()
    key_difference = key1 != key2
    key_length = len(key1) == 12
    assert key_difference == key_length

#Tests for simple Database Access functions
def test_create_case():
    test_case_id = oats.create_case('Test', 'Test', solution='testsol', description='test desc', test=True)
    teardown()
    assert test_case_id

def test_update_case():
    case_setup()
    test_case_id = oats.update_case('1234', solution='testsol2', status=None, test=True)
    teardown()
    assert test_case_id

def test_close_case():
    case_setup()
    no_done = DB.test.find({'Status': 'resolved'}).count()
    oats.close_case('1234', test=True)
    done = DB.test.find({'Status': 'resolved'}).count()
    teardown()
    assert done != no_done

def test_take_case():
    case_setup()
    no_tech = DB.test.find({'Status': 'technician_on_case'}).count()
    no_tech2 = DB.test.find({'technician': 'testtech'}).count()
    oats.take_case('1234', 'testtech', test=True)
    tech = DB.test.find({'Status': 'technician_on_case'}).count()
    tech2 = DB.test.find({'technician': 'testtech'}).count()
    assert no_tech != tech and no_tech2 != tech2

#Tests for advanced Database Access functions
def test_get_solutions():
    assert False

def test_vrf_ip():
    assert False

def test_open_cases():
    assert False

def test_neighbor():
    assert False

def test_interface_neighbor():
    assert False