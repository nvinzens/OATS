#!/bin/sh

sudo apt-get update

sudo apt-get install -y python2.7 python-dev python-setuptools build-essential libxml2-dev libxslt1-dev libffi-dev graphviz libpq-dev libssl-dev zlib1g-dev

sudo mkdir -p /opt/netbox/

sudo apt-get install -y git

cd /opt/netbox/ && sudo git clone -b master https://github.com/digitalocean/netbox.git .

cd /opt/netbox/ && sudo pip install -r requirements.txt

sudo cp /home/vagrant/OATS/vagrant/configuration.py /opt/netbox/netbox/netbox

cd /opt/netbox/netbox/ &&  sudo python manage.py migrate

cd /opt/netbox/netbox/ &&  sudo python -y manage.py collectstatic --no-input