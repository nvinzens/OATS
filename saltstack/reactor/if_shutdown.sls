{% set data = data['data'] %}
shutdown_interface:
  local.net.load_template:
    - tgt: {{ data['device'] }}
    - kwarg:
        template_name: /etc/salt/template/shut_interface.jinja
        interface_name: {{ data['interface'] }}
