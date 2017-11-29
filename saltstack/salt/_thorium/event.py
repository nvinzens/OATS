from __future__ import absolute_import
import time
from interruptingcow import timeout #pip install interruptingcow
import salt.config
import salt.utils.event
import salt.utils.stringutils


def count(name, count_event, collect=10):
    now = time.time()
    counter = 1
    ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': True}
    mtr = 'message_start_tracker'
    if mtr not in __context__:
        __context__[mtr] = {}
    if count_event not in __reg__:
        __reg__[count_event] = {}
        __reg__[count_event]['counter'] = counter
        __reg__[count_event]['time'] = now
    else:
        counter = __reg__[count_event]['counter']
    for event in __events__:
        try:
            event_data = event['data']['data']
        except KeyError:
            event_data = event['data']
        if salt.utils.stringutils.expr_match(event['tag'], count_event):
            if now - __reg__['time'] > collect:
                if counter <= 1:
                    __tshoot_ifdown(event_data)
                    counter = 0
                else:
                    __tshoot_ospf_nbr_down(event_data)
                    counter = 0
            else:
                counter += 1
        else:
            if count_event not in __context__[mtr]:
                __context__[mtr][count_event] = now
            if now - __context__[mtr][count_event] > collect:
                if counter <= 1:
                    __tshoot_ifdown(event_data)
                    counter = 0
                else:
                    __tshoot_ospf_nbr_down(event_data)
                    counter = 0
                __context__[mtr].pop(count_event, None)
        __reg__[count_event]['counter'] = counter
    return ret


def __tshoot_ifdown(event_data):
    __salt__['salt.cmd'](fun='tshoot.ospf_nbr_down', host=event_data['minion'], origin_ip=event_data['origin_ip'],
                         yang_message=event_data['yang_message'], error=event_data['error'],
                         tag=event_data['tag'])


def __tshoot_ospf_nbr_down(event_data):
    __salt__['salt.cmd'](fun='tshoot.ifdown', host=event_data['minion'],
                         origin_ip=event_data['origin_ip'],
                         yang_message=event_data['yang_message'], error=event_data['error'],
                         tag=event_data['tag'])
