package tests

import "list"

// _platform sets the node platform used for all tests (must match the local
// machine).
_platform: "linux-amd64"

// _stream selects what is streamed from nodes during tests.
_stream: {ResultStream: Include: Log: true}

// _sysinfo selects what system information is retrieved.
_sysinfo: {
	// SysInfo gathers system information.
	SysInfo: {
		OS: {
			Command: {Command: "uname -a"}
		}
		Command: [
			{Command: "lscpu"},
			{Command: "lshw -sanitize"},
		]
		File: [
			"/proc/cmdline",
			"/sys/devices/system/clocksource/clocksource0/available_clocksource",
			"/sys/devices/system/clocksource/clocksource0/current_clocksource",
		]
		Sysctl: [
			"^net\\.core\\.",
			"^net\\.ipv4\\.tcp_",
			"^net\\.ipv4\\.udp_",
		]
	}
}

// _offloads contains the ethtool arguments for offloads config.
_offloads: "rx off tx off sg off tso off gso off gro off rxvlan off txvlan off"


_sshNode: {
	ID:       string & !=""
	_index:   int
	Platform: _platform
	Launcher: SSH: {
		Root: false
		Destination: "lab-agesched0\(_index)"
		// Destination: "sv-lab-\(ID)"
	}
}


_nodes: {
	setup: {
		Serial: [
			_stream,
			_sysinfo,
			for n in [client, server] {
				Child: {
					Node: n.node
					Serial: [
						_stream,
						_qdiscdel & {_iface: n.iface},
						_nftdel,
						for c in n.setup {System: Command: c},
					]
				}
			},
		]
	}

	client: {
		post: [...string]
		// node:  _sshNode & {ID: "client"}
		// iface: "enp0s31f6"
		node:  _sshNode & {ID: "client", _index: 1}
		iface: "enp1s0f0"
		setup: list.Concat([
			[
				"sysctl -w net.ipv6.conf.all.disable_ipv6=1",
				"ethtool -K \(iface) \(_offloads)",
			],
			post,
			[
				"ping -c 3 -i 0.1 server",
			],
		])
	}

	server: {
		post: [...string]
		// node:  _sshNode & {ID: "server"}
		// iface: "enp0s31f6"
		node:  _sshNode & {ID: "server", _index: 2}		
		iface: "enp1s0f0"
		setup: list.Concat([
			[
				"sysctl -w net.ipv6.conf.all.disable_ipv6=1",
				"ethtool -K \(iface) \(_offloads)",
			],
			post,
		])
	}
}
