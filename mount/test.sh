#!/bin/bash
set -e
trap "exit" INT TERM
trap "kill 0" EXIT

timestamp=$(date +%s)
echo "Starting test at $timestamp"


echo "Resetting the network to codel"
nft delete table inet prioritize || true
tc qdisc del root dev ens4 || true
sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.sh | grep  0.0000- > /mnt/shared/logs/iperf-log-$timestamp-codel.txt
echo "Test finished"
sleep 2


echo "Enabling pfifo_fast"
tc qdisc replace root dev ens4 pfifo_fast
sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.sh | grep  0.0000- > /mnt/shared/logs/iperf-log-$timestamp-pfifo.txt
echo "Test finished"
sleep 2


echo "Enabling age based prioritization"
nft -f /mnt/shared/rulesets/prioritize.nft
sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.sh | grep  0.0000- > /mnt/shared/logs/iperf-log-$timestamp-age.txt
echo "Test finished"


echo "Resetting the network"
nft delete table inet prioritize
tc qdisc del root dev ens4

