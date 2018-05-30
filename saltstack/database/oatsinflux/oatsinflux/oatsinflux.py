#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
from influxdb import exceptions
import time
import json

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


def connect_influx_client(host=None, port=None, user=None, password=None, dbname=None):
    '''
    Connects to an influxdb through a client.
    :param host: IP Address of the InfluxDB host.
    :param port: Port number of the InfluxDB on the Host.
    :param user: Username for InfluxDB
    :param password: Password for the specified user.
    :param dbname: Name of the specific Database on Influx.
    :return: The client with which one can write or read on the Influx Database.
    '''
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


def write_event(host, timestamp, sensor_type, event_name, severity, data, db=None, client=None):
    '''
    Public Function to write events onto Influx.
    :param host: Event host
    :param timestamp: Event timestamp
    :param sensor_type: Event sensortype
    :param event_name: Event name
    :param severity: Event severity
    :param data: Additional relevant data for the event, format varies between event types
    :param db: Name of the influxdb
    :param client: If a client is already present can use this one instead.
    :return:
    '''
    if not db:
        db = 'timedb'
    if not client:
        client = connect_influx_client(host=None, port=None, user=None, password=None, dbname=db)

    try:
        if sensor_type == 'syslog':
            __write_syslog(host, timestamp, sensor_type, event_name, severity, data, client)
        elif sensor_type == 'api':
            __write_api(host, timestamp, sensor_type, event_name, severity, data, client)
        elif sensor_type == 'netflow':
            __write_netflow(host, timestamp, sensor_type, event_name, severity, data, client)
        elif sensor_type == 'streaming-telemetry':
            __write_stream(host, timestamp, sensor_type, event_name, severity, data, client)
        else:
            raise ValueError('Invalid Event Type')
    except Exception as error:
        print('Caught this error: ' + repr(error))


def __write_syslog(host, timestamp, sensor_type, event_name, severity, data, client):
    '''
    Private function to write a syslog event.
    :param host: Event host
    :param timestamp: Event timestamp
    :param sensor_type: Event sensortype
    :param event_name: Event name
    :param severity: Event severity
    :param data: Contains Information about the relevant interface and its state, both have to be extracted from
    the data yang_message
    :param client:
    :return: success True/False
    '''
    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_syslog"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(sensor_type)
    metrics['tags']['event_name'] = str(event_name)

    milli = data["message_details"]["milliseconds"]
    millis = milli + '000000'
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S'+millis, time.gmtime(timestamp))

    metrics['fields']['severity'] = severity
    error = data['error']
    metrics['fields']['error'] = error
    metrics['fields']['os'] = data['os']

    data_nested = data["yang_message"]

    if str(error) == 'OSPF_NEIGHBOR_UP' or str(error) == 'OSPF_NEIGHBOR_DOWN':
        metrics['fields']['interface'] = __get_syslog_interface(data_nested)[0]
        metrics['fields']['neighbor'] = __get_syslog_neighbor(data_nested)[0]
    elif str(error) == 'INTERFACE_CHANGED':
        metrics['fields']['interface'] = __get_syslog_interface(data_nested)[0]

    state_msgs = __get_state_msg(data_nested)
    for k,v in state_msgs.items():
        metrics['fields'][str(k)] = str(v)
        if str(k) == 'oper_status':
            if str(v) == 'UP' or str(v) == 'up':
                metrics['fields']['if_state_id'] = 0
            else:
                metrics['fields']['if_state_id'] = 1
        elif str(k) == 'adjacency-state':
            if str(v) == 'UP' or str(v) == 'up':
                metrics['fields']['ospf_state_id'] = 0
            else:
                metrics['fields']['ospf_state_id'] = 1
    try:
        success = client.write_points([metrics])
    except (AttributeError, exceptions.InfluxDBClientError) as err:
        print ("Caught exception in oatsinflux.write_syslog" + err.args)

    return success


def __get_state_msg(yang_message):
    '''
    Helper Function for syslog write to extract the state
    :param yang_message: contains the relevant information
    :return: the state if successful or nothing if no state could be found
    '''
    for k, v in sorted(yang_message.items()):
        if k == 'state':
            return v
        if v:
            return __get_state_msg(v)
        else:
            return ''


def __get_syslog_interface(yang_message):
    '''
    Helper Function for syslog write to extract the interface
    :param yang_message: contains the relevant information
    :return: the interface if successful or nothing if no state could be found
    '''
    for k, v in sorted(yang_message.items()):
        if k == 'interface':
            return v.keys()
        if v:
            return __get_syslog_interface(v)
        else:
            return ''


def __get_syslog_neighbor(yang_message):
    '''
    Helper Function for syslog write to extract the ip address of the neighbor
    :param yang_message: contains the relevant information
    :return: the ip address if successful or nothing if no state could be found
    '''
    for k, v in sorted(yang_message.items()):
        if k == 'neighbor':
            return v.keys()
        if v:
            return __get_syslog_neighbor(v)
        else:
            return ''


def __write_api(host, timestamp, sensor_type, event_name, severity, data, client):
    '''
    Private function to write an api event.
    :param host: Event host
    :param timestamp: Event timestamp
    :param sensor_type: Event sensortype
    :param event_name: Event name
    :param severity: Event severity
    :param data: 0/1 to specifiy if something is wrong or not
    :param client:
    :return: success True/False
    '''
    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_api"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(sensor_type)
    metrics['tags']['event_name'] = str(event_name)
    nano = '.000000000'
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S' + nano, time.gmtime(timestamp))
    metrics['fields']['severity'] = severity
    metrics['fields']['data'] = data

    try:
        success = client.write_points([metrics])
    except (AttributeError, exceptions.InfluxDBClientError) as err:
        print ("Caught exception in oatsinflux.write_api " + err.args)

    return success


def __write_netflow(host, timestamp, sensor_type, event_name, severity, data, client):
    '''
    Private function to write a netflow event.
    :param host: Event host
    :param timestamp: Event timestamp
    :param sensor_type: Event sensortype
    :param event_name: Event name
    :param severity: Event severity
    :param data: yang message with all attached netflow data
    :param client:
    :return: success True/False
    '''
    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_netflow"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(sensor_type)
    metrics['tags']['event_name'] = str(event_name)

    nano = '.000000000'
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S'+nano, time.gmtime(timestamp))
    metrics['fields']['severity'] = severity
    for netflow in data["DataSets"][0]:
        metrics['fields'][netflow["I"]] = netflow["V"]

    try:
        success = client.write_points([metrics])
    except (AttributeError, exceptions.InfluxDBClientError) as err:
        print ("Caught exception in oatsinflux.write_netflow " + err.args)

    return success


def __write_stream(host, timestamp, sensor_type, event_name, severity, data, client):
    '''
    Private function to write a streaming telemetry event.
    :param host: Event host
    :param timestamp: Event timestamp
    :param sensor_type: Event sensortype
    :param event_name: Event name
    :param severity: Event severity
    :param data: yang message with all attached netflow data
    :param client:
    :return: success True/False
    '''
    success = False
    metrics = {}
    metrics['measurement'] = "oats_timeseries_streaming"
    metrics['tags'] = {}
    metrics['fields'] = {}
    metrics['tags']['host'] = str(host)
    metrics['tags']['type'] = str(sensor_type)
    metrics['tags']['event_name'] = str(event_name)

    time_string = str(timestamp)
    milli = time_string[-3:]
    millis = '.' + milli + '000000'
    epoch = timestamp / 1000
    metrics['time'] = time.strftime('%Y-%m-%d %H:%M:%S'+millis, time.gmtime(epoch))
    metrics['fields']['severity'] = severity
    data_json = json.loads(data)
    metrics['fields']['key'] = data_json['name']
    metrics['fields']['value'] = data_json['value']

    try:
        success = client.write_points([metrics])
    except (AttributeError, exceptions.InfluxDBClientError) as err:
        print ("Caught exception in oatsinflux.write_stream " + err.args)

    return success


def get_type_data(sensor_type, timestamp, event_name, timeframe, host=None, db_name=None):
    '''
    Function to read information from Influx
    :param sensor_type: which type of information should be queried
    :param timestamp: the relevant point in time
    :param event_name: the specific name of the event
    :param timeframe: amount of seconds before and after the timestamp, which are still relevant
    :param host: name of the host
    :param db_name: name of the influx database
    :return: A list of dictionaries
    '''
    measurement = None
    if not db_name:
        db_name = 'timedb'
    if sensor_type == 'syslog':
        measurement = 'oats_timeseries_syslog'
    elif sensor_type == 'api':
        measurement = 'oats_timeseries_api'
    elif sensor_type == 'netflow':
        measurement = 'oats_timeseries_netflow'
    elif sensor_type == 'streaming-telemetry':
        measurement = 'oats_timeseries_streamin'
    else:
        raise ValueError('Invalid Event Type')

    client = connect_influx_client(dbname=db_name) 

    timestamp = str(timestamp)
    if len(timestamp) == 13:
        timestamp = timestamp + 'ms'
    elif len(timestamp) == 10:
        timestamp = timestamp + 's'
    time_after = timestamp + ' + ' + str(timeframe) + 's'
    time_before = timestamp + ' - ' + str(timeframe) + 's'
    sql_query = "SELECT * from " + measurement + " WHERE time > " + time_before + " AND time < " + time_after
    rs = None
    try:
        rs = client.query(sql_query)
    except str(exceptions.InfluxDBClientError), e:
        print "Exception caught on get Type data query: " + e

    if host:
        results = list(rs.get_points(tags={"event_name": str(event_name), "host": str(host)}))
    else:
        results = list(rs.get_points(tags={"event_name": str(event_name)}))

    return results


def __write(measurement, host, interface, region, value, time=None, db=None, client=None):
    '''
    A basic influx write function for testing and as a base for new functions
    :param measurement: the type of information
    :param host: the relevant host
    :param interface: the host interface
    :param region: the region where the host is located
    :param value: the value which is to be entered into influx
    :param time: the timestamp
    :param db: name of the database
    :param client: if it exists the client
    :return:
    '''
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
