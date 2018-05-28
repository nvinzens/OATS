#!/usr/bin/env python2.7
import psycopg2
import random
import string
import datetime
import time

from oatspsql import oatspsql

KEY_LEN = 12


def test_connect():
    connect = None
    cursor = None
    connect = oatspsql.connect_to_db()
    cursor = oatspsql.create_cursor(connect)
    oatspsql.close_connection(connect, cursor)
    assert connect is not None and cursor is not None


def test_key_gen():
    key1 = oatspsql.key_gen()
    key2 = oatspsql.key_gen()
    key_difference = key1 != key2
    key_length = len(key1) == 12
    assert key_difference == key_length


def test_create_and_delete_case():
    caseid = None
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    deleted = oatspsql.delete_case(caseid)
    assert deleted is True and caseid is not None


def test_create_and_delete_case_with_solution():
    caseid = None
    caseid = oatspsql.create_case(error='test', host='test', solution='sol', description='Test', status='new')
    deleted = oatspsql.delete_case(caseid)
    assert deleted is True and caseid is not None


def test_update_case():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    updated = oatspsql.update_case(caseid, solution='New stuff')
    deleted = oatspsql.delete_case(caseid)
    assert updated is not None and caseid is not None and deleted is True


def test_update_case_state():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    updated = oatspsql.update_case(caseid, solution='New stuff', status='technician_needed')
    deleted = oatspsql.delete_case(caseid)
    assert updated is not None and caseid is not None and deleted is True


def test_take_case():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    tech_id = oatspsql.take_case(case_id=caseid, technician='techy')
    deleted = oatspsql.delete_case(caseid)
    assert caseid is not None and tech_id is not None and deleted is True


def test_get_solutions_as_string():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    sol = []
    sol = oatspsql.get_solutions_as_string(caseid)
    print sol
    deleted = oatspsql.delete_case(caseid)
    assert sol is not None and caseid is not None and deleted is True


def test_cases_of_last_day():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    cases = oatspsql.show_cases_of_last_day()
    deleted = oatspsql.delete_case(caseid)
    assert caseid is not None and len(cases) >= 1 and deleted is True


def test_open_cases():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    cases = oatspsql.numb_open_cases()
    deleted = oatspsql.delete_case(caseid)
    assert caseid is not None and cases >= 1 and deleted is True


def test_open_cases_nr():
    caseid = oatspsql.create_case(error='test', host='test', description='Test', status='new')
    cases = oatspsql.show_open_cases_nr()
    deleted = oatspsql.delete_case(caseid)
    assert caseid is not None and len(cases) >= 1 and deleted is True
