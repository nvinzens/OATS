Run install_dependencies:
  cmd.run:
    - name: /srv/scripts/install_dependencies.sh
    - user: root
    - group: root
    - shell: /bin/bash

salt-proxy-configure:
  salt_proxy.configure_proxy:
    - proxyname: router1
    - start: True # start the process if it isn't running
