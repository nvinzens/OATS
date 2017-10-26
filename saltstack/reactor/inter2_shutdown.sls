shutdown_interface_static:
  local.net.load_config:
    - tgt: router1
    - kwarg:
        interface_name: GigabitEthernet2
        #interface_COMAND??: shutdown
