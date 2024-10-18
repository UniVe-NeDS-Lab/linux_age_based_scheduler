
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
sudo nft -f /mnt/shared/nftables/priority.nft
sudo tc qdisc replace root dev ens4 pfifo_fast
```

To reset default queueing:
```
sudo nft delete table inet prioritizeflows
sudo tc qdisc del root dev ens4
```

To check:
```
sudo nft list ruleset
sudo tc qdisc
```