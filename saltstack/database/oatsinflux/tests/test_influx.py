#!/usr/bin/env python2.7
from influxdb import InfluxDBClient
from oatsinflux import oatsinflux
import datetime
import pytest
import time

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


def helper_data():
    data = {
        "yang_message": {
            "interface": {
                "test_interface": {
                    "neighbor": {
                        "test_neighbor": {
                            "state": {
                                "adjacency-state": "DOWN"
                            }
                        }
                    }
                }
            }
        }
    }
    return data


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

    success = oatsinflux.__write(measurement=measure, host=host, interface=interface, region=reg, value=val, time=None, db=db, client=cl)

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

    success = oatsinflux.__write(measurement=measure, host=host, interface=interface, region=reg, value=val, time=time, db=db, client=cl)

    cl.drop_database(db)

    cl.close()

    assert success is True


def test_event_exception():
    data = {"data": "test"}
    with pytest.raises(Exception) as excinfo:
        oatsinflux.write_event(host='test', timestamp=int(time.time()), sensor_type='test', event_name='test',
                               severity=1, data=data)
    assert str(excinfo.value) == 'Invalid Event Type'


def test_syslog():
    db = 'test'
    data = {"yang_message": {"network-instances": {"network-instance": {"global": {"protocols": {"protocol": {"ospf":
            {"ospfv2": {"areas": {"area": {"area": {"interfaces": {"interface": {"GigabitEthernet2.35": {"neighbors":
            {"neighbor": {"172.16.56.5": {"state": {"adjacency-state": "DOWN"}}}}}}}}}}}}}}}}}},
            "message_details": {"severity": 5, "facility": 23, "time": "06:06:02", "pri": "189", "host": "R13", "tag":
                "OSPF-5-ADJCHG", "messageId": "807", "date": "May  2", "message":
                "Nbr 172.16.56.5 on GigabitEthernet2.35 from INIT to DOWN, Neighbor Down: Dead timer expired",
                "milliseconds": ".617", "processnumber": "1"}, "facility": 23, "ip": "10.20.1.13", "error":
                "OSPF_NEIGHBOR_DOWN", "host": "R13", "yang_model": "openconfig-ospf", "timestamp": 1525241162, "os":
                "ios", "severity": 5}

    cl = oatsinflux.connect_influx_client(dbname=db)
    cl.create_database(db)
    success = oatsinflux.__write_syslog(host='test', timestamp=int(time.time()), sensor_type='test', event_name='test',
                               severity=1, data=data, client=cl)
    cl.drop_database(db)
    cl.close()
    assert success is True


def test_syslog_helpers():
    data = helper_data()
    interface = oatsinflux.__get_syslog_interface(data)
    neighbor = oatsinflux.__get_syslog_neighbor(data)
    state_msg = oatsinflux.__get_state_msg(data)
    assert interface[0] == "test_interface" and neighbor[0] == "test_neighbor" \
           and state_msg['adjacency-state'] == "DOWN"


def test_netflow():
    db = 'test'
    data = {"AgentID":"10.20.1.22","Header":{"Version":9,"Count":3,"SysUpTime":169636000,"UNIXSecs":1525209942,
            "SeqNum":9688,"SrcID":16777217},"DataSets":[[{"I":58,"V":22},
            {"I":56,"V":"00:19:99:b3:92:bd"},{"I":80,"V":"00:19:99:b3:93:df"},{"I":8,"V":"192.168.1.10"},
            {"I":12,"V":"192.168.1.11"},{"I":7,"V":0},{"I":11,"V":0},{"I":6,"V":"0x00"},{"I":10,"V":10},
            {"I":14,"V":0},{"I":61,"V":0},{"I":1,"V":989527440},{"I":2,"V":725460},{"I":152,"V":1525209888587},
            {"I":153,"V":1525209926587},{"I":352,"V":1002585720},{"I":5,"V":0},{"I":4,"V":17}],[{"I":58,"V":22},
            {"I":56,"V":"00:19:99:b3:92:bd"},{"I":80,"V":"00:19:99:b3:93:df"},{"I":8,"V":"192.168.1.10"},
            {"I":12,"V":"192.168.1.11"},{"I":7,"V":35464},{"I":11,"V":5201},{"I":6,"V":"0x00"},{"I":10,"V":10},
            {"I":14,"V":0},{"I":61,"V":0},{"I":1,"V":217638046},{"I":2,"V":145093},{"I":152,"V":1525209888587},
            {"I":153,"V":1525209926587},{"I":352,"V":220249720},{"I":5,"V":0},{"I":4,"V":17}]]}
    cl = oatsinflux.connect_influx_client(dbname=db)
    cl.create_database(db)
    timestamp = int(time.time()) * 1000
    success = oatsinflux.__write_stream(host='test', timestamp=timestamp, sensor_type='test', event_name='test',
                                        severity=1, data=data, client=cl)
    cl.drop_database(db)
    cl.close()
    assert success is True


def test_stream():
    db = 'test'
    data = '{"name":"GigabitEthernet1/0/1","value":3383114216}'
    cl = oatsinflux.connect_influx_client(dbname=db)
    cl.create_database(db)
    timestamp = int(time.time()) * 1000
    success = oatsinflux.__write_stream(host='test', timestamp=timestamp, sensor_type='test', event_name='test',
                                        severity=1, data=data, client=cl)
    cl.drop_database(db)
    cl.close()
    assert success is True


def test_api():
    data = 0
    db = 'test'
    cl = oatsinflux.connect_influx_client(dbname=db)
    cl.create_database(db)
    timestamp = int(time.time())
    success = oatsinflux.__write_stream(host='test', timestamp=timestamp, sensor_type='test', event_name='test',
                                        severity=1, data=data, client=cl)
    cl.drop_database(db)
    cl.close()
    assert success is True
