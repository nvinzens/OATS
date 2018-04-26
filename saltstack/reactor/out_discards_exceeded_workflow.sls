{% set event_data = data['data'] %}

out_discards_workflow:
  runner.tshoot.out_discards_exceeded:
    - data: {{ event_data['data'] }}
    - host: {{ event_data['host'] }}
    - timestamp: {{ event_data['timestamp'] }}
    - current_case: {{ event_data['case'] }}

