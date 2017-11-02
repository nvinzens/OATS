{% set data = data['data'] %}
no_shutdown_interface:
  local.net.load_template:
    - tgt: {{ data['device'] }}
    - kwarg:
        template_name: /etc/salt/template/noshut_interface.jinja
        interface_name: {{ data['interface']}}
