#!/bin/bash


for (( i=1; i<=10; i++ ))
do
    iperf3 -c server -p 5202 -Z -n 2K > /dev/null
done


iperf3 -c server -p 5201 -Z -n 10G -P 3 > /dev/null &


for (( i=1; i<=500; i++ ))
do
    iperf3 -c server -p 5202 -Z -n 2K > /dev/null
done


wait $(jobs -p)