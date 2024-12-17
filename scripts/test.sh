#!/bin/bash
set -e
trap "exit" INT TERM
trap "kill 0" EXIT

if [ -z "$1" ] 
then
    logdir=logs
else
    logdir=$1
fi
mkdir -p $logdir

iface=enp0s31f6
timestamp=$(date +%s)
echo "Starting test at $timestamp"

echo "Resetting interface to default fq_codel"
nft delete table inet prioritize 2>/dev/null || true
tc qdisc del root dev $iface 2>/dev/null || true
sleep 1

echo "Starting iperf2 test"
./scripts/iperf-test.py | gzip > $logdir/iperf-log-$timestamp-fqcodel.json.gz
echo "Test finished"
tc -s qdisc show dev $iface
sleep 2

echo "Enabling codel"
tc qdisc add dev $iface root handle 1: codel
sleep 1

echo "Starting iperf2 test"
./scripts/iperf-test.py | gzip > $logdir/iperf-log-$timestamp-codel.json.gz
echo "Test finished"
tc -s qdisc show dev $iface
sleep 2


echo "Enabling age based prioritization"
tc qdisc del root dev $iface
tc qdisc add dev $iface root handle 1: prio bands 3
tc qdisc add dev $iface parent 1:1 handle 10: codel
tc qdisc add dev $iface parent 1:2 handle 20: codel
tc qdisc add dev $iface parent 1:3 handle 30: codel
nft -f ./rulesets/prioritize.nft
sleep 1

echo "Starting iperf2 test"
./scripts/iperf-test.py | gzip > $logdir/iperf-log-$timestamp-age.json.gz
echo "Test finished"
tc -s qdisc show dev $iface


echo "Enabling pfifo"
tc qdisc del root dev $iface
tc qdisc add dev $iface root handle 1: pfifo
nft -f ./rulesets/prioritize-pfifo.nft
sleep 1

echo "Starting iperf2 test"
./scripts/iperf-test.py | gzip > $logdir/iperf-log-$timestamp-pfifo.json.gz
echo "Test finished"
tc -s qdisc show dev $iface


echo "Enabling pfifo_fast"
tc qdisc del root dev $iface
tc qdisc add dev $iface root handle 1: pfifo_fast
nft -f ./rulesets/prioritize-pfifo.nft
sleep 1

echo "Starting iperf2 test"
./scripts/iperf-test.py | gzip > $logdir/iperf-log-$timestamp-pfifofast.json.gz
echo "Test finished"
tc -s qdisc show dev $iface


echo "Resetting the network"
nft delete table inet prioritize
tc qdisc del root dev $iface

