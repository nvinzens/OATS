salt-proxy-configure:
  salt_proxy.configure_proxy:
    - proxyname: router1
    - start: True # start the process if it isn't running
