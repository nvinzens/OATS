set napalm-logs configuration file:
  file.managed:
    - name: /etc/napalm/logs
    - source: /home/sa/oats/SA_AT/napalm/logs/conf/napalm-logs.conf
    - user: root
    - group: root
    - mode: 644


set napalm-logs client script:
  file.managed:
    - name: /etc/napalm/scripts/client.py
    - source: /home/sa/oats/SA_AT/napalm/scripts/client.py
    - user: root
    - group: root
    - mode: 644


set napalm-logs salt events script:
  file.managed:
    - name: /etc/napalm/scripts/salt_events.py
    - source: /home/sa/oats/SA_AT/napalm/scripts/salt_events.py
    - user: root
    - group: root
    - mode: 644