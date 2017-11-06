{% set event_data = data['data'] %}
check connectivity to server:
  local.net.ping:
    - tgt: {{ event_data['device'] }}
    - arg:
      - 192.168.50.10
      - timeout=10
      - count=5
