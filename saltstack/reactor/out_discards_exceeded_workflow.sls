{% set event_data = data['data'] %}

ifdown_workflow:
  runner.tshoot.out_discards_exceeded:
    - data: {{ event_data['data'] }}
    - host: {{ event_data['host'] }}
    - timestamp: {{ event_data['timestamp'] }}

