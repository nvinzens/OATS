{% set event_data = data['data'] %}

ping_and_run_state:
  local.ifdown_state.workflow:
    - tgt: {{ event_data['device'] }}
    - arg:
      - {{ event_data['interface'] }}
      - {{ event_data['device'] }}

