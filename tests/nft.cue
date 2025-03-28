package tests


_nftprioritize: {
    threshold: 55Mi
    table: "prioritize"
    _base: {
        mapping: string
        setup: [
            "nft add table inet \(table)",
            "nft add map inet \(table) multiqueue { typeof ct bytes : meta priority; flags interval; elements = { \(mapping) } }",
            "nft add chain inet \(table) y { type filter hook output priority 0; policy accept; }",
            "nft add rule inet \(table) y meta priority set ct bytes map @multiqueue",
        ]
    }
    cake: _base & {
        mapping: "0-\(threshold) : 1:2, * : 1:1"
    }
    prio: _base & {
        mapping: "0-\(threshold) : 1:1, * : 1:2"
    }
    pfifofast: _base & {
        mapping: "0-\(threshold) : 1:6, * : 1:0"
    }
}

