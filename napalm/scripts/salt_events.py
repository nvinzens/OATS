#!/usr/bin/env python

import salt.client
import json

def send_ifdown_event(device, interface):
    caller = salt.client.Caller()
    print('configuring: ' + device)
    print('Checking connectivity')
    caller.sminion.functions['event.send'](
      'napalm/syslog/*/INTERFACE_DOWN/*',
      {'device': device,
        'interface': interface}
    )

if __name__ == '__main__':
     send_ifdown_event()
