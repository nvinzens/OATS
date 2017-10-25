increase_prefix_limit_on_thresh_exceeded:
  local.net.load_template:
    - tgt: "hostname:{{ data['host'] }}"
    - tgt_type: grain
    - kwarg:
        template_name: salt://increase_prefix_limit.jinja
        openconfig_structure: {{ data['open_config'] }}
