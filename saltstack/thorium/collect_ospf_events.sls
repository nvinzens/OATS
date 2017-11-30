count_ospf_events:
  local.cmd:
    - tgt: '*'
    - func: event.count
    - arg:
      - count_event: napam/syslog/*/OSPF_NEIGHBOR_DOWN/dead_timer_expired/*
