#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
import time

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

    milli = data["message_details"]["milliseconds"]
    millis = milli + '000000'
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S'+millis, time.localtime(timestamp))

    metrics['fields']['severity'] = severity
    metrics['fields']['error'] = data['error']
    metrics['fields']['os'] = data['os']

    data_nested = data["yang_message"]
    metrics['fields']['interface'] = __get_syslog_interface(data_nested)[0]
    metrics['fields']['neighbor'] = __get_syslog_neighbor(data_nested)[0]

    state_msgs = __get_state_msg(data_nested)
    for k,v in state_msgs.items():
        metrics['fields'][str(k)] = str(v)
        
    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print (err.args)

    return success


def __get_state_msg(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            return v
        if v:
            return __get_state_msg(v)
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
        print (err.args)

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

    nano = '000000000'
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S'+nano, time.localtime(timestamp))
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
        print (err.args)

    return success


def __write(measurement, host, interface, region, value, time=None, db=None, client=None):

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
