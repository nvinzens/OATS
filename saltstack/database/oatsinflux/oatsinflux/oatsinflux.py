#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
import jmespath

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


def connect_influx_client(host=None, port=None, user=None, password=None, dbname=None):
    if not host:
        host = 'localhost'
    if not port:
        port = 8086
    if not user:
        user = 'root'
    if not password:
        password = 'root'
    if not dbname:
        dbname = 'example'
    client = InfluxDBClient(host, port, user, password, dbname)

    return client


def write_event(host, timestamp, type, event_name, severity, data, db=None, client=None):

    if not db:
        db = 'timedb'
    if not client:
        client = connect_influx_client(host=None, port=None, user=None, password=None, dbname=db)

    try:
        if type == 'syslog':
            __write_syslog(host, timestamp, type, event_name, severity, data, client)
        elif type == 'api':
            __write_api(host, timestamp, type, event_name, severity, data, client)
        elif type == 'netflow':
            __write_netflow(host, timestamp, type, event_name, severity, data, client)
        elif type == 'streaming-telemetry':
            __write_stream(host, timestamp, type, event_name, severity, data, client)
        else:
            raise ValueError('Invalid Event Type')
    except Exception as error:
        print('Caught this error: ' + repr(error))


def __write_syslog(host, timestamp, type, event_name, severity, data, client):

    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_data"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(type)
    metrics['tags']['event_name'] = str(event_name)
    metrics['time'] = timestamp
    metrics['fields']['severity'] = severity
    metrics['fields']['error'] = data['error']
    metrics['fields']['os'] = data['os']

    data_nested = data["yang_message"]
    metrics['fields']['interface'] = __get_syslog_interface(data_nested)[0]
    metrics['fields']['neighbor'] = __get_syslog_neighbor(data_nested)[0]
    metrics['fields']['state_change'] = __get_state_change(data_nested)
    metrics['fields']['state_change_msg'] = __get_state_change_msg(data_nested)

    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print err.args

    return success


def __get_state_change_msg(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v.get('adjacency-state-change-reason-message') is not None:
                return v['adjacency-state-change-reason-message']
            return ''
        if v:
            return __get_state_change_msg(v)
        else:
            return ''


def __get_state_change(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            if v['adjacency-state']:
                return v['adjacency-state']
            return ''
        if v:
            return __get_state_change(v)
        else:
            return ''


def __get_syslog_interface(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'interface':
            return v.keys()
        if v:
            return __get_syslog_interface(v)
        else:
            return ''


def __get_syslog_neighbor(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'interface':
            return v.keys()
        if v:
            return __get_syslog_neighbor(v)
        else:
            return ''


def __write_api(host, timestamp, type, event_name, severity, data, client):

    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_data"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(type)
    metrics['tags']['event_name'] = str(event_name)
    metrics['time'] = timestamp
    metrics['fields']['severity'] = severity

    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print err.args

    return success


def __write_netflow(host, timestamp, type, event_name, severity, data, client):

    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_data"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(type)
    metrics['tags']['event_name'] = str(event_name)
    metrics['time'] = timestamp
    metrics['fields']['severity'] = severity
    for netflow in data["DataSets"][0]:
        metrics['fields'][netflow["I"]] = netflow["V"]

    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print err.args

    return success


def __write_stream(host, timestamp, type, event_name, severity, data, client):

    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_data"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(type)
    metrics['tags']['event_name'] = str(event_name)
    metrics['time'] = timestamp
    metrics['fields']['severity'] = severity

    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print err.args

    return success


def write(measurement, host, interface, region, value, time=None, db=None, client=None):

    if not db:
        db = 'timedb'
    if not client:
        client = connect_influx_client(host=None, port=None, user=None, password=None, dbname=db)

    measure = measurement
    device = host
    intf = interface
    reg = region
    val = value
    success = False

    if not time:
        point = [
            {
                "measurement": measure,
                "tags": {
                    "host": device,
                    "interface": intf,
                    "region": reg
                },
                "fields": {
                    "value": val
                }
            }
        ]
    else:
        point = [
            {
                "measurement": measure,
                "tags": {
                    "host": device,
                    "interface": intf,
                    "region": reg
                },
                "time": time,
                "fields": {
                    "value": val
                }
            }
        ]
    try:
        success = client.write_points(point)

    except Exception, e:

        print(str(e))

    client.close()

    return success
