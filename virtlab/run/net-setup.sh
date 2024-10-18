ip link add name br0 type bridge
ip tuntap add tap0 mode tap
ip tuntap add tap1 mode tap
ip link set tap0 master br0
ip link set tap1 master br0
ip link set up dev tap0
ip link set up dev tap1
ip link set up dev br0
