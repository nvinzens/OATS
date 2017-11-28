import sys
import pymongo
from pymongo import MongoClient
import datetime
import json
from itertools import izip
from enum import Enum


client = MongoClient()
db = client.oatsdb
class Status(Enum):
    NEW = 'new'
    WORKING = 'solution_deployed'
    ONHOLD = 'technician_needed'
    TECH = 'technician_on_case'
    DONE = 'resolved'


def main():
    while 1:
        try:
            selection = raw_input('\nSelect 1 to create, 2 to update, 3 to read, 4 to delete, E to end\n')

            if selection == '1':
                insert()
            elif selection == '2':
                update()
            elif selection == '3':
                read()
            elif selection == '4':
                delete()
            elif selection == 'E':
                sys.exit()
            elif selection == 'e':
                sys.exit()
            else:
                print '\nINVALID SELECTION\n'
        except KeyboardInterrupt:
            sys.exit()

def insert():
    case_nr = ''
    device = ''
    try:
        while not case_nr:
            case_nr = raw_input('Enter Case id *required: ')
        event = 'User defined'
        description = raw_input('Enter Description: ')
        status = 'new'
        technician = 'not_called'
        while not device:
            device = raw_input('Enter involved Device *required: ')
        solution = raw_input('Enter Solution: ')

        while 1:
            selection = raw_input('\nInsert this into Database?\nCase Nr:' + case_nr  + '\nDescription: ' + description + '\nDevice: ' + device + '\nSolution: ' + solution +'\n\n [y] or [n]')
            if selection == 'y':
                db.cases.insert_one(
                    {
                        'case_nr': case_nr,
                        'Event': event,
                        'Description': description,
                        'Status': status,
                        'created': datetime.datetime.utcnow(),
                        'last_updated': datetime.datetime.utcnow(),
                        'technician': technician,
                        'Sender_Device': device,
                        'Solution': [solution]
                    })
                print '\nInserted data successfully\n'
                break
            elif selection == 'n':
                print '\nInsertion Cancelled\n'
                break
            else:
                print '\nINVALID SELECTION\n'
    except Exception, e:
        print str(e)

def update():
    update_elements = []
    case_attr =[]
    up_case_id = ''
    up_solution = ''
    try:
        while not up_case_id:
            up_case_id = raw_input('Enter Case id *required: ')
        up_event = raw_input('Enter Event :')
        if up_event:
            update_elements.append(up_event)
            case_attr.append('Event')
        up_description = raw_input('Enter Description :')
        if up_description:
            update_elements.append(up_description)
            case_attr.append('Description')
        up_status = raw_input('Enter Status: \n new, solution_deployed, technician_needed, technician_on_case, resolved: \n')
        if up_status:
            update_elements.append(up_status)
            case_attr.append('Status')
        up_technician = raw_input('Enter Technician :')
        if up_technician:
            update_elements.append(up_technician)
            case_attr.append('technician')
        up_device = raw_input('Enter involved Device :')
        if up_device:
            update_elements.append(up_device)
            case_attr.append('Sender_Device')
        up_solution = raw_input('Enter Solution :')

        while 1:
            print '\nUpdate Case Nr: ' + up_case_id + ', as follows:'
            for el, attr in izip(update_elements, case_attr):
                if el:
                    print attr + ': '+ el
            if up_solution:
                print '\nAdded Solution: ' + up_solution + '\n'
            selection = raw_input('Confirm [y] or [n]:')

            if selection == 'y':
                for el, attr in izip(update_elements, case_attr):
                    if el:
                        db.cases.update_one(
                            {'case_nr': up_case_id},
                            {
                                '$set': {
                                    attr: el,
                                    'last_updated': datetime.datetime.utcnow(),
                                }
                            }
                        )
            if up_solution:
                db.cases.update_one(
                    {'case_nr': up_case_id},
                    {
                        {
                            '$set': {
                                'last_updated': datetime.datetime.utcnow(),
                            },
                            '$push':
                                {'Solution': up_solution}
                         }
                    }
                    )
                print '\nData updated successfully\n'
                break
            elif selection == 'n':
                print '\nUpdate cancelled\n'
                break
            else:
                print '\nINVALID SELECTION\n'
    except Exception, e:
        print str(e)


def read():
    try:
        caseCol = db.cases.find()
        print '\nAll data from Case Database\n'
        for cas in caseCol:
            print cas

    except Exception, e:
        print str(e)


def delete():
    try:
        del_case = raw_input('\nEnter Case Nr to delete: \n')
        while 1:
            selection = raw_input('\nDelete every Case with Nr: ' + del_case + ', [y] or [n]:')

            if selection == 'y':
                db.cases.delete_many({'case_nr': del_case})
                print '\nDeletion successful\n'
                break
            elif selection == 'n':
                print '\nDeletion cancelled\n'
                break
            else:
                print '\nINVALID SELECTION\n'
    except Exception, e:
        print str(e)


main()