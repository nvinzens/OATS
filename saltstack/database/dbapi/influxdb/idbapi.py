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


def write(measurement, host, region, value, time=None, db=None):

    if not db:
        db = 'timedb'

    client = connect_influx_client(host=None, port=None, user=None, password=None, dbname=db)

    measure = measurement
    device = host
    reg = region
    val = value

    if not time:
        point = [
            {
                "measurement": measure,
                "tags": {
                    "host": device,
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
                    "region": reg
                },
                "time": time,
                "fields": {
                    "value": val
                }
            }
        ]
    try:
        client.write_points(point)

    except Exception, e:

        print(str(e))

    client.close()

    return measurement + ' ' + host + ' ' + region + ' ' + value + ' ' + str(time)
