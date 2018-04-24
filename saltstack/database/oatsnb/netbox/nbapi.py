#!/usr/bin/env python2.7
import pynetbox


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

    return neighbors
