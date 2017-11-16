import sys
import pymongo
from pymongo import MongoClient
import datetime
import json

client = MongoClient()
db = client.test


def main():
    while (1):
        selection = raw_input('\nSelect 1 to insert, 2 to update, 3 to read, 4 to delete, "CTRL +C" to end\n')

        if selection == '1':
            insert()
        elif selection == '2':
            update()
        elif selection == '3':
            read()
        elif selection == '4':
            print 'delete'
            delete()
        else:
            print '\n INVALID SELECTION \n'

def insert():
    try:
        case_nr = raw_input('Enter Case id :')
        event = raw_input('Enter Event :')
        description = raw_input('Enter Description :')
        status = "New"
        technician = "not_called"
        device = raw_input('Enter involved Device :')
        solution = raw_input('Enter Solution :')

        db.cases.insert_one(
            {
              "host_name": "$INSERT_HOST_NAME$",
              "ip_address": "$INSERT_IP_ADDRESS$",
              "MAC_address": "$INSERT_MAC_ADDRESS$",
              "Class": "$INSERT_CLASS$",
              "Role": "$INSERT_ROLE$",
              "connections": [
                { "interface": "$INSERT_INTERFACE$", "ip": "INSERT_IP_ADDRESS", "neighbor": "$INSERT_NEIGHBOR$" }
              ]
            })
        print '\nInserted data successfully\n'

    except Exception, e:
        print str(e)

def update():
    try:
        up_case_id = raw_input('Enter Case id :')
        up_event = raw_input('Enter Event :')
        up_description = raw_input('Enter Description :')
        up_status = raw_input('Enter Status: New, solution_deployed, technician_needed, technician_called, resolved')
        up_technician = raw_input('Enter Technician :')
        up_device = raw_input('Enter involved Device :')
        up_solution = raw_input('Enter Solution :')

        db.cases.update_one(
            {"id": up_case_id},
            {
                "$set": {
                    "Event": up_event,
                    "Description": up_description,
                    "Status": up_status,
                    "last_updated": datetime.datetime.utcnow(),
                    "technician": up_technician,
                    "Sender_Device": up_device,
                    "Solution_tried": {
                        "Solution": up_solution
                    }
                }
            }
        )
        print "\nData updated successfully\n"

    except Exception, e:
        print str(e)


def read():
    try:
        caseCol = db.cases.find()
        print '\n All data from Case Database \n'
        for cas in caseCol:
            print cas

    except Exception, e:
        print str(e)


def delete():
    try:
        del_case = raw_input('\nEnter Case id to delete\n')
        db.cases.delete_many({"id": del_case})
        print '\nDeletion successful\n'
    except Exception, e:
        print str(e)


main()
