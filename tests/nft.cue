package tests


_nftprioritize: {
    // threshold: 55Mi // from 5 class test
    // threshold: 90475270 // size*pdf cumsum kneed
    // threshold: 6332751 // phfit + optimize 2lps
    // threshold: 13746699 // cdf kneed

    threshold: 19500715 // 10 gbps
    // threshold: 6331208 // 1 gbps

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

