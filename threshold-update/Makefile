GCC=/usr/bin/gcc

all: threshold_update conntrack_events

threshold_update: threshold_update.c
		  ${GCC} threshold_update.c -o threshold_update -l mnl -l netfilter_conntrack
      
conntrack_events: conntrack_events.c
		  ${GCC} conntrack_events.c -o conntrack_events -l mnl -l netfilter_conntrack
