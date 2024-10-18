## Run 

From the `virtlab` folder:

```
sudo run/qemu-cloud.sh client
sudo run/qemu-cloud.sh server
```


## Generate images

Base images 
`https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2` # has cloud kernel instead of generic
`https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2` # generic kernel supports 9p fs

To (re)generate separate images:
```
qemu-img create -f qcow2 -b debian-12-generic-amd64.qcow2 -F qcow2 virtlab/img/client-cloud.qcow2
qemu-img create -f qcow2 -b debian-12-generic-amd64.qcow2 -F qcow2 virtlab/img/server-cloud.qcow2
```


## Config

A config iso will be generated based on the contents of the `config` folder