#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo Maccari 
This code is free software, released with GPLv2 or later licenses

"""

import threshold_update as tu
from datetime import datetime, timedelta
import numpy as np
import nftables
import json
import collections
import subprocess



flush_rules = "flush ruleset\n"

class TimeOrderedQueues:

    def __init__(self, maxitems=3, update_interval=1):
        self.maxitems = maxitems
        # a queue of lists, one for every update period
        self.deq = collections.deque([[]], maxitems)
        self.lastupdate = datetime.now()
        #self.updateinterval = timedelta(minutes=update_interval)
        self.updateinterval = timedelta(seconds=update_interval)
        self.lastvalue = None


    def addSample(self, b):
        # append a new sample to the last list
        self.deq[-1].append(b)
        now = datetime.now()
        if self.lastvalue == None or now-self.lastupdate > self.updateinterval:
            print(self.deq)
            if self.lastvalue != None:
                # a new list
                self.deq.append([])
            self.lastupdate = datetime.now()
            # right now the threshold is set to the median of the 
            # lenght of the connections seen so far
            self.lastvalue = self.getMedian()
            return self.lastvalue
        return 0

    def getMedian(self):
        return np.median([x for minute in self.deq for x in minute])

def make_multiqueue_prioritize(thresholds, priorities):
    """ pfifo_fast uses the same classification than prio
        the first number (8001) is ignored
        the second is mapped as: 6->0, 4->1, 0->1, 2->2
        with the priority lowering from queue 0 to 2 """

    # create the rules to give priority to flows based on 
    # sent traffic 
    ruleset_init= """
    table ip prioritizeflows {{
            map multiqueue {{
                typeof ct bytes : meta priority
        		flags interval
		        elements = {{ {ranges} }}
		}}
   	chain mqueue {{
		type filter hook output priority 0; policy accept;
		meta priority set ct bytes map @multiqueue
        }}
    }}
    """
    ranges = '\n'
    pad = ' '*30
    for t in range(len(thresholds)-1):
        ranges += pad + f'{thresholds[t]}-{thresholds[t+1]} : 8001:{priorities[t]}:, \n'
    ranges += pad + f'* : 8001:{priorities[-1]}, \n'
        
    return ruleset_init.format(ranges=ranges)

def make_multiqueue_mark(thresholds, priorities):
    # same stuff as before, but instead of giving priority,
    # just mark the packets. Useful for debugging.
    ruleset_init= """
    table ip markflows {{
            map multiqueue {{
                typeof ct bytes : meta mark
        		flags interval
		        elements = {{ {ranges} }}
		}}
   	chain mqueue {{
		type filter hook output priority 0; policy accept;
        ct mark set ct bytes map @multiqueue
        }}
    }}
    """
    ranges = '\n'
    pad = ' '*30
    for t in range(len(thresholds)-1):
        ranges += pad + f'{thresholds[t]}-{thresholds[t+1]} : {t+1}, \n'
    ranges += pad + f'* : {priorities[-1]}, \n'
        
    return ruleset_init.format(ranges=ranges)

def init_nftables(thresholds=[0,1000], prio=[6,4,2]):
    #ruleset = flush_rules + make_multiqueue_mark(thresholds, prio) 
    ruleset = flush_rules + make_multiqueue_prioritize(thresholds, prio) 
    # use the nftables python bindings
    nft = nftables.Nftables()
    nft.set_json_output(True)
    # apply the ruleset
    rc, output, error = nft.cmd(ruleset)
    #print(json.loads(output))
    

def main_loop():
    # this sets-up the custom module for the collection of 
    # the connections size samples. 
    tu.set_up()
    while True:
        bt = tu.get_bytes()
        newm = int(data.addSample(bt))
        if newm: 
            init_nftables([0,newm], [1,2])
            print(f'updating threshold to {newm}')
    tu.tear_down()

def set_tc_pfifo_fast(iface="wlp0s20f3"):
    # this needs to be changed to the right interface name. 
    # it sets the default queueing discipline to PFIFO_FAST
    # that is the one we use as a base to priotize the traffic
    # the default is codel
    subprocess.call(["/sbin/tc", "qdisc", "replace", "root", "dev", 
                     iface, "pfifo_fast"])

data = TimeOrderedQueues(3, 5)
set_tc_pfifo_fast()
init_nftables()
main_loop()
