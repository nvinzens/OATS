import pymongo
from pymongo import MongoClient
import sys
import datetime
import json

#Constants
MASTER = 'master'
DB_CLIENT = MongoClient()
DB = DB_CLIENT.oatsdb
#TODO: enum for status

def ifdown(host, origin_ip, yang_message, error, tag):
    '''
    Function that executes a workflow to fix the error that started an ifdown event
    '''

    conf = 'No changes'
    success = False
    yang_message = YangMessage(yang_message)
    interface = yang_message.getInterface()
    comment = 'Interface down status on host ' + host + ' detected. '
    interface_neighbor = _get_interface_neighbor(host, interface)
    case_id = create_case(error, host, status='solution_deployed')

    # check if error is still present, might have been solved already
    if _ping(host, interface_neighbor):
        close_case(case_id)
        return {
            'error': error,
            'tag': tag,
            'comment': 'Error not present anymore. Workflow not executed',
            'changes': conf,
            'success': True
        }

    neighbors = _get_neighbors(interface_neighbor)
    device_up = _check_device_connectivity(neighbors, interface_neighbor)

    if device_up:
        # cycle affected interface
        _if_shutdown(host, interface)
        conf = _if_noshutdown(host, interface)
        # check if cycle was successful
        success = _ping(host, interface_neighbor)
        if success:
            success = True
            comment += ('Config for Interface '
                       + interface + ' automatically changed from down to up')
            #TODO: remove?
            _post_slack(comment)
            close_case('TODO global case id')
        else:
            update_case('TODO global case id','solution',status='technician_needed')
            comment = ('Could not fix down status of ' + interface + ' on host'
                       + host + ' .')
            _post_slack(comment)
    if not device_up:
        # TODO: powercycle, check power consumation
        success = False
        update_case('TODO global case id','solution',status='technician_needed')
        _post_slack('Interface ' + interface + ' on host '
                     + host + ' down. Neighbor ' + interface_neighbor +
                    ' is down.')
        comment = 'Could not restore connectivity - Slack Message sent'

    return {
        'error': error,
        'tag': tag,
        'comment': comment,
        'changes': conf,
        'success': success
    }


def create_case(error, host, solution=None, description=None, status='New'):
    #TODO update indent
    #default values for everything
  event = error
  device = host
  solution = solution

  case_id = event + device

  new_case = {
    'case_nr': case_id,
    'Event': event,
    'Description': 'Event description',
    'Status': 'New',
    'created': datetime.datetime.utcnow(),
    'last_updated': datetime.datetime.utcnow(),
    'technician': 'not_called',
    'Sender_Device': device,
    'Solution': [
        {solution},
    ]
  }

  try:
    DB.cases.insert_one(new_case)
    print '\nCase inserted successfully\n'

  except Exception, e:
      print str(e)

  return case_id

def update_case(case_id, solution, status=None):
    #if state exists update state else only solution
    return case_id

def close_case(case_id):
    #status of case = resolved
    return case_id

def take_case(case_id, technician):
    #technician takes case
    return case_id

def _post_slack(message):
    channel = '#testing'
    user = 'OATS'
    api_key = 'xoxp-262145928167-261944878470-261988872518-7e7aae3dc3e8361f9ef04dca36ea6317'
    update_case('TODO global case id', {'TODO DICT': 'FOR SOLUTION'}, status='technician_called')
    #get case extract data and post it to slack
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def _ping(from_host, to_host):
    ping_result = None
    if from_host == MASTER:
        ping_result = __salt__['salt.execute'](to_host, 'net.ping', {'127.0.0.1'})
        return ping_result[to_host]['result']
    else:
        ping_result = __salt__['salt.execute'](from_host, 'net.ping', {to_host})
    return ping_result[from_host]['out']['success']['results']


def _if_noshutdown(minion, interface):
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case('TODO global case id', {'TODO DICT': 'FOR SOLUTION'})
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)


def _if_shutdown(minion, interface):
    template_name = 'shutdown_interface'
    template_source = 'interface ' + interface + '\n  shutdown\nend'
    config = {'template_name': template_name,'template_source': template_source}
    update_case('TODO global case id', {'TODO DICT': 'FOR SOLUTION'})
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)


def _check_device_connectivity(neighbors, host):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :return: if the host is connected to one of his neighbors or the master: True/False
    '''
    # TODO: uncomment for use in real env, in lab env routers are pingable even if the respective interfaces are down
    connected = False
    #for neighbor in neighbors:
    #    connected = __ping(neighbor, host)
    #    if connected:
    #        return connected
    # TODO: evaluate what it means when master is connected, but none of the neighbors
    connected = _ping(MASTER, host)
    return connected


def _get_interface_neighbor(host, interface):
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['interface'] == interface:
            update_case('TODO global case id',{'TODO DICT':'FOR SOLUTION'})
            return link['neighbor']


def _get_neighbors(host):
    neighbors = []
    links = DB.network.find_one({'host_name': host})['connections']
    for link in links:
        if link['neighbor'] and not link['neighbor'] == MASTER:
            neighbors.append(link['neighbor'])
    update_case('TODO global case id', {'TODO DICT': 'FOR SOLUTION'})
    return neighbors


class YangMessage(object):
    def __init__(self, yang_message):
        self.yang_message = yang_message

    def getInterface(self):
        return self.yang_message['interfaces']['interface'].popitem()[0]
