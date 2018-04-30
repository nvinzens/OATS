{% set event_data = data['data'] %}

ospf_nbr_down_workflow:
  runner.tshoot.ospf_nbr_down:
    - host: {{ event_data['host'] }}
    - yang_message: {{ event_data['data']['yang_message'] }}
    - error: {{ event_data['data']['error'] }}
    - tag: {{ event_data['data']['message_details']['tag'] }}
    - process_number: {{ event_data['data']['message_details']['processnumber'] }}
    - current_case: {{ event_data['case'] }}

