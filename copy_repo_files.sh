#!/bin/sh
# Copies the files from the SA_AT Git repo to the right folders
echo Start of the Script
echo Copy Saltstack folder
cp -r ./saltstack/. /srv/saltstack
cp -r ./napalm/. /etc/napalm
cp -r ./saltstack/etc/. /etc/salt
cp -r ./napalm/logs/conf/napalm-logs.conf /etc/napalm/logs/
cp -r ./napalm/logs/ios/. /usr/local/lib/python2.7/dist-packages/napalm_logs/config/ios/
echo all finished

