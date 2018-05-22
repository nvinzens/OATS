#!/bin/sh
# Copies the files from the OATS Git repo to the right folders
# /etc is used for configuration files
# /usr/local/bin for binaries (executables)
echo "starting oats bootstrap..."

if [  ! -d "/etc/oats" ]; then
    echo "creating /etc/oats..."
    mkdir /etc/oats
fi

echo "setting up oats config..."
cp config.yaml /etc/oats/config.yaml

if [  ! -d "/etc/napalm" ]; then
    echo "creating /etc/napalm..."
    mkdir "/etc/napalm"
fi
echo "copying default oats napalm-logs configuration to /etc/napalm"
cp ./napalm/logs/conf/napalm-logs.conf /etc/napalm/logs

if [ ! -d "/srv/saltstack" ]; then
    echo "creating /srv/saltstack..."
    echo "copying salt files to /srv/saltstack"
    cp -r ./saltstack/. /srv/saltstack
fi

if [ ! -d "/usr/local/bin/oats" ]; then
    echo "creating oats binary directory /usr/local/bin/oats"
    mkdir "/usr/local/bin/oats"
fi

echo "copying telemetry binaries to /usr/local/bin/oats"
cp -r ./telemetry/. /usr/local/bin/oats/telemetry

echo "copying telemetry binaries to /usr/local/bin/oats"
cp -r ./telemetry/. /usr/local/bin/oats/telemetry

echo "copying kafka consumer binaries to /usr/local/bin/oats"
cp -r ./kafka/. /usr/local/bin/oats/kafka

echo "copying napalm-logs client binaries to /usr/local/bin/oats"
cp -r ./napalm/scripts/. /usr/local/bin/oats/napalm-logs

echo "copying oats-api client to /usr/local/bin/oats"
cp -r ./oats_api/ /usr/local/bin/oats/oats-api

if [ ! -d "/usr/local/bin/oats/kafka-streams" ]; then
    echo "copying kafka-streams binaries to /usr/local/bin/oats"
    mkdir "/usr/local/bin/oats/kafka-streams"
fi
cp ./streaming_clients/oats-generic-kafka-streams/classes/artifacts/oats_generic_kafka_streams_jar/oats-generic-kafka-streams.jar /usr/local/bin/oats/kafka-streams/oats-generic-kafka-streams.jar

echo "setting up oats systemd files..."
cp -r ./systemd/. /lib/systemd/system
systemctl daemon-reload

# do not overwrite slack key
#echo "setting up oats salt configuration..."
#cp -r ./saltstack/etc/. /etc/salt

echo "installing napalm-logs ios profiles..."
cp -r ./napalm/logs/ios/. /usr/local/lib/python2.7/dist-packages/napalm_logs/config/ios/

echo "installing oats specific fork of ncclient"
pip install --upgrade git+https://github.com/nvinzens/ncclient.git

echo "oats bootstrap done"



