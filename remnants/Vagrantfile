# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. Please don't change it
# unless you know what you're doing.

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  net_ip = "192.168.50"
  routers = ['router1']
  config.vm.provider "virtualbox" do |v|
    v.memory = 8192
  end

  config.vm.define :at_server do |at_server|
    at_server.vm.box = "ubuntu/trusty64"
    at_server.vm.host_name = "at.server"
    at_server.vm.network "private_network", ip: "#{net_ip}.10"

    at_server.vm.synced_folder "saltstack", "/srv"
    at_server.vm.synced_folder "saltstack/reactor", "/etc/salt/reactor"
    at_server.vm.synced_folder "saltstack/template", "/etc/salt/template"
    at_server.vm.synced_folder "napalm", "/srv/napalm"

    # install napalm dependencies
    at_server.vm.provision "shell",
      inline: "sudo apt-get update && sudo apt-get install -y --force-yes libssl-dev libffi-dev python-dev python-cffi"
    # install pip & setuptools
    at_server.vm.provision "shell",
      inline: "sudo apt-get install -y python-pip python-dev build-essential"
    at_server.vm.provision "shell",
      inline: "sudo pip install --upgrade pip"
    at_server.vm.provision "shell",
      inline:"sudo pip install --upgrade virtualenv"
    at_server.vm.provision "shell",
      inline: "sudo pip install setuptools"
    at_server.vm.provision "shell",
      inline: "sudo pip install --upgrade setuptools"
    #install napalm & napalm-logs
    at_server.vm.provision "shell",
      inline: "sudo pip install napalm"
    at_server.vm.provision "shell",
      inline: "sudo pip install napalm-logs"
    #install mongodb and pymongo
    at_server.vm.provision "shell",
      inline: "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6"
    at_server.vm.provision "shell",
      inline: "echo 'deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list"
    at_server.vm.provision "shell",
      inline: "sudo apt-get update"
    at_server.vm.provision "shell",
      inline: "sudo apt-get install -y mongodb-org"
    at_server.vm.provision "shell",
      inline: "python -m pip install pymongo"
    #import example data
    at_server.vm.provision "shell",
      inline: "mongoimport --db oatsdb --collection cases --drop --file /srv/database/test_db/caselist.json"
    at_server.vm.provision "shell",
      inline: "mongoimport --db oatsdb --collection network --drop --file /srv/database/test_db/networkdata.json"
    at_server.vm.provision "shell",
      inline: "mongoimport --db oatsdb --collection technician --drop --file /srv/database/test_db/technician.json"

      at_server.vm.provision :salt do |salt|
        salt.master_config = "saltstack/etc/master"
        salt.minion_config = "saltstack/etc/minion"

        salt.master_key = "saltstack/keys/master_minion.pem"
        salt.master_pub = "saltstack/keys/master_minion.pub"
        salt.minion_key = "saltstack/keys/master_minion.pem"
        salt.minion_pub = "saltstack/keys/master_minion.pub"

        salt.seed_master = {
                            "master" => "saltstack/keys/master_minion.pub"
                           }

        salt.install_type = "stable"
        # salt.install_args = "develop" //use only for install_type=git
        salt.verbose = true
        salt.colorize = true
        salt.install_master = true
        salt.no_minion  = false
        salt.bootstrap_options = "-P -c /tmp"

        salt.run_highstate = true

      end
    end
  end
