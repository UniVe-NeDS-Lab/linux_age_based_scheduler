#!/bin/bash
set -e
trap "exit" INT TERM
trap "kill 0" EXIT

timestamp=$(date +%s)
echo "Starting test at $timestamp"


echo "Resetting the network"
nft delete table inet prioritize || true
tc qdisc del root dev ens4 || true
sleep 1


echo "Starting ss"
ss --oneline --events --info state all dst server > /mnt/shared/logs/iperf-log-$timestamp-def.txt &
sleep 20


echo "Starting iperf3 traffic"
/mnt/shared/iperf-test.sh
sleep 20
killall ss


echo "Test finished"
sleep 2


echo "Enabling age based prioritization"
nft -f /mnt/shared/rulesets/prioritize.nft
tc qdisc replace root dev ens4 pfifo_fast
sleep 1


echo "Starting ss"
ss --oneline --events --info state all dst server > /mnt/shared/logs/iperf-log-$timestamp-age.txt &
sleep 20


echo "Starting iperf3 test"
/mnt/shared/iperf-test.sh
sleep 20
killall ss


echo "Test finished"


echo "Resetting the network"
nft delete table inet prioritize
tc qdisc del root dev ens4

