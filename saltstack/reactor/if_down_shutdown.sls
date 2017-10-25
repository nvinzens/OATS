shutdown_interface:
  local.net.load_template:
    - tgt: 
    - kwarg:
        template_name: /etc/salt/shut_interface.jinja
        interface_name:
