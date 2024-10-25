
Both machines have 2 network interfaces:
- **ens3** connection to host and internet, with nat and ssh port forward (2221 and 2222)
- **ens4** bridge between client and server


```
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug ens3
iface ens3 inet dhcp

# Tap interface
allow-hotplug ens4
iface ens4 inet static
        address 192.168.42.1/24
        address 192.168.42.2/24
```

To limit bandwith, can do this on the host:
```
sudo tc qdisc add dev tap0 root tbf rate 100mbit latency 50ms burst 1540
sudo tc qdisc add dev tap1 root tbf rate 100mbit latency 50ms burst 1540
```