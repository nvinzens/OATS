#!/bin/sh

sudo apt-get update

echo "Add the InfluxData repository"
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

echo "Install and start the InfluxDB service:"
sudo apt-get update && sudo apt-get install influxdb
sudo systemctl start influxdb

echo "Point the process to the correct configuration file by using the -config option:"
influxd -config /etc/influxdb/influxdb.conf

echo "Set the environment variable INFLUXDB_CONFIG_PATH to the path of your configuration file and start the process."
echo $INFLUXDB_CONFIG_PATH
/etc/influxdb/influxdb.conf

influxd