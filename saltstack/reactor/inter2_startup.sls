startup_interface_static:
  local.net.load_config:
    - tgt: router1
    - kwarg:
        interface_name: GigabitEthernet2
        #interface_COMAND???: no shutdown
        #ip_addr???: 192.168.50.12 255.255.255.0
