#!/usr/bin/env python2.7
import psycopg2
import random
import spring
from enum import Enum
import datetime

class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'

def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='casedb' user='netbox' host='localhost' password='oatsadmin69'")
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


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

    connect_to_db()

    v1 = key_gen()
    v5 = datetime.datetime.utcnow()
    v6 = datetime.datetime.utcnow()
    v7 = 'not_called'
    if not description:
        description = 'No description'
    if not solution:
        solution = ['Case created without automated Solution']

    try:
        cur.execute("""INSERT INTO cases (case_nr, "Event", "Status", "Description", "created", "last_updated", "technician",
      "Sender_device", "Solution") VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                    (v1, error, description, status, v5, v6, v7, host, solution))
        print('\nCase inserted successfully\n')
    except Exception, e:
        print(str(e))

    close_connection()
    return v1


def update_case(case_id, solution, status=None, test=False):

    connect_to_db()

    v1 = datetime.datetime.utcnow()
    if status == Status.ONHOLD.value or status==Status.WORKING.value or status==Status.TECH.value or status==Status.DONE.value :
        try:
            cur.execute("""UPDATE cases SET "Status" = %s, "last_updated" = %s, WHERE case_nr = %s::varchar;""", (status, v1, case_id))
            print('\nCase updated successfully\n')
        except Exception, e:
            print(str(e))
    else:
        try:
            cur.execute("""UPDATE cases SET "last_updated" = %s WHERE case_nr = %s::varchar;""", (status, v1, case_id))
            print('\nCase updated successfully\n')
        except Exception, e:
            print(str(e))
    sql = "UPDATE cases SET solution = solution || %s WHERE case_nr = %s::varchar"
    sol = '{' + solution + '}'
    cur.execute(sql, (sol, case_id))
    close_connection()
    return case_id


def take_case(case_id, technician, test=False):

    connect_to_db()

    v1 = datetime.datetime.utcnow()

    try:
        cur.execute("""UPDATE cases SET "last_updated" = %s, "technician" = %s WHERE case_nr = %s::varchar;""",
                    (v1, technician, case_id))
        print('\nTechnician assigned successfully\n')
    except Exception, e:
        print(str(e))

    close_connection()
    return case_id


def get_solutions_as_string(case_id, test=False):

    connect_to_db()
    sol_string = []

    try:
        cur.execute("""SELECT * FROM cases WHERE case_nr = %s::varchar;""",
                    (case_id))
        rows = cur.fetchall()
        for row in rows:
            sol_string.extend(row[8])
    except Exception, e:
        print(str(e))


    close_connection()
    return sol_string


def show_cases_of_last_day(test=False):

    connect_to_db()
    cases = []

    sql = "SELECT * FROM cases WHERE last_updated>= NOW() - '1 day'::INTERVAL"
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            cases.append(rows[0])
    except Exception, e:
        print(str(e))

    close_connection()
    return cases


def numb_open_cases(status=None, test=False):

    connect_to_db()
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

    close_connection()
    return amount


def show_open_cases_nr(test=False):

    connect_to_db()
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

    close_connection()
    return cases


def close_connection():
    conn.commit()
    cur.close()
    conn.close()
