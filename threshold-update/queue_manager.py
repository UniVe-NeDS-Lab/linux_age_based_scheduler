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



flush_rules = "flush ruleset\n"

def make_multiqueue_prioritize(thresholds, priorities):

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
        ranges += pad + f'{thresholds[t]}-{thresholds[t+1]} : 1:{priorities[t]:04}, \n'
    ranges += pad + f'* : 1:{priorities[-1]:04}, \n'
        
    return ruleset_init.format(ranges=ranges)

def make_multiqueue_mark(thresholds, priorities):

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

def init_nftables(thresholds=[0,1000], prio=[1,2]):
    ruleset = flush_rules + make_multiqueue_mark(thresholds, prio) 
    nft = nftables.Nftables()
    nft.set_json_output(True)
    rc, output, error = nft.cmd(ruleset)
    #print(json.loads(output))
    
def main_loop():
    tu.set_up()
    conn_size = []
    last_change = datetime.now()
    while True:
        bt = tu.get_bytes()
        conn_size.append(bt)
        if datetime.now() - last_change > timedelta(seconds=1):
            m = int(np.median(conn_size))
            init_nftables([0,m], [1,2])
            print(f'updating threshold to {m}')
            last_change = datetime.now()
    tu.tear_down()


    
init_nftables()
main_loop()
