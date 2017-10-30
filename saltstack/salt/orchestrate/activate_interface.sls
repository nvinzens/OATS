{% set data = salt.pillar.get('event_data') %}

activate_remote_interface:
  local.net.load_config:
    - tgt: {{ data['device'] }}
    - text: 'interface {{ data['interface_name'] }} no shutdown'
#no_shutdown_interface:
#  local.net.load_template:
#    - tgt:
#    - kwarg:
#        template_name: /etc/salt/template/noshut_interface.jinja
#        interface_name:
