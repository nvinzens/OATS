{% set event_data = data['data'] %}

ospf_nbr_down_workflow:
  runner.tshoot.ospf_nbr_down:
    - host: {{ event_data['minion'] }}
    - origin_ip: {{ event_data['origin_ip'] }}
    - yang_message: {{ event_data['yang_message'] }}
    - error: {{ event_data['error'] }}
    - tag: {{ event_data['tag'] }}
    - process_number: {{ event_data['message_details']['processnumber'] }}
    - current_case: {{ event_data['case'] }}

