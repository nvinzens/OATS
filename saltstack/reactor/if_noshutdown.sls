{% set event_data = data['data'] %}

wait_for_successful_ping:
  salt.wait_for_event:
    - name: salt/job/*/ret/{{ event_data['device'] }}
    - event_id: net.ping
    - timeout: 5
    - onfail:
      - local.slack: send_notification_to_slack_channel

no_shutdown_interface:
  local.net.load_template:
    - tgt: {{ event_data['device'] }}
    - kwarg:
        template_name: /etc/salt/template/noshut_interface.jinja
        interface_name: {{ event_data['interface'] }}
    - onlyif:
      - salt: wait_for_successful_ping

send_notification_to_slack_channel:
  local.slack.post_message:
    - tgt: 'master'
    - arg:
      - "#testing"
      - "Interface {{ event_data['interface'] }} is down BLABLA"
      - Interface Shutdown Reactor
      - xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317
    - kwargs:
      - test: False
