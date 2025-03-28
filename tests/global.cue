package tests

// _dark2 is the Dark2 qualitative color scheme from colorbrewer2.org, with
// the first blue-green color replaced by the green color, as it's too close.
_dark2: [
	//"#1b9e77",
	"#66a61e",
	"#d95f02",
	"#7570b3",
	"#e7298a",
	"#e6ab02",
	"#a6761d",
	"#666666",
]

// tcpdump defines a Runner to run tcpdump to stdout, and save stdout to a file.
_tcpdump: {
	// iface defines the interface to capture on.
	_iface: string & !=""

	// snaplen is how many bytes to capture from each packet.
	_snaplen: int | *128

	System: {
		Command:    "tcpdump -i \(_iface) -s \(_snaplen) -w -"
		Background: true
		Stdout:     "\(_iface).pcap.zst"
	}
}

// _qdiscstats defines a Runner to run tc -s qdisc show dev <iface> to stdout,
_qdiscstats: {
	// iface defines the interface to display.
	_iface: string & !=""

	System: {
		Command:    "tc -s qdisc show dev \(_iface)"
		Stdout:     "qdisc_\(_iface).txt"
	}
}

// _qdiscstats defines a Runner to run tc -s qdisc show dev <iface> to stdout,
_qdiscdel: {
	// iface defines the interface to clean up.
	_iface: string & !=""

	System: {
		Command: "tc qdisc del root dev \(_iface)"
		IgnoreErrors: true
	}
}

_nftdel: {
	System: {
		Command: "nft delete table inet \(_nftprioritize.table)"
		IgnoreErrors: true
	}
}

// Run all commands as root using sudo, if antler was not run as root.
#System: Root: bool | *true