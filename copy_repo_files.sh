#!/bin/sh
# Copies the files from the SA_AT Git repo to the right folders
# /etc is used for configuration files
# /usr/local/bin for binaries (executables)
echo Start of the Script
echo Copy Saltstack folder
mkdir /etc/oats
mkdir /etc/napalm
mkdir /srv/saltstack
mkdir /usr/local/bin/oats
mkdir /usr/local/bin/oats/telemetry
mkdir /usr/local/bin/oats/kafka
mkdir /usr/local/bin/oats/kafka-streams
mkdir /usr/local/bin/oats/napalm-logs
cp -r ./systemd/. /lib/systemd/system
cp -r ./kafka/. /usr/local/bin/oats/kafka
cp -r ./telemetry/. /usr/local/bin/oats/telemetry
cp -r ./napalm/scripts/. /usr/local/bin/oats/napalm-logs
cp ./streaming_clients/buffer.client/classes/artifacts/buffer_client_jar/buffer.client.jar /usr/local/lib/kafka-streams/buffer.client.jar
cp config.yaml /etc/oats/config.yaml
cp -r ./saltstack/. /srv/saltstack
cp ./napalm/logs/conf/napalm-logs.conf /etc/napalm/logs
cp -r ./napalm/scripts/. /etc/napalm/scripts
cp -r ./saltstack/etc/. /etc/salt
cp -r ./napalm/logs/ios/. /usr/local/lib/python2.7/dist-packages/napalm_logs/config/ios/
echo all finished

