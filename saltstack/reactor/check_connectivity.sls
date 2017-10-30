{% set data = data['data'] %}
activate_remote_interface:
  local.net.ping:
    - tgt: {{ data['device'] }}
    - arg:
      - 192.168.50.10
