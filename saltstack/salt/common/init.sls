/etc/hosts:
  file.managed:
    - name: /etc/hosts
    - source: salt://common/hosts
    - user: root
    - group: root
    - mode: 644

set module:
  file.managed:
    - name: /srv/saltstack/salt/_modules/tshoot.py
    - source: /home/sa/oats/SA_AT/saltstack/salt/_modules/tshoot.py
    - user: root
    - group: root
    - mode: 644

