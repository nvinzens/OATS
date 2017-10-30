#invoke_orchestrate_file:
#  runner.state.orchestrate:
#    - args:
#      - mods: orchestrate.activate_interface
#      - pillar:
#          event_tag: {{ tag }}
#          event_data: {{ data['data']|json }}
{% set data = data['data'] %}
activate_remote_interface:
  local.net.ping:
    - tgt: {{ data['device'] }}
    - arg:
      - 192.168.50.10
    #- text: 'interface {{ data['interface'] }} no shutdown'

#no_shutdown_interface:
#  local.net.load_template:
#    - tgt: {{ data['device']}}
#    - kwarg:
#        template_name: /etc/salt/template/noshut_interface.jinja
#        interface_name:
