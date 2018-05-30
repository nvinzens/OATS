#!/usr/bin/env python2.7
import pynetbox
from oatspsql import oatspsql


def connect(url=None, token=None):
    '''
    Function to connect to netbox
    :param url: ip address of the netbox host
    :param token: netbox api token
    :return: the connection
    '''
    if not url:
        url = 'http://10.20.1.10'
    if not token:
        token = '20b9f6f9963f94e627198069cc27bc822a84e320'
    nb = pynetbox.api(
        url=url,
        token=token
    )
    return nb


def get_ospf_neighbors(host, case=None):
    '''
    Function to return all ospf neighbors of a host
    :param host:
    :param case: ID to update the case information in the psql database
    :return: a list of hostnames
    '''
    # custom field on ip address to poll ospf area
    nb = connect()
    host = str(host)
    ospf_nb = []
    neighborip = nb.ipam.ip_addresses.filter(device=host)
    for nbip in neighborip:
        if nbip.custom_fields["OSPF_area"] is not None:
            ospf_nb.append(nbip.custom_fields["OSPF_area"])
    if case:
        sol = 'Got OSPF neighbors of ' + host
        oatspsql.update_case(case_id=case, solution=sol)
    return ospf_nb


def get_vrf_ip(host):
    '''
    Function to get a custom field on the device in netbox which specifies the management ip address
    :param host: hostname
    :return: ip address of the management ip address
    '''
    # custom field on device to poll salt master
    nb = connect()
    host = str(host)
    ip = nb.dcim.devices.filter(host)
    vrfip = ip[0].custom_fields["Salt"]
    return vrfip


def get_interface_neighbor(host, interface, case=None):
    '''
    Function to return the neighbor of a device behind a certain interface
    :param host: hostname
    :param interface: name of the interface
    :param case: ID to update the case information in the psql database
    :return: hostname of the neighbor as string
    '''
    nb = connect()
    host = str(host)
    neighbor = ''
    neighborif = nb.dcim.interface_connections.filter(device=host)
    for nbif in neighborif:
        if nbif.interface_a.name == interface and nbif.interface_a.device.name != host:
            neighbor = nbif.interface_a.device.name
        elif nbif.interface_b.name == interface and nbif.interface_b.device.name != host:
            neighbor = nbif.interface_b.device.name
    if case:
        sol = 'Got neighbor of ' + host + ' on interface: ' + interface
        oatspsql.update_case(case_id=case, solution=sol)
    return neighbor


def get_neighbors(host, case=None):
    '''
    Function to return all neigbors of a host
    :param host: the hostname
    :param case: ID to update the case information in the psql database
    :return: list of the hostname of all neighbors
    '''
    nb = connect()
    host = str(host)
    neighbors = []
    neighborif = nb.dcim.interface_connections.filter(device=host)
    for nbif in neighborif:
        if nbif.interface_b.device.name == host:
            neighbors.append(nbif.interface_a.device.name)
        else:
            neighbors.append(nbif.interface_b.device.name)
    if case:
        sol = 'Got neighbors of ' + host
        oatspsql.update_case(case_id=case, solution=sol)
    return neighbors
