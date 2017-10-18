/etc/salt/proxy:
  file.managed:
    - name: /etc/salt/proxy
    - source: salt://napalm_proxy/proxy.conf
    - user: root
    - group: root
- mode: 644
