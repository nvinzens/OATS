#!/usr/bin/env python
import sys
import pymongo
from pymongo import MongoClient
import datetime
import json
from itertools import izip

client = MongoClient()
db = client.oatsdb


def main():
    while 1:
        try:
            selection = raw_input('\nSelect 1 to insert, 2 to update, 3 to read, 4 to delete, E to end\n')

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
                print('\nINVALID SELECTION\n')

        except KeyboardInterrupt:
            sys.exit()

def insert():
    tech_id = ''
    try:
        while not tech_id:
            tech_id = raw_input('Enter Tech id *required:')
        fname = raw_input('Enter First Name :')
        lname = raw_input('Enter Last Name :')
        schannel = raw_input('Enter Slack Channel :')

        while 1:
            selection = raw_input('\nInsert this Technician into the Database?\nTech Id: ' + tech_id + '\nFirst Name: '+ fname + '\nLast Name: '+ lname + '\nSlack Channel: ' + schannel +'\n[y] or [n]: ')

            if selection == 'y':
                db.technician.insert_one(
                    {
                        "tech_id": tech_id,
                        "first_name": fname,
                        "last_name": lname,
                        "slack_channel": schannel
                    })
                print('\nInserted data successfully\n')
                break
            elif selection == 'n':
                print('\nInsertion Cancelled\n')
                break
            else:
                print('\nINVALID SELECTION\n')

    except Exception, e:
        print(str(e))

def update():
    update_elements = []
    tech_attr = []
    up_tech_id = ''
    try:
        while not up_tech_id:
            up_tech_id = raw_input('Enter Tech id *required: ')
        up_fname = raw_input('Enter First Name :')
        if up_fname:
            update_elements.append(up_fname)
            tech_attr.append("first_name")
        up_lname = raw_input('Enter Last Name :')
        if up_lname:
            update_elements.append(up_lname)
            tech_attr.append("last_name")
        up_schannel = raw_input('Enter Slack Channel :')
        if up_schannel:
            update_elements.append(up_schannel)
            tech_attr.append("slack_channel")

        while 1:
            print('\nUpdate Technician: ' + up_tech_id + ', as follows:')
            for el, attr in izip(update_elements, tech_attr):
                if el:
                    print(attr + ": "+ el)
            selection = raw_input('Confirm [y] or [n]')

            if selection == 'y':
                for el, attr in izip(update_elements, tech_attr):
                    if el:
                        db.cases.update_one(
                            {"tech_id": up_tech_id},
                            {
                                "$set": {
                                    attr: el,
                                }
                            }
                        )
                print("\nData updated successfully\n")
                break
            elif selection == 'n':
                print("\nUpdate cancelled\n")
                break
            else:
                print('\nINVALID SELECTION\n')

    except Exception, e:
        print(str(e))


def read():
    try:
        techCol = db.technician.find()
        print('\n All data from Technician Database \n')
        for tec in techCol:
            print('\nTech ID: ' + tec['tech_id'])
            print('First name: ' + tec['first_name'])
            print('Last name: ' + tec['last_name'])
            print('Slack Channel: ' + tec['slack_channel'])

    except Exception, e:
        print(str(e))


def delete():
    try:
        del_tech = raw_input('\nEnter Tech id to delete\n')
        while 1:
            selection = raw_input('\nDelete every Case with Nr: ' + del_tech + ", [y] or [n]:")

            if selection == 'y':
                db.technician.delete_many({"tech_id": del_tech})
                print('\nDeletion successful\n')
                break
            elif selection == 'n':
                print('\nDeletion cancelled\n')
                break
            else:
                print('\nINVALID SELECTION\n')
    except Exception, e:
        print(str(e))


main()