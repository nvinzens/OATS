#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
from oatsinflux import oatsinflux
import datetime

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
        client = oatsinflux.connect_influx_client(host=None, port=None, user=None, password=None, dbname=db)

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


def test_connect():

    db = 'test'

    client = oatsinflux.connect_influx_client(dbname=db)

    client.create_database(db)

    point = [
        {
            "measurement": 'test',
            "tags": {
                "host": 'test_dev',
                "interface": 'test_port',
                "region": 'test_reg'
            },
            "fields": {
                "value": 1
            }
        }
    ]

    test_val = client.write_points(point)

    client.drop_database(db)

    client.close()

    assert test_val is True


def test_write_no_time():

    db = 'test'
    measure = 'test_ms'
    host = 'test_host'
    interface = 'test_port'
    reg = 'test_reg'
    val = 1

    cl = oatsinflux.connect_influx_client(dbname=db)

    cl.create_database(db)

    success = oatsinflux.write(measurement=measure, host=host, interface=interface, region=reg, value=val, time=None, db=db, client=cl)

    cl.drop_database(db)

    cl.close()

    assert success is True


def test_write_with_time():

    db = 'test'
    measure = 'test_ms'
    host = 'test_host'
    interface = 'test_port'
    reg = 'test_reg'
    time = datetime.datetime.utcnow()
    val = 1

    cl = oatsinflux.connect_influx_client(dbname=db)

    cl.create_database(db)

    success = oatsinflux.write(measurement=measure, host=host, interface=interface, region=reg, value=val, time=time, db=db, client=cl)

    cl.drop_database(db)

    cl.close()

    assert success is True
