#!/bin/bash
set -e
trap "exit" INT TERM
trap "kill 0" EXIT

if [[ -z "$1" ]]
then
    echo "Usage: $0 <logdir>"
    exit 1
fi

sshhost=sv-lab-client
sshhostsrv=sv-lab-server
iface=enp0s31f6
timestamp=$(date +%s)
dir=$(ssh $sshhost mktemp -d /tmp/iperftest.XXXX)

seed=${SEED-$RANDOM}

echo "Starting test at $timestamp - using directory $dir - seed $seed"

echo "Push scripts to the client"
ssh -q $sshhost "mkdir -p $dir $dir/logs"
scp -r scripts/ $sshhost:$dir/scripts
scp -r rulesets/ $sshhost:$dir/rulesets

run-test () {
    sleep 2
    echo " - Starting iperf2 test - $1 $2"
    ssh $sshhost "$dir/scripts/setup-tc.sh $1 $iface"  # setup tc and nftables
    sleep 1
    ssh $sshhost "SEED=$seed $dir/scripts/iperf-test.py | gzip > $dir/logs/iperf-log-$timestamp-$1$2.json.gz"  # run iperf test
    ssh $sshhost "sudo tc -s qdisc show dev $iface"  # show qdisc stats
}

# ensure interface is clean
ssh $sshhost "$dir/scripts/setup-tc.sh reset $iface 2>/dev/null || true"
ssh $sshhost "sudo nft delete table inet prioritize 2>/dev/null || true"

# disable offloading
ssh $sshhost "sudo ethtool -K $iface rx off tx off sg off tso off gso off gro off rxvlan off txvlan off"
ssh $sshhostsrv "sudo ethtool -K $iface rx off tx off sg off tso off gso off gro off rxvlan off txvlan off"

# run tests

run-test fqcodel
run-test codel
run-test pfifo
run-test cake

ssh $sshhost "sudo nft -f $dir/rulesets/prioritize.nft"
run-test age  # age + prio codel

ssh $sshhost "sudo nft -f $dir/rulesets/prioritize-pfifo.nft"
run-test pfifofast  # age + pfifo_fast

ssh $sshhost "sudo nft -f $dir/rulesets/prioritize-cake.nft"
run-test cake age  # age + cake


# reset interface
ssh $sshhost "$dir/scripts/setup-tc.sh reset $iface"
ssh $sshhost "sudo nft delete table inet prioritize"


echo "Downloading logs"
scp $sshhost:$dir/logs/* ./logs/$1