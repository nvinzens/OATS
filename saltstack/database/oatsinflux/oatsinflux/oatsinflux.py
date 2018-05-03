#!/usr/bin/env python2.7
from influxdb import InfluxDBClient

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
    #metrics['fields']['interface'] = syslog['yang_message']["network-instances"]["network-instance"]["global"]
    # ["protocols"]["protocol"]
    #metrics['fields']['neighbor'] =
    #metrics['fields']['state'] =

    try:
        success = client.write_points([metrics])
    except AttributeError as err:
        print err.args

    return success


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
    metrics['fields']['58'] = data["DataSets"][0][0]["V"]
    metrics['fields']['56'] = data["DataSets"][0][1]["V"]
    metrics['fields']['80'] = data["DataSets"][0][2]["V"]
    metrics['fields']['8'] = data["DataSets"][0][3]["V"]
    metrics['fields']['12'] = data["DataSets"][0][4]["V"]
    metrics['fields']['7'] = data["DataSets"][0][5]["V"]
    metrics['fields']['11'] = data["DataSets"][0][6]["V"]
    metrics['fields']['6'] = data["DataSets"][0][7]["V"]
    metrics['fields']['10'] = data["DataSets"][0][8]["V"]
    metrics['fields']['14'] = data["DataSets"][0][9]["V"]
    metrics['fields']['61'] = data["DataSets"][0][10]["V"]
    metrics['fields']['1'] = data["DataSets"][0][11]["V"]
    metrics['fields']['2'] = data["DataSets"][0][12]["V"]
    metrics['fields']['152'] = data["DataSets"][0][13]["V"]
    metrics['fields']['153'] = data["DataSets"][0][14]["V"]
    metrics['fields']['352'] = data["DataSets"][0][15]["V"]
    metrics['fields']['5'] = data["DataSets"][0][16]["V"]
    metrics['fields']['4'] = data["DataSets"][0][17]["V"]

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
