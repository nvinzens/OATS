from ncclient import manager
from ncclient.xml_ import new_ele, sub_ele
from lxml import etree

XPATH = "/memory-ios-xe-oper:memory-statistics/memory-statistic/free-memory"


def errback(notif):
	pass


def callback(notif):
	print (etree.tostring(notif.datastore_ele, pretty_print=True).decode('utf-8'))

manager = manager.connect(host='10.20.1.21',
                              port=830,
                              username='ins',
                              password='ins@lab',
                              allow_agent=False,
                              look_for_keys=False,
                              hostkey_verify=False,
                              unknown_host_cb=True)

s =  manager.establish_subscription(callback, errback, xpath=XPATH, period=1000)
print s
while True:
	pass
