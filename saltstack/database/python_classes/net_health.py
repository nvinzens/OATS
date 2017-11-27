import sys
import pymongo
from pymongo import MongoClient
import json
import pprint
from bson.son import SON
from datetime import datetime, timedelta
from enum import Enum


client = MongoClient()
DB = client.oatsdb

class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'

def main():

    open_cases = numb_open_cases(Status.NEW.value)
    numb_open_cases(Status.WORKING.value)
    numb_open_cases(Status.ONHOLD.value)
    numb_open_cases(Status.TECH.value)

    print '\nThe Number of unresolved Cases is: ' + str(open_cases) + '\n'

    show_cases_of_last_day()

    show_open_cases_nr()

def numb_open_cases(status=None):

    new_cases = DB.cases.find({'Status': 'new'}).count()
    auto_cases = DB.cases.find({'Status': 'solution_deployed'}).count()
    techreq_cases = DB.cases.find({'Status': 'technician_needed'}).count()
    tech_cases = DB.cases.find({'Status': 'technician_on_case'}).count()

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

def show_open_cases_nr():

    try:
        new_case_col = DB.cases.find({'Status':'new'})
        auto_cases_col = DB.cases.find({'Status': 'solution_deployed'})
        techreq_cases_col = DB.cases.find({'Status': 'technician_needed'})
        tech_cases_col = DB.cases.find({'Status': 'technician_called'})

        print '\nCases with Status new:'
        for cas in new_case_col:
            print '\n' + cas['case_nr']
        print '\nCases with Status solution_deployed:'
        for aucas in auto_cases_col:
            print '\n' + aucas['case_nr']
        print '\nCases with Status technician_needed:'
        for techcol in techreq_cases_col:
            print '\n' + techcol['case_nr']
        print '\nCases with Status technician_called:'
        for techcol in tech_cases_col:
            print '\n' + techcol['case_nr']


    except Exception, e:
        print str(e)

def show_cases_of_last_day():
    last_day = datetime.now() - timedelta(hours=24)
    cases = DB.cases.find({'last_updated':{'$gt':last_day}})
    print '\nList of cases updated in the last 24 hours:\n'
    for cas in cases:
        print 'Case Nr: ' + cas['case_nr']
        print 'Case Event: ' + cas['Event']
        print 'Case Description: ' + cas['Description']
        print 'Case Status: ' + cas['Status']

def show_open_case_dev():
    pipe = [
        {'$project': {'Sender_device':1, 'Status':1}},
            {'$match':{'$or': [{'Status': 'new'}, {'Status': 'solution_deployed'}, {'Status': 'technician_needed'}, {'Status': 'technician_called'}]}},
            {'$group': {'_id': '$Status', 'total': {'$sum': 1}}}
        ]

    pprint.pprint(list(DB.cases.aggregate(pipe)))

if __name__ == '__main__':
    main()