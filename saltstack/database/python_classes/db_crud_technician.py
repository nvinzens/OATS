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
        tech_id = raw_input('Enter Tech id :')
        fname = raw_input('Enter First Name :')
        lname = raw_input('Enter Last Name :')
        schannel = raw_input('Enter Slack Channel :')

        db.technician.insert_one(
            {
                "tech_id": tech_id,
                "first_name": fname,
                "last_name": lname,
                "slack_channel": schannel
            })
        print '\nInserted data successfully\n'

    except Exception, e:
        print str(e)

def update():
    try:
        up_tech_id = raw_input('Enter Tech id :')
        up_fname = raw_input('Enter First Name :')
        up_lname = raw_input('Enter Last Name :')
        up_schannel = raw_input('Enter Slack Channel :')

        db.technician.update_one(
            {"id": up_tech_id},
            {
                "$set": {
                    "tech_id": tech_id,
                    "first_name": up_fname,
                    "last_name": up_lname,
                    "slack_channel": up_schannel
                }
            }
        )
        print "\nData updated successfully\n"

    except Exception, e:
        print str(e)


def read():
    try:
        techCol = db.technician.find()
        print '\n All data from Technician Database \n'
        for tec in techCol:
            print tec

    except Exception, e:
        print str(e)


def delete():
    try:
        del_tech = raw_input('\nEnter Tech id to delete\n')
        db.technician.delete_many({"id": del_tech})
        print '\nDeletion successful\n'
    except Exception, e:
        print str(e)


main()