GCC=/usr/bin/gcc

all: updater threshold_update_lib threshold_update_lib_py

threshold_update_lib_py: threshold_update.c
		  ${GCC} -shared threshold_update.c -l mnl -l netfilter_conntrack `python3-config --cflags` `python3-config --ldflags` -fPIC -o threshold_update.so

threshold_update_lib: threshold_update.c
		  ${GCC} -shared threshold_update.c -l mnl -l netfilter_conntrack `python3-config --cflags` `python3-config --ldflags` -DWITHOUT_PYTHON -fPIC -o threshold_update_lib.so

updater: threshold_update_lib updater.c
		  ${GCC} updater.c threshold_update_lib.so -o updater -l mnl -l netfilter_conntrack  
      
conntrack_events: conntrack_events.c
		  ${GCC} conntrack_events.c -o conntrack_events -l mnl -l netfilter_conntrack

clean:
	rm *.o *.so conntrack_events updater
