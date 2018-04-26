#!/usr/bin/env python2.7
import pynetbox
from oatspsql import oatspsql
from oatsnb import oatsnb


def test_connect():
    test_nb = None
    test_nb = oatsnb.connect()
    assert test_nb is not None


def test_device():
    test_nb = oatsnb.connect()
    host = 'R11'
    dev = test_nb.dcim.devices.filter(name='R11')
    assert host == str(dev[0])


def test_ospf_neighbors():
    test_nb = oatsnb.connect()
    host = 'R11'
    ospf = None
    ospf = oatsnb.get_ospf_neighbors(host=host)
    assert ospf is not None


def test_neighbors():
    test_nb = oatsnb.connect()
    host = 'R11'
    neighbor = []
    neighbor = oatsnb.get_neighbors(host=host)
    assert len(neighbor) != 0


def test_interface_neighbor():
    test_nb = oatsnb.connect()
    host = 'R11'
    interface = 'GigabitEthernet2.13'
    neighbor = ''
    neighbor = oatsnb.get_interface_neighbor(host=host, interface=interface)
    assert neighbor == 'R13'


def test_vrf_ip():
    test_nb = oatsnb.connect()
    host = 'R11'
    salt = '10.20.1.11'
    vrf = ''
    vrf = oatsnb.get_vrf_ip(host=host)
    assert vrf == salt
