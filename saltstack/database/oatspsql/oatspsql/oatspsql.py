#!/usr/bin/env python2.7
import psycopg2
import random
import string
from enum import Enum
import datetime

#global int to define the length of the generated case id
KEY_LEN = 12


class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'


def connect_to_db(db=None, user=None, host=None, pw=None):
    """
    Create a connection to the PostgrSQL database
    :param db: specify the database name
    :param user: spec. the db user
    :param host: the ip address where the database is hosted
    :param pw: the password of the user
    :return: the connection
    """
    if not db:
        db = 'casedb'
    if not user:
        user = 'netbox'
    if not host:
        host = 'localhost'
    if not pw:
        pw = 'oatsnetbox'

    data_conn = "dbname='" + str(db) + "' user='" + str(user) + "' host='" + str(host) + "' password=" + str(pw) + "'"
    try:
        conn = psycopg2.connect("dbname='casedb' user='netbox' host='localhost' password='oatsnetbox'")
    except (Exception, psycopg2.DatabaseError) as error:
        print('error in connect_to_db: ' + str(error))
    return conn


def create_cursor(conn):
    """
    Creates a cursor on the connected database
    :param conn: the database connection
    :return: the cursor
    """
    try:
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print('Error in create_cursor: ' + str(error))
    return cur


def base_str():
    return string.letters+string.digits


def key_gen():
    """
    Generates a key from random letters and numbers.
    :return: returns the generated key
    """
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    return ''.join(keylist)


def create_case(error, host, solution=None, description=None, status=Status.NEW.value):
    """
    Creates a new case on the database
    :param error: The name of the error.
    :param host: The hostname of the relevant device.
    :param solution: A List of applied solutions
    :param description: A desc. of the problem
    :param status: Status of the troubleshooting progress
    :return: the id of the newly created case
    """
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = key_gen()
    v5 = datetime.datetime.utcnow()
    v6 = datetime.datetime.utcnow()
    v7 = 'not_called'
    if not description:
        description = 'No description'
    if not solution:
        sol = ['Case created without automated Solution']
    else:
        curly = str(solution)
        sol = [curly]

    try:
        cur.execute("""INSERT INTO cases (case_nr, "event", "description", "status", "created", "last_updated", "technician",
      "sender_device", "solution") VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
                    (str(v1), str(error), str(description), str(status), v5, v6, v7, str(host), sol))
        print('\nCase inserted successfully\n')
    except Exception, e:
        print('error in create_case: ' + str(e))

    close_connection(conn, cur)
    return v1


def update_case(case_id, solution, status=None):
    """
    Updates a case in the database
    :param case_id: the id to find the specific case
    :param solution: Additional applied solutions
    :param status: THe new status of the progress of the troubleshooting process
    :return: the id of the case
    """
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = datetime.datetime.utcnow()
    status = str(status)
    if status == str(Status.ONHOLD.value) or status == str(Status.WORKING.value) or status == str(Status.TECH.value) \
            or status == str(Status.DONE.value):
        try:
            cur.execute("""UPDATE cases SET "status" = %s, "last_updated" = %s WHERE case_nr = %s::varchar;""",
                        (str(status), v1, str(case_id)))
            print('\nCase with State updated successfully\n')
        except Exception, e:
            print('Error in update_case with state1: ' + str(e))
    else:
        try:
            cur.execute("""UPDATE cases SET "last_updated" = %s WHERE case_nr = %s::varchar;""",
                        (v1, str(case_id)))
            print('\nCase without State updated successfully\n')
        except Exception, e:
            print('Error in update_case without state: ' + str(e))
    close_connection(conn, cur)
    conn = connect_to_db()
    cur = create_cursor(conn)
    sql = "UPDATE cases SET solution = solution || %s WHERE case_nr = %s::varchar"
    sol = '{' + str(solution) + '}'
    try:
        cur.execute(sql, (sol, case_id))
        print('\nAdditional solution step to case added successfully\n')
    except Exception, e:
        print('Error in update_case with solution: ' + str(e))
    close_connection(conn, cur)
    return case_id


def close_case(case_id):
    """
    Puts the status of a case to resolved and updates the last updated time.
    :param case_id: Id of the case in the database
    :return: ID of the closed case
    """
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = datetime.datetime.utcnow()
    status = str(Status.DONE.value)
    try:
        cur.execute("""UPDATE cases SET "status" = %s, "last_updated" = %s WHERE case_nr = %s::varchar;""",
                    (status, v1, case_id))
        print('\nCase closed successfully\n')
    except Exception, e:
        print('Error in close_case: ' + str(e))
    close_connection(conn, cur)
    return case_id


def take_case(case_id, technician):
    """
    Changes the status of the case and assigns a technician to it.
    :param case_id: Id of the case in the database
    :param technician: Name of the technician
    :return: The Id of the updated case
    """
    conn = connect_to_db()
    cur = create_cursor(conn)

    v1 = datetime.datetime.utcnow()

    try:
        cur.execute("""UPDATE cases SET "last_updated" = %s, "technician" = %s WHERE case_nr = %s::varchar;""",
                    (v1, technician, case_id))
        print('\nTechnician assigned successfully\n')
    except Exception, e:
        print('Error in take_case: ' + str(e))

    close_connection(conn, cur)
    return case_id


def get_solutions_as_string(case_id):
    """
    Function to get the list of applied solutions for a case
    :param case_id: Id of the case in the database
    :return: a list of solutions as string with inserted new lines.
    """
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
        print('Error in get_solutions_as_string: ' + str(e))
    close_connection(conn, cur)
    solution_strings = '\n'.join(sol_string)
    return solution_strings


def delete_case(case_id):
    """
    Deletes a case from the database.
    :param case_id: ID of the case in the database
    :return: True if successful
    """
    case_id = case_id
    conn = connect_to_db()
    cur = create_cursor(conn)
    exist = False
    delete_sql = "DELETE FROM cases WHERE case_nr = %s;"
    try:
        cur.execute(delete_sql, (case_id,))
        exist = True
    except Exception, e:
        print('Error in delete_case: ' + str(e))
    close_connection(conn, cur)
    return exist


def show_cases_of_last_day():
    """
    Function to get all caseids of cases from the last day
    :return: List of caseids
    """
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
        print('Error in show_cases_of_last_day: ' + str(e))
    close_connection(conn, cur)
    return cases


def numb_open_cases(status=None):
    """
    Function the get the number of open cases.
    :param status: If only a cases with a specific state should be returned.
    :return: Number of open cases
    """
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
        print('Error in numb_open_cases: ' + str(e))
    close_connection(conn, cur)
    return amount


def show_open_cases_nr():
    """
    Function to get the case id of all still open cases
    :return: List of case ids
    """
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
        print('Error in show_open_cases_nr: ' + str(e))
    close_connection(conn, cur)
    return cases


def close_connection(conn, cur):
    """
    Commits and closes the database connection, closes the cursor
    :param conn: The database connection
    :param cur: The cursor
    :return:
    """
    conn.commit()
    cur.close()
    conn.close()
