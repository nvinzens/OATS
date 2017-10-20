/etc/salt/proxy:
  file.managed:
    - name: /etc/salt/proxy
    - source: salt://napalm_proxy/proxy.conf
    - user: root
    - group: root
    - mode: 644

salt-proxy-configure-router1:
  salt_proxy.configure_proxy:
    - proxyname: router1
    - start: True
    - require:
      - pip: napalm-ios

python-pip:
  pkg.installed

python-dev:
  pkg.installed

python-cffi:
  pkg.installed

libxslt1-dev:
  pkg.installed

libffi-dev:
  pkg.installed

libssl-dev:
  pkg.installed

napalm-ios:
  pip.installed:
    - name: napalm-ios
    - require:
      - pkg: python-pip
      - pkg: python-dev
      - pkg: python-cffi
      - pkg: libxslt1-dev
      - pkg: libffi-dev
      - pkg: libssl-dev
