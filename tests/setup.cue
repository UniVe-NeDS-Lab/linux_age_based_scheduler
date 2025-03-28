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
	Platform: _platform
	Launcher: SSH: {
		Root: false
		Destination: "sv-lab-\(ID)"
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
		node:  _sshNode & {ID: "client"}
		iface: "enp0s31f6"
		setup: list.Concat([
			[
				"sysctl -w net.ipv6.conf.all.disable_ipv6=1",
				"ethtool -K \(iface) \(_offloads)",
				"ping -c 3 -i 0.1 server",
			],
			post,
		])
	}

	server: {
		post: [...string]
		node:  _sshNode & {ID: "server"}		
		iface: "enp0s31f6"
		setup: list.Concat([
			[
				"sysctl -w net.ipv6.conf.all.disable_ipv6=1",
				"ethtool -K \(iface) \(_offloads)",
			],
			post,
		])
	}
}
