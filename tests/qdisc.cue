package tests

_qdiscs: [
    {
        name: "pfifo"
        iface: string
        setup: [
            "tc qdisc add dev \(iface) root handle 1: pfifo",
        ]
    },
    {
        name: "codel"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: codel interval \(interval)ms target \(interval*0.05)ms",
        ]
    },
    {
        name: "fqcodel"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: fq_codel interval \(interval)ms target \(interval*0.05)ms",
        ]
    },
    {
        name: "cake"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: cake rtt \(interval)ms",
        ]
    },
    {
        name: "pie"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
        ]
    },
    {
        name: "fqpie"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: fq_pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
        ]
    },
    {
        name: "age-pfifofast"
        iface: string
        setup: [
            "tc qdisc add dev \(iface) root handle 1: pfifo_fast",
            for l in _nftprioritize.pfifofast.setup { l },
        ]
    },
    {
        name: "age-prio-codel"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: prio bands 3",
            "tc qdisc add dev \(iface) parent 1:1 handle 10: codel interval \(interval)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:2 handle 20: codel interval \(interval)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:3 handle 30: codel interval \(interval)ms target \(interval*0.05)ms",
            for l in _nftprioritize.prio.setup { l },
        ]
    },
    {
        name: "age-prio-fqcodel"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: prio bands 3",
            "tc qdisc add dev \(iface) parent 1:1 handle 10: fq_codel interval \(interval)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:2 handle 20: fq_codel interval \(interval)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:3 handle 30: fq_codel interval \(interval)ms target \(interval*0.05)ms",
            for l in _nftprioritize.prio.setup { l },
        ]
    },
    {
        name: "age-cake"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: cake rtt \(interval)ms",
            for l in _nftprioritize.cake.setup { l },
        ]
    },
    {
        name: "age-prio-pie"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: prio bands 3",
            "tc qdisc add dev \(iface) parent 1:1 handle 10: pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:2 handle 20: pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:3 handle 30: pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            for l in _nftprioritize.prio.setup { l },
        ]
    },
    {
        name: "age-prio-fqpie"
        iface: string
        interval: int
        setup: [
            "tc qdisc add dev \(iface) root handle 1: prio bands 3",
            "tc qdisc add dev \(iface) parent 1:1 handle 10: fq_pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:2 handle 20: fq_pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            "tc qdisc add dev \(iface) parent 1:3 handle 30: fq_pie tupdate \(interval*0.3)ms target \(interval*0.05)ms",
            for l in _nftprioritize.prio.setup { l },
        ]
    },
]

_netem_delay: {
    iface: string
    delay: int
    setup: [
        "tc qdisc add dev \(iface) root netem limit 100000 delay \(delay)ms \(delay*0.1)ms distribution normal"
    ]
}