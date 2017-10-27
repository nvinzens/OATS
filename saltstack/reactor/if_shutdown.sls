shutdown_interface:
  local.net.load_template:
    - tgt:
    - kwarg:
        template_name: /etc/salt/template/shut_interface.jinja
        interface_name:
