#!/usr/bin/env python2.7
from influxdb import InfluxDBClient

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


def write(measurement, host, region, value, time=None):

    client = InfluxDBClient(database='timedb')

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
