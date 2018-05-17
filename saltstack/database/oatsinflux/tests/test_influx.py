#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
from oatsinflux import oatsinflux
import datetime

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


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


def test_event():
    return True


def test_syslog():
    return True


def test_syslog_helpers():
    return True


def test_netflow():
    return True


def test_stream():
    return True


def test_api():
    return True