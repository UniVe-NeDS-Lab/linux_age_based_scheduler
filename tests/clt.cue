package tests

import "list"

_clt: {
	// _rtt is the path RTT, in milliseconds
	_rtt: 10

	// traffic generation parameters
	_duration: "6h"
	_nActors: 80	
	_thinkingTime: "1.0s"
	_seed: 322

	Timeout: "0s"

	_qdisc: {
		name: string
		setup: [...string]
		interval: _rtt
		iface: _rig.client.iface
	}

	// ID is the Test ID.
	ID: {
		name: "closedloop"
		rtt: "\(_rtt)ms"
		qdisc: _qdisc.name
		seed: "\(_seed)"
	}
	Path: "{{.name}}_{{.qdisc}}_"

	Serial: [
		_rig.setup,
		_server,
		_do,
	]

	// After is the report pipeline for the Test.
	After: [
		{Analyze: {}},
		{EmitStreamStats: Name: "streams.json"},
		{SaveFiles: {}},
	]

	_rig: _nodes & {
		serverAddr: "server:7777"
		client: post: [
			for l in _qdisc.setup {l},
            "tc qdisc show dev \(client.iface)",
            "nft list ruleset",
		]
		server: post: []
	}

	// _server runs StreamServer in the right namespace
	_server: {
		Child: {
			Node: _rig.server.node
			Serial: [
				{StreamServer: ListenAddr: _rig.serverAddr},
				{PacketServer: ListenAddr: _rig.serverAddr},
			]
		}
	}

	// _do runs the test using two StreamClients
	_do: {
		Child: {
			Node: _rig.client.node
			Serial: [
				{Sleep: "1s"},
				{Parallel: [
					for j in list.Range(0, _nActors, 1)
					{ClosedLoopActor:{
						ThinkingTime: _thinkingTime
						Duration: _duration
						Seed: _seed*_nActors*2 + j
						Random: {
							Seed: _seed*_nActors*2 + j+1
							Run: [
								for len in _connsizespareto 
								{StreamClient: {
									Addr: _rig.serverAddr
									Upload: {
										Flow: "actor\(j)"
										CCA: "cubic"
										Length: len
										IOSampleInterval: "\(_rtt*4)ms"
									}}
								},
							]
							Weights: _connprobpareto
						}
					}},
				]},
				{Sleep: "1s"},
				_qdiscstats & {_iface: _rig.client.iface},
			]
		}
	}
}
