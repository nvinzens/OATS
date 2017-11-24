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
            print '\nINVALID SELECTION\n'

def insert():
    host_name = ''
    ip_address = ''
    interface_names = []
    port_ips = []
    neighbor_neighbors = []
    number_of_connections = None
    try:
        while not host_name:
            host_name = raw_input('Enter Device Host name *required: ')
        while not ip_address:
            ip_address = raw_input('Enter IP Address *required: ')
        mac_address = raw_input('Enter MAC Address: ')
        dev_class = raw_input('Enter Device Class "Router", "Switch", "Device": ')
        role = raw_input('Enter Device Role "Core", "Distribution", "Access", "External": ')
        while number_of_connections is None:
            number_of_connections = int(raw_input('Enter Number of Connections *required: '))
        while len(interface_names) < number_of_connections:
            if_name = raw_input('Enter Interface Name for Interface Number "' + str(len(interface_names)+1) + '": ')
            interface_names.append(if_name)
        while len(port_ips) < number_of_connections:
            up_port_ip = raw_input('Enter Interface Ip for Interface Number "' + str(len(port_ips)+1) + '": ')
            port_ips.append(up_port_ip)
        while len(neighbor_neighbors) < number_of_connections:
            up_port_neighbor = raw_input('Enter Interface Neighbor for Interface Number "' + str(len(neighbor_neighbors)+1) + '": ')
            neighbor_neighbors.append(up_port_neighbor)

        while 1:
            print '\nUpdate Device : ' + host_name + ', as follows:'
            print '\nIP Adresse: ' + ip_address + '\nMAC Address: ' + mac_address + '\nClass: ' + dev_class + '\nRole: ' + role
            for ifn, ipp, nn in izip(interface_names, port_ips, neighbor_neighbors):
                print 'Interface name: ' + ifn + ' Port IP: ' + ipp + ' Neighbor: ' + nn
            selection = raw_input('Confirm [y] or [n]')
            if selection == 'y':
                db.network.insert_one(
                    {
                        'host_name': host_name,
                        'ip_address': ip_address,
                        'MAC_address': mac_address,
                        'Class': dev_class,
                        'Role': role,
                    })
                for ifn, ipp, nn in izip(interface_names, port_ips, neighbor_neighbors):
                    db.network.update_one(
                        {'host_name': host_name},
                        {
                            '$pushAll': {
                                'connections': [
                                     {'interface': ifn, 'ip': ipp, 'neighbor': nn}
                                ]}
                        }
                    )
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
    host_name = ''
    number_of_connections = ''
    interface_names = []
    port_ips = []
    neighbor_neighbors = []
    update_dev_props = []
    dev_attr = []
    try:
        while not host_name:
            host_name = raw_input('Enter Device Host name *required: ')
        up_ip_address = raw_input('Enter IP Address: ')
        if up_ip_address:
            update_dev_props.append(up_ip_address)
            dev_attr.append('ip_address')

        up_mac_address = raw_input('Enter MAC Address: ')
        if up_mac_address:
            update_dev_props.append(up_mac_address)
            dev_attr.append('MAC_address')
        up_dev_class = raw_input('Enter Device Class "Router", "Switch", "Device": ')
        if up_dev_class:
            update_dev_props.append(up_dev_class)
            dev_attr.append('Class')
        up_role = raw_input('Enter Device Role "Core", "Distribution", "Access", "External": ')
        if up_role:
            update_dev_props.append(up_role)
            dev_attr.append('Role')
        while not number_of_connections:
            number_of_connections = int(raw_input('Enter Number of Connections *required: '))
        while len(interface_names) < number_of_connections:
            if_name = raw_input('Enter Interface Name for Interface Number "' + str(len(interface_names) + 1) + '": ')
            interface_names.append(if_name)
        while len(port_ips) < number_of_connections:
            up_port_ip = raw_input('Enter Interface Ip for Interface Number "' + str(len(port_ips) + 1) + '": ')
            port_ips.append(up_port_ip)
        while len(neighbor_neighbors) < number_of_connections:
            up_port_neighbor = raw_input('Enter Interface Neighbor for Interface Number "' + str(len(neighbor_neighbors) + 1) + '": ')
            neighbor_neighbors.append(up_port_neighbor)

        while 1:
            print '\nUpdate Device : ' + host_name + ', as follows:\n'
            for prop, attr in izip(update_dev_props, dev_attr):
                if prop:
                    print '\n' + attr + ": "+ prop
            for ifn, ipp, nn in izip(interface_names, port_ips, neighbor_neighbors):
                print 'Interface name: ' + ifn + ' Port IP: ' + ipp + ' Neighbor: ' + nn
            selection = raw_input('Confirm [y] or [n]')

            if selection == 'y':
                for prop, attr in izip(update_dev_props, dev_attr):
                    if prop:
                        db.network.update_one(
                            {'host_name': host_name},
                            {
                                '$set': {
                                    attr: prop,
                                }
                            }
                        )
                for ifn, ipp, nn in izip(interface_names, port_ips, neighbor_neighbors):
                    db.network.update_one(
                        {'host_name': host_name},
                        {
                            '$pushAll': {
                                'connections': [
                                     {'interface': ifn, 'ip': ipp, 'neighbor': nn}
                                ]}
                        }
                    )

                print '\nData updated successfully\n'
                break
            elif selection == 'n':
                print '\nUpdate cancelled\n'
                break
            else:
                print '\nINVALID SELECTION\n'
        db.network.update_one(
            {'host_name': up_host_name,},
            {
                'ip_address': up_ip_address,
                'MAC_address': up_mac_address,
                'Class': up_dev_class,
                'Role': up_role,
            }
        )

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
        while 1:
            selection = raw_input('\nDelete every Device with Hostname: ' + del_dev + ', [y] or [n]:')

            if selection == 'y':
                db.network.delete_many({'host_name': del_dev})
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
