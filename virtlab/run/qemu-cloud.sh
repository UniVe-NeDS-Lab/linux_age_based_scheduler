#1 /bin/sh

if [ "$#" -ne 1 ] || ([ "$1" != "client" ] && [ "$1" != "server" ]); then
    echo "Usage: $0 <client|server>"
    exit 1
fi

# create the seed iso file
genisoimage \
    -output virtlab/img/seed-$1.iso \
    -volid cidata -rational-rock -joliet \
    virtlab/config/$1;


if [ "$1" = "client" ]; then
    SSHPORT=2221
    FGPORT=5001
    MAC=52:55:00:d1:55:01
    TAP=tap0
else
    SSHPORT=2222
    FGPORT=5002
    MAC=52:55:00:d1:55:02
    TAP=tap1
fi

IMG=virtlab/img/debian-12-generic-amd64.qcow2
# IMG=virtlab/img/$1-cloud.qcow2

# run the VM
exec qemu-system-x86_64 \
    -m 4G --enable-kvm -cpu host -machine accel=kvm -smp 4 -snapshot -nographic \
    -drive file=$IMG,index=0,format=qcow2,media=disk \
    -drive file=virtlab/img/seed-$1.iso,index=1,media=cdrom \
    -netdev user,id=external,hostfwd=tcp::$SSHPORT-:22,hostfwd=tcp::$FGPORT-:5999 -device virtio-net-pci,netdev=external \
    -netdev tap,id=internal,ifname=$TAP,script=no,downscript=no -device e1000,netdev=internal,mac=$MAC \
    -virtfs local,path=$(pwd)/mount,mount_tag=shared,security_model=none,id=hostshare
