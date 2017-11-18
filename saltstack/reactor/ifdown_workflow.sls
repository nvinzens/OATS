{% set event_data = data['data'] %}

ping_and_run_state:
  local.tshoot.ifdown:
    - tgt: {{ event_data['minion'] }}
    - arg:
      - {{ event_data['minion'] }}
      - {{ event_data['origin_ip'] }}
      - {{ event_data['yang_message'] }}

