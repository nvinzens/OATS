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
