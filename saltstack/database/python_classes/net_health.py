import sys
import pymongo
from pymongo import MongoClient
import json
import pprint
from bson.son import SON

client = MongoClient()
db = client.oatsdb

def main():

    new = 'New'

    #show_open_cases_nr()

    open_cases = numb_open_cases(new)

    print '\nThe Number of unresolved Cases is: ' + str(open_cases) + '\n'

def numb_open_cases(status=None):

    new_cases = db.cases.find({'Status': 'New'}).count()
    auto_cases = db.cases.find({'Status': 'solution_deployed'}).count()
    techreq_cases = db.cases.find({'Status': 'technician_needed'}).count()
    tech_cases = db.cases.find({'Status': 'technician_called'}).count()

    open_cases = new_cases + auto_cases + techreq_cases + tech_cases

    if status == 'New':
        print '\nNumber of Cases with Status New: ' + str(new_cases)
    elif status == 'solution_deployed':
        print '\nNumber of Cases with Status "solution_deployed": ' + str(auto_cases)

    elif status == 'technician_needed':
        print '\nNumber of Cases with Status "technician_needed": ' + str(techreq_cases)
    elif status == 'technician_called':
        print '\nNumber of Cases with Status "technician_called": ' + str(tech_cases)

    return open_cases

def show_open_cases_nr():

    try:
        new_case_col = db.cases.find({'Status':'New'})
        auto_cases_col = db.cases.find({'Status': 'solution_deployed'})
        techreq_cases_col = db.cases.find({'Status': 'technician_needed'})
        tech_cases_col = db.cases.find({'Status': 'technician_called'})

        print '\nCases with Status New:'
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

def show_open_case_dev():
    '''
        pipe = [
            {'$project': {'Sender_device':1, 'Status':1}},
            {'$match':{'$or': [{'Status': 'New'}, {'Status': 'solution_deployed'}, {'Status': 'technician_needed'}, {'Status': 'technician_called'}]}},
            {'$group': {'_id': '$Status', 'total': {'$sum': 1}}}
        ]

        pprint.pprint(list(db.cases.aggregate(pipe)))
        '''
    #Should return if and how many Open Cases currently are on a certain device
    print 'hello'

if __name__ == '__main__':
    main()