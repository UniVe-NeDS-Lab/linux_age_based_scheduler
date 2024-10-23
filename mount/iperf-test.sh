#!/bin/bash
# set -e
# trap "exit" INT TERM
# trap "kill 0" EXIT


flags="-c server -p 5001 -f b"


iperf-loop () {
    while true
    do
        iperf $flags -n $1
        sleep 0.100
    done
}


for (( j=1; j<=30; j++ ))
do
    iperf-loop 100M &
    sleep 0.1
done

for (( i=1; i<=20; i++ ))
do    
    iperf-loop 10K &
    sleep 0.005
done

sleep 240

kill $(jobs -p)
wait $(jobs -p)