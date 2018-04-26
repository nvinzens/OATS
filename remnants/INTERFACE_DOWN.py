'''
message example:
Nov 11 10:28:25.254: %LINK-5-CHANGED: Interface
GigabitEthernet2, changed state to administratively down
'''


from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

import napalm_logs.utils
from napalm_logs.config import OPEN_CONFIG_NO_MODEL

__tag__ = 'LINK-5-CHANGED'
__error__ = 'INTERFACE_DOWN'
__yang_model__ = OPEN_CONFIG_NO_MODEL

log = logging.getLogger(__file__)

_RGX_PARTS = [
    ('interface', r'(\w+\d[.]?[\d]?)'),
    ('change_mode', r'(\w+)'),
    ('status', r'(\w+)')
]
_RGX_PARTS = OrderedDict(_RGX_PARTS)

_RGX = (
    'Interface {0[interface]}, '
    'changed state to {0[change_mode]} {0[status]}'
).format(_RGX_PARTS)  # ATTENTION to escape the parans


def emit(msg_dict):
    log.debug('Evaluating the message dict:')
    log.debug(msg_dict)
    ret = {}
    extracted = napalm_logs.utils.extract(_RGX, msg_dict['message'], _RGX_PARTS)
    if not extracted:
        return ret
    interface = '{0[interface]}'.format(extracted)
    change_mode = '{0[change_mode]}'.format(extracted)
    status = '{0[status]}'.format(extracted)
    ret.update(napalm_logs.utils.setval(interface, change_mode, status, dict_=ret))
    return ret