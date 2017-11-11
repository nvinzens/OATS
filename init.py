import re
from collections import OrderedDict

import napalm_logs.utils

_RGX_PARTS = [
    ('date', r'(\w+ \d+)'),
    ('time', r'(\d+:\d+:\d+.\d+)'),
    ('tag', r'([\w\d-]+)'),
    ('message', r'(.*)')
]
_RGX_PARTS = OrderedDict(_RGX_PARTS)

_RGX = '\{0[date]} {0[time]}: %{0[tag]}: {0[message]}'.format(_RGX_PARTS)


def extract(msg):
    return napalm_logs.utils.extract(_RGX, msg, _RGX_PARTS)