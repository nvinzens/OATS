from __future__ import with_statement
import zmq
import napalm_logs.utils
import salt.utils.event
import salt.client
import collections
from expiringdict import ExpiringDict #pip install expiringdict
import time
import threading
from threading import Thread
import Queue
from oatssalthelpers import oats
from salt_event import send_salt_event


CACHE_SIZE = 1000
MAX_AGE = 11
AGGREGATE_EVENTS = ['OSPF_NEIGHBOR_DOWN']


# cache for not sending the same event multiple times
# event correlation only looks if in the last MAX_AGE seconds the same event occured
# and if it did, skips it
# can be refined, but needs to get data from the database for that
cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE)
lock = threading.Lock()


class Aggregator(Thread):
    cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=MAX_AGE)
    counter = Queue.Queue()

    def __init__(self, event_msg, primary_opt_arg, secondary_opt_arg=None, collect_for=MAX_AGE):
        Thread.__init__(self)
        self.event = event_msg['error']
        self.cache[self.event] = {}
        self.cache[self.event]['counter'] = 1
        self.collect_for = collect_for
        self.event_msg = event_msg
        self.current_case = oats.create_case(self.event, self.event_msg['host'])
        self.primary_arg = primary_opt_arg
        self.secondary_arg = secondary_opt_arg

    def run(self):
        if self.event in AGGREGATE_EVENTS:
            thread = Thread(target=self.__wait_and_collect_(), args=(self.counter))
            thread.start()
            n = 0
            # TODO: currently needs if case for every new error, make generic
            if self.event == 'OSPF_NEIGHBOR_DOWN':
                self.secondary_arg = 'ifdown'
                n = len(oats.get_ospf_neighbors(self.event_msg['host']), case = self.current_case)
            thread.join()
            if n == self.counter.get():
                #send with primary_arg
                send_salt_event(self.event_msg['yang_message'], self.event_msg['host'], self.event_msg['ip'],
                                               self.event_msg['tag'], self.event_msg['message_details'],
                                                self.event_msg['error'], self.primary_arg, case=self.current_case)
            else:
                #send with secondary_arg
                send_salt_event(self.event_msg['yang_message'], self.event_msg['host'], self.event_msg['ip'],
                                self.event_msg['tag'], self.event_msg['message_details'],
                                self.event_msg['error'], self.secondary_arg, case=self.current_case)
        else:
            send_salt_event(self.event_msg['yang_message'], self.event_msg['host'], self.event_msg['ip'],
                            self.event_msg['tag'], self.event_msg['message_details'],
                            self.event_msg['error'], self.primary_arg, case=self.current_case)



    def __wait_and_collect_(self):
        time.sleep(MAX_AGE - 1)

    def increment(self):
        count = self.counter.get()
        count += 1
        self.counter.put(count)
_


