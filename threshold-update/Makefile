GCC=/usr/bin/gcc

all: updater threshold_update_lib

threshold_update_lib: threshold_update.c
		  ${GCC} -c threshold_update.c -l mnl -l netfilter_conntrack `python3-config --cflags`

updater: threshold_update_lib updater.c
		  ${GCC} updater.c threshold_update.o -o updater -l mnl -l netfilter_conntrack  
      
conntrack_events: conntrack_events.c
		  ${GCC} conntrack_events.c -o conntrack_events -l mnl -l netfilter_conntrack

clean:
	rm threshold_update.o conntrack_events updater
