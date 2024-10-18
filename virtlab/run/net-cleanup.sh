ip link set tap0 nomaster
ip link set tap1 nomaster
ip tuntap del tap0 mode tap
ip tuntap del tap1 mode tap
ip link set down dev br0
ip link del br0
