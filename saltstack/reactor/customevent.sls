install lftp on master.minion:
  local.pkg.install:
    - tgt: 'master'
    - arg:
      - lftp
#invoke_orchestrate_file:
#  runner.state.orchestrate:
#    - args:
#      - mods: orchestrate.activate_interface
#      - pillar:
#          event_tag: {{ tag }}
#          event_data: {{ data['data']|json }}

    #- text: 'interface {{ data['interface'] }} no shutdown'
