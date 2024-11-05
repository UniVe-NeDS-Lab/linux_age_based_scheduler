#!/bin/bash
set -e
trap "exit" INT TERM
trap "kill 0" EXIT

ssh="sshpass -p password ssh -oStrictHostKeyChecking=no debian@server"

timestamp=$(date +%s)
echo "Starting test at $timestamp"

echo "Resetting the network to codel"
nft delete table inet prioritize || true
# $ssh sudo nft delete table inet prioritize || true
tc qdisc del root dev ens4 || true
# $ssh sudo tc qdisc del root dev ens4 || true
sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.py > /mnt/shared/logs/iperf-log-$timestamp-codel.txt
echo "Test finished"
tc -s qdisc show dev ens4
sleep 2


echo "Enabling pfifo_fast"

tc qdisc add dev ens4 root handle 1: prio bands 3
tc qdisc add dev ens4 parent 1:1 handle 10: codel
tc qdisc add dev ens4 parent 1:2 handle 20: codel
tc qdisc add dev ens4 parent 1:3 handle 30: codel

sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.py > /mnt/shared/logs/iperf-log-$timestamp-pfifo.txt
echo "Test finished"
tc -s qdisc show dev ens4
sleep 2


echo "Enabling age based prioritization"
nft -f /mnt/shared/rulesets/prioritize.nft
sleep 1

echo "Starting iperf2 test"
/mnt/shared/iperf-test.py > /mnt/shared/logs/iperf-log-$timestamp-age.txt
echo "Test finished"
tc -s qdisc show dev ens4


echo "Resetting the network"
nft delete table inet prioritize
tc qdisc del root dev ens4

