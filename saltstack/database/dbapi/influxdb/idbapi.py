#!/usr/bin/env python2.7
import sys
from influxdb import InfluxDBClient

# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')


def main():
    while 1:
        try:
            selection = raw_input('\nSelect 1 to create, E to end\n')

            if selection == '1':
                write('cpu_load_short', 'RTest', 'ins-lab', '1')
            elif selection == 'E':
                sys.exit()
            elif selection == 'e':
                sys.exit()
            else:
                print('\nINVALID SELECTION\n')
        except KeyboardInterrupt:
            sys.exit()


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

    print(measurement + ' ' + host + ' ' + region + ' ' + value + ' ' + str(time))

    client.close()


main()
