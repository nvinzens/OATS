{% set event_data = data['data'] %}

ping_and_run_state:
  runner.tshoot.ifdown:
    - minion: {{ event_data['minion'] }}
    - origin_ip: {{ event_data['origin_ip'] }}
    - yang_message: {{ event_data['yang_message'] }}
    - error: {{ event_data['error'] }}
    - tag: {{ event_data['tag'] }}

