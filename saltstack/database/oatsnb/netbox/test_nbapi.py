#!/usr/bin/env python2.7
import pynetbox
from oatspsql import oatspsql


def connect(url=None, token=None):
    if not url:
        url = 'http://152.96.193.117:8000'
    if not token:
        token = '427aa3baf14652867311f7421a6aa4aa192c59fe'
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


def test_connect():
    test_nb = None
    test_nb = connect()
    assert test_nb is not None


def test_device():
    test_nb = connect()
    host = 'R11'
    dev = test_nb.dcim.devices.filter(name='R11')
    assert host == str(dev[0])


def test_ospf_neighbors():
    test_nb = connect()
    host = 'R11'
    ospf = None
    ospf = get_ospf_neighbors(host=host)
    assert ospf is not None


def test_neighbors():
    test_nb = connect()
    host = 'R11'
    neighbor = []
    neighbor = get_neighbors(host=host)
    assert len(neighbor) != 0


def test_interface_neighbor():
    test_nb = connect()
    host = 'R11'
    interface = 'GigabitEthernet2.13'
    neighbor = ''
    neighbor = get_interface_neighbor(host=host, interface=interface)
    assert neighbor == 'R13'


def test_vrf_ip():
    test_nb = connect()
    host = 'R11'
    salt = '10.20.1.11'
    vrf = ''
    vrf = get_vrf_ip(host=host)
    assert vrf == salt
