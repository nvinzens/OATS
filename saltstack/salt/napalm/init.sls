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
    - order: 1

set napalm proxy beacon:
  file.managed:
    - name: /etc/salt/minion.d/beacons.conf
    - source: /srv/etc/minion.d/beacons.conf

Run restart_minion:
  cmd.script:
    - name: /srv/scripts/restart_minion.sh
    - user: root
    - group: root
    - shell: /bin/bash
    - order: last
