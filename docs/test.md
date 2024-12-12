To enable age based priority: 
```
sudo nft -f ./rulesets/prioritize-pfifo.nft
sudo tc qdisc replace root dev enp0s31f6 pfifo_fast
```

To reset default queueing:
```
sudo nft delete table inet prioritize
sudo tc qdisc del root dev enp0s31f6
```

To check:
```
sudo nft list ruleset
sudo tc -s qdisc show dev enp0s31f6
```

Age based priority with codel:

```
sudo nft -f ./rulesets/prioritize.nft
sudo tc qdisc del root dev enp0s31f6
sudo tc qdisc add dev enp0s31f6 root handle 1: prio bands 3
sudo tc qdisc add dev enp0s31f6 parent 1:1 handle 10: codel
sudo tc qdisc add dev enp0s31f6 parent 1:2 handle 20: codel
sudo tc qdisc add dev enp0s31f6 parent 1:3 handle 30: codel
```

default qdisc
```
qdisc fq_codel 0: dev enp0s31f6 root refcnt 2 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb ecn drop_batch 64
```