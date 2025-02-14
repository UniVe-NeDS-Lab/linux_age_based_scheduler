#!/bin/bash
set -e

iface=${2:-enp0s31f6}

case "$1" in
    "reset")
        sudo tc qdisc del root dev $iface 2>/dev/null || true        
        ;;
    "codel")
        sudo tc qdisc del root dev $iface || true
        sudo tc qdisc add dev $iface root handle 1: codel
        ;;
    "fqcodel")
        sudo tc qdisc del root dev $iface || true
        sudo tc qdisc add dev $iface root handle 1: fq_codel
        ;;
    "age")
        sudo tc qdisc del root dev $iface || true
        sudo tc qdisc add dev $iface root handle 1: prio bands 3
        sudo tc qdisc add dev $iface parent 1:1 handle 10: codel
        sudo tc qdisc add dev $iface parent 1:2 handle 20: codel
        sudo tc qdisc add dev $iface parent 1:3 handle 30: codel
        ;;
    "pfifo")
        sudo tc qdisc del root dev $iface || true
        sudo tc qdisc add dev $iface root handle 1: pfifo
        ;;
    "pfifofast")
        sudo tc qdisc del root dev $iface || true
        sudo tc qdisc add dev $iface root handle 1: pfifo_fast
        ;;
    *)
        echo "Usage: $0 <reset|codel|fqcodel|age|pfifo|pfifofast> [iface]"
        exit 1
        ;;
esac