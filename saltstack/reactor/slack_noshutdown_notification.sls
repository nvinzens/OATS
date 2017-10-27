send_notification_to_slack_channel:
  local.slack.post_message:
    - tgt: 'master'
    - arg:
      - "#testing"
      - "Interface {{ if_name }} is up"
      - Interface Start Reactor
      - xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317
    - kwargs:
      - test: False
