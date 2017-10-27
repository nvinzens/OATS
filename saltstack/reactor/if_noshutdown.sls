shutdown_interface:
  local.net.load_template:
    - tgt:
    - kwarg:
        template_name: /etc/salt/template/noshut_interface.jinja
        interface_name:
