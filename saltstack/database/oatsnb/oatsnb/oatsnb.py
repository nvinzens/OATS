#!/usr/bin/env python2.7
import pynetbox
from oatspsql import oatspsql


def connect(url=None, token=None):
    if not url:
        url = 'http://10.20.1.10'
    if not token:
        token = '20b9f6f9963f94e627198069cc27bc822a84e320'
    nb = pynetbox.api(
        url=url,
        token=token
    )
    return nb


def get_ospf_neighbors(host, case=None, test=False):
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


def get_vrf_ip(host, test=False):
    # custom field on device to poll salt master
    nb = connect()
    host = str(host)
    ip = nb.dcim.devices.filter(host)
    vrfip = ip[0].custom_fields["Salt"]
    return vrfip


def get_interface_neighbor(host, interface, case=None, test=False):
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


def get_neighbors(host, case=None, test=False):
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
