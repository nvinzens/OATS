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
        host_name = raw_input('Enter Device Host name :')
        ip_address = raw_input('Enter IP Address :')
        mac_address = raw_input('Enter MAC Address :')
        dev_class = raw_input('Enter Device Class "Router", "Switch", "Device" :')
        role = raw_input('Enter Device Role "Core", "Distribution", "Access", "External" :')
        port_name = raw_input('Enter Interface Name:')
        port_ip = raw_input('Enter Interface IP Address :')
        port_neighbor = raw_input('Enter Neighbor :')

        db.network.insert_one(
            {
              "host_name": host_name,
              "ip_address": ip_address,
              "MAC_address": mac_address,
              "Class": dev_class,
              "Role": role,
              "connections": [
                { "interface": port_name, "ip": port_ip, "neighbor": port_neighbor}
              ]
            })
        print '\nInserted data successfully\n'

    except Exception, e:
        print str(e)

def update():
    try:
        up_host_name = raw_input('Enter Device Host name :')
        up_ip_address = raw_input('Enter IP Address :')
        up_mac_address = raw_input('Enter MAC Address :')
        up_dev_class = raw_input('Enter Device Class "Router", "Switch", "Device" :')
        up_role = raw_input('Enter Device Role "Core", "Distribution", "Access", "External" :')
        up_port_name = raw_input('Enter Interface Name:')
        up_port_ip = raw_input('Enter Interface IP Address :')
        up_port_neighbor = raw_input('Enter Neighbor :')

        db.network.update_one(
            {"host_name": up_host_name,},
            {
                "ip_address": up_ip_address,
                "MAC_address": up_mac_address,
                "Class": up_dev_class,
                "Role": up_role,
                "connections": [
                    {"interface": up_port_name, "ip": up_port_ip, "neighbor": up_port_neighbor}
                ]
            }
        )
        print "\nData updated successfully\n"

    except Exception, e:
        print str(e)


def read():
    try:
        netcol = db.network.find()
        print '\n All data from Network Database \n'
        for net in netcol:
            print net

    except Exception, e:
        print str(e)


def delete():
    try:
        del_dev = raw_input('\nEnter Device Host Name to delete\n')
        db.network.delete_many({"host_name": del_dev})
        print '\nDeletion successful\n'
    except Exception, e:
        print str(e)


main()
