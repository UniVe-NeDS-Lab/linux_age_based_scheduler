// This package was created by the antler init command.  Feel free to remove
// any comments in this file and add your own doc.

package tests

// Tests lists the tests to run.
Test: [
	for q in _qdiscs {
		_clt & {_qdisc: q}
	}
]

// MultiReport adds an HTML index file.
MultiReport: [{
	Index: {
		Title: "Tests for the sample package"
	}
}]
