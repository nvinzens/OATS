set napalm-logs configuration file:
  file.managed:
    - name: /etc/napalm/logs
    - source: /home/sa/oats/napalm/logs/conf/napalm-logs.conf
    - order: 1