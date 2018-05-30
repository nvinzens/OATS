#!/usr/bin/env python2.7
import psycopg2
import random
import string
from enum import Enum
import datetime
import yaml
import logging.config

#global int to define the length of the generated case id
KEY_LEN = 12

log_file = open('/etc/oats/logging.yaml')
log_conf = yaml.load(log_file)
logging.config.dictConfig(log_conf['logging'])
logger = logging.getLogger('oats.psql')


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
    logger.info('Connecting to PostgreSQL Database...')
    try:
        conn = psycopg2.connect("dbname='casedb' user='netbox' host='localhost' password='oatsnetbox'")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.exception('Error in establishing connection to psql db')
    return conn


def create_cursor(conn):
    """
    Creates a cursor on the connected database
    :param conn: the database connection
    :return: the cursor
    """
    logger.info('Creating cursor for psql database...')
    try:
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.exception('Error in creating cursor for psql db')
    return cur


def base_str():
    return string.letters+string.digits


def key_gen():
    """
    Generates a key from random letters and numbers.
    :return: returns the generated key
    """
    keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
    logger.info('Generating new Caseid')
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
        logger.exception('Exception in oatspsql.create_case')

    logger.debug('Creating new case in psql database for error {0} on host {1}'.format(error, host))
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

    logger.info('Update_Case {0}'.format(case_id))
    v1 = datetime.datetime.utcnow()
    status = str(status)
    if status == str(Status.ONHOLD.value) or status == str(Status.WORKING.value) or status == str(Status.TECH.value) \
            or status == str(Status.DONE.value):
        try:
            cur.execute("""UPDATE cases SET "status" = %s, "last_updated" = %s WHERE case_nr = %s::varchar;""",
                        (str(status), v1, str(case_id)))
            logger.debug('Case with State updated successfully')
        except Exception, e:
            logger.exception('Error in update_case with state1 {0}'.format(case_id))
    else:
        try:
            cur.execute("""UPDATE cases SET "last_updated" = %s WHERE case_nr = %s::varchar;""",
                        (v1, str(case_id)))
            logger.debug('Case without State updated successfully')
        except Exception, e:
            logger.exception('Error in update_case  without state: {0}'.format(case_id))
    close_connection(conn, cur)
    conn = connect_to_db()
    cur = create_cursor(conn)
    sql = "UPDATE cases SET solution = solution || %s WHERE case_nr = %s::varchar"
    sol = '{' + str(solution) + '}'
    try:
        cur.execute(sql, (sol, case_id))
        logger.debug('Additional solution step to case added successfully: {0}'.format(case_id))
    except Exception, e:
        logger.exception('Error in update_case with solution: {0}'.format(case_id))
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

    logger.info('Closing case: {0}'.format(case_id))
    v1 = datetime.datetime.utcnow()
    status = str(Status.DONE.value)
    try:
        cur.execute("""UPDATE cases SET "status" = %s, "last_updated" = %s WHERE case_nr = %s::varchar;""",
                    (status, v1, case_id))
        logger.debug('Case {0} closed successfully'.format(case_id))
    except Exception, e:
        logger.exception('Error in close_case {0}'.format(case_id))
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
        logger.debug('Technician {0} successfully asigned to case {1}'.format(technician, case_id))
    except Exception, e:
        logger.exception('Error in take_case: {0}'.format(case_id))

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
    logger.debug('Getting solutions as strings for case: {0}'.format(case_id))
    try:
        cur.execute("""SELECT * FROM cases WHERE case_nr = %s::varchar;""",
                    (case_id,))
        rows = cur.fetchall()
        for row in rows:
            sol_string.extend(row[8])
        logger.debug('Successfully extracted solutions as strings for case: {0}'.format(case_id))
    except Exception, e:
        logger.exception('Error in oatspsql.get_solutions_as_string: {0}'.format(case_id))
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
    logger.debug('Deleting case: {0}'.format(case_id))
    try:
        cur.execute(delete_sql, (case_id,))
        exist = True
        logger.debug('Successfully deleted case: {0}'.format(case_id))
    except Exception, e:
        logger.exception('Exception in oatspsql.delete_case {0}'.format(case_id))
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
    logger.debug('Trying to access cases of the last day')
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            cases.append(row[0])
        logger.debug('Got cases of last day')
    except Exception, e:
        logger.exception('Exception in show_cases_of_last_day')
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
    logger.debug('Trying to access number of open cases')
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
        logger.debug('Got number of open cases')
    except Exception, e:
        logger.exception('Exception in oatspsql.numb_open_cases')
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
    logger.debug('Trying to show open cases by number')
    try:
        cur.execute(sql, (v1, state))
        rows = cur.fetchall()
        for row in rows:
            cases.append(row[0])
        logger.debug('Got open cases by number')
    except Exception, e:
        logger.exception('Error in oatspsql.show_open_cases_nr')
    close_connection(conn, cur)
    return cases


def close_connection(conn, cur):
    """
    Commits and closes the database connection, closes the cursor
    :param conn: The database connection
    :param cur: The cursor
    :return:
    """
    logger.info('Closing psql db connection')
    conn.commit()
    cur.close()
    conn.close()
