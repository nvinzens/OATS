#!/usr/bin/env python2.7
import psycopg2
import random
import string
from enum import Enum
import datetime
import time

KEY_LEN = 12


class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'


def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='casedb' user='netbox' host='localhost' password='oatsadmin69'")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn


def create_cursor(conn):
    try:
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return cur


def base_str():
    return string.letters+string.digits


def key_gen():
    '''
    Generates a key from random letters and numbers.
    :return: returns the generated key
    '''
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)


def create_case(error, host, solution=None, description=None, status=Status.NEW.value, test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = key_gen()
    v5 = datetime.datetime.utcnow()
    v6 = datetime.datetime.utcnow()
    v7 = 'not_called'
    if not description:
        description = 'No description'
    if not solution:
        solution = ['Case created without automated Solution']

    try:
        cur.execute("""INSERT INTO cases (case_nr, "Event", "Description", "Status", "created", "last_updated", "technician",
      "Sender_device", "solution") VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                    (v1, error, description, status, v5, v6, v7, host, solution))
        print('\nCase inserted successfully\n')
    except Exception, e:
        print(str(e))

    close_connection(conn, cur)
    return v1


def update_case(case_id, solution, status=None, test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = datetime.datetime.utcnow()
    status = str(status)
    if status == str(Status.ONHOLD.value) or status == str(Status.WORKING.value) or status == str(Status.TECH.value) \
            or status == str(Status.DONE.value):
        try:
            cur.execute("""UPDATE cases SET "Status" = %s, "last_updated" = %s WHERE case_nr = %s::varchar;""",
                        (status, v1, case_id))
            print('\nCase updated successfully\n')
        except Exception, e:
            print(str(e))
    else:
        try:
            cur.execute("""UPDATE cases SET "last_updated" = %s WHERE case_nr = %s::varchar;""", (status, v1, case_id))
            print('\nCase updated successfully\n')
        except Exception, e:
            print(str(e))
    close_connection(conn, cur)
    conn = connect_to_db()
    cur = create_cursor(conn)
    sql = "UPDATE cases SET solution = solution || %s WHERE case_nr = %s::varchar"
    sol = '{' + solution + '}'
    cur.execute(sql, (sol, case_id))
    close_connection(conn, cur)
    return case_id


def take_case(case_id, technician, test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = datetime.datetime.utcnow()

    try:
        cur.execute("""UPDATE cases SET "last_updated" = %s, "technician" = %s WHERE case_nr = %s::varchar;""",
                    (v1, technician, case_id))
        print('\nTechnician assigned successfully\n')
    except Exception, e:
        print(str(e))

    close_connection(conn, cur)
    return case_id


def get_solutions_as_string(case_id, test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)
    sol_string = []
    try:
        cur.execute("""SELECT * FROM cases WHERE case_nr = %s::varchar;""",
                    (case_id,))
        rows = cur.fetchall()
        for row in rows:
            sol_string.extend(row[8])
    except Exception, e:
        print(str(e))
    close_connection(conn, cur)
    return sol_string


def delete_case(case_id):
    case_id = case_id
    conn = connect_to_db()
    cur = create_cursor(conn)
    exist = False
    delete_sql = "DELETE FROM cases WHERE case_nr = %s;"
    try:
        cur.execute(delete_sql, (case_id,))
        exist = True
    except Exception, e:
        print(str(e))
    close_connection(conn, cur)
    return exist


def show_cases_of_last_day(test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)
    cases = []
    sql = "SELECT * FROM cases WHERE last_updated>= NOW() - '1 day'::INTERVAL"
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            cases.append(row[0])
    except Exception, e:
        print(str(e))
    close_connection(conn, cur)
    return cases


def numb_open_cases(status=None, test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)
    v1 = "Status"
    amount = 0
    if not status:
        state = Status.DONE.value
        sql = "SELECT * FROM cases WHERE NOT %s = %s::varchar;"
    else:
        state = status
        sql = "SELECT * FROM cases WHERE %s = %s::varchar;"
    try:
        cur.execute(sql, (v1, state))
        rows = cur.fetchall()
        amount = len(rows)
    except Exception, e:
        print(str(e))
    close_connection(conn, cur)
    return amount


def show_open_cases_nr(test=False):
    conn = connect_to_db()
    cur = create_cursor(conn)
    cases = []
    v1 = "Status"
    state = Status.DONE.value
    sql = "SELECT * FROM cases WHERE NOT %s = %s::varchar;"
    try:
        cur.execute(sql, (v1, state))
        rows = cur.fetchall()
        for row in rows:
            cases.append(row[0])
    except Exception, e:
        print(str(e))
    close_connection(conn, cur)
    return cases


def close_connection(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def test_connect():
    connect = None
    cursor = None
    connect = connect_to_db()
    cursor = create_cursor(connect)
    close_connection(connect, cursor)
    assert connect is not None and cursor is not None


def test_key_gen():
    key1 = key_gen()
    key2 = key_gen()
    key_difference = key1 != key2
    key_length = len(key1) == 12
    assert key_difference == key_length


def test_create_and_delete_case():
    caseid = None
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    deleted = delete_case(caseid)
    assert deleted is True and caseid is not None


def test_update_case():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    updated = update_case(caseid, solution='New stuff', test=False)
    deleted = delete_case(caseid)
    assert updated is not None and caseid is not None and deleted is True


def test_update_case_state():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    updated = update_case(caseid, solution='New stuff', status=Status.ONHOLD.value, test=False)
    deleted = delete_case(caseid)
    assert updated is not None and caseid is not None and deleted is True


def test_take_case():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    tech_id = take_case(case_id=caseid, technician='techy')
    deleted = delete_case(caseid)
    assert caseid is not None and tech_id is not None and deleted is True


def test_get_solutions_as_string():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    sol = []
    sol = get_solutions_as_string(caseid, test=False)
    print sol
    deleted = delete_case(caseid)
    assert sol is not None and caseid is not None and deleted is True


def test_cases_of_last_day():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    cases = show_cases_of_last_day()
    deleted = delete_case(caseid)
    assert caseid is not None and len(cases) >= 1 and deleted is True


def test_open_cases():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    cases = numb_open_cases()
    deleted = delete_case(caseid)
    assert caseid is not None and cases >= 1 and deleted is True


def test_open_cases_nr():
    caseid = create_case(error='test', host='test', description='Test', status=Status.NEW.value, test=False)
    cases = show_open_cases_nr()
    deleted = delete_case(caseid)
    assert caseid is not None and len(cases) >= 1 and deleted is True