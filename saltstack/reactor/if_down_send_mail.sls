shutdown_interface:
{%- set if_name = data.yang_message.interfaces.interface.keys()[0] %}

send_email:
  local.smtp.send_msg:
    - tgt: {{ data.host }}
    - arg:
        - rjoehl@hsr.ch
        - Interface down notification email body.
    - kwarg:
        subject: Interface {{ if_name }} is down
