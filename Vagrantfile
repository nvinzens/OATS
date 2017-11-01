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
    at_server.vm.synced_folder "saltstack/etc/minion.d", "/etc/salt/minion.d"
    at_server.vm.synced_folder "napalm", "/srv/napalm"

    #increase performance?

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
      #  salt.install_args = "develop"
        salt.verbose = true
        salt.colorize = true
        salt.install_master = true
        salt.no_minion  = false
        salt.bootstrap_options = "-P -c /tmp"

        salt.run_highstate = true

      end
    end
  end

      # Install Cherrypy and run salt-api
      #at_system.vm.provision "shell",
      #  inline: "sudo apt-get update && sudo apt-get install python-pip -y"
      #at_system.vm.provision "shell",
      #  inline: "sudo pip install cherrypy"
      #at_system.vm.provision "shell",
      #  inline: "sudo salt-api -d"

      # Set ubuntu password for api access
      #at_system.vm.provision "shell",
      #  inline: "sudo echo 'ubuntu:1234' | sudo chpasswd"
      # install ZeroMQ
      #inline: "sudo apt-get install libtool pkg-config build-essential autoconf automake"
      #inline: "sudo apt-get install libzmq-dev"
      #inline:  "git clone git://github.com/jedisct1/libsodium.git"
      #inline: "cd libsodium"
      #inline: "./autogen.sh"
      #inline: "./configure && make check"
      #inline: "sudo make install"
      #inline: "sudo ldconfig"
      #inline: "wget http://download.zeromq.org/zeromq-4.2.2.tar.gz"
      #inline: "tar -xvf zeromq-4.2.2.tar.gz"
      #inline: "cd zeromq-4.2.2"
      #inline: "./autogen.sh"
      #inline: "./configure && make check"
      #inline: "sudo make install"
      #inline: "sudo ldconfig"

    # nuts.vm.provision "shell",
      # inline: "git clone https://github.com/HSRNetwork/Nuts.git"
    # nuts.vm.provision "shell",
      # inline: "cd Nuts; sudo python setup.py install"


    # environment variable for nuts (settings)
    # nuts.vm.provision "shell",
      # inline: "echo 'export NUTS_SALT_REST_API_URL=http://192.168.100.100:8000' >> /home/ubuntu/.profile"
    # nuts.vm.provision "shell",
      # inline: "echo 'export NUTS_SALT_REST_API_USERNAME=ubuntu' >> /home/ubuntu/.profile"
    # nuts.vm.provision "shell",
      # inline: "echo 'export NUTS_SALT_REST_API_PASSWORD=1234' >> /home/ubuntu/.profile"
    # nuts.vm.provision "shell",
      # inline: "echo 'export NUTS_SALT_REST_API_EAUTH=pam' >> /home/ubuntu/.profile"


    #at_system.vm.synced_folder "at_system/testfiles/", "/home/ubuntu/testfiles"
    #at_server.vm.synced_folder "saltstack/master.d/", "/etc/salt/master.d"
    #at_system.vm.provision "shell",
    #  inline: "sudo apt-get update && sudo apt-get install python-git -y"
    #at_system.vm.provision "shell",
    #  inline: "sudo apt-get update && sudo apt-get install_typestall python-pip -y"
