{% set event_data = data['data'] %}

ping_and_run_state:
  local.ifdown_state.ping:
    - tgt: {{ event_data['device'] }}
