{% set event_data = data['data'] %}

port_flap_workflow:
  runner.tshoot.port_flap:
    - host: {{ event_data['host'] }}
    - yang_message: {{ event_data['data']['yang_message'] }}
    - error: {{ event_data['data']['error'] }}
    - tag: {{ event_data['data']['message_details']['tag'] }}
    - current_case: {{ event_data['case'] }}

