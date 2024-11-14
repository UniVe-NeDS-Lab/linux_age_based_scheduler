
To collect stats: 
```
ss --oneline --events --info dst server > /mnt/shared/logs/iperf-log-$(date +%s).txt
```

To start traffic:
```
iperf-test.sh
```

To enable age based priority: 
```
sudo nft -f /mnt/shared/rulesets/prioritize.nft
sudo tc qdisc replace root dev ens4 pfifo_fast
```

To reset default queueing:
```
sudo nft delete table inet prioritize
sudo tc qdisc del root dev ens4
```

To check:
```
sudo nft list ruleset
sudo tc -s qdisc show dev ens4
```

```
sudo tc qdisc add dev ens4 root handle 1: prio bands 3
sudo tc qdisc add dev ens4 parent 1:1 handle 10: codel
sudo tc qdisc add dev ens4 parent 1:2 handle 20: codel
sudo tc qdisc add dev ens4 parent 1:3 handle 30: codel
```


```
sudo nft -f /mnt/shared/rulesets/prioritize.nft
sudo tc qdisc del root dev ens4
sudo tc qdisc add dev ens4 root handle 1: prio bands 3
sudo tc qdisc add dev ens4 parent 1:1 handle 10: codel
sudo tc qdisc add dev ens4 parent 1:2 handle 20: codel
sudo tc qdisc add dev ens4 parent 1:3 handle 30: codel
```