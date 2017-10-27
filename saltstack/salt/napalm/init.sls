#Run install_dependencies:
#  cmd.run:
#    - name: /srv/scripts/install_dependencies.sh
#    - user: root
#    - group: root
#    - shell: /bin/bash

set napalm proxy configuration file:
  file.managed:
    - name: /etc/salt/proxy
    - source: /srv/etc/proxy
#napalm:
#  install:
#    - napalm-ios
