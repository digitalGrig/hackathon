#!/usr/bin/env python

import daemon, os, time
from datetime import datetime

devices = {
	'90:21:55:AE:E4:0B': 'Cristian Grigoriu',
	'CC:78:5F:2D:76:8D': 'George Dragusin'
	}
lastseen = {}
thrsh = 200

def proximity():
	while True:
		for baddr in devices:
			cmd = "hcitool cc {0} 2>/dev/null;hcitool lq {0} 2>/dev/null".format(baddr)
			f = os.popen(cmd)
			lines = f.readlines()
			for line in lines:
				if (line.startswith('Link')):
					link = int(line.rpartition(':')[2].strip())
					lastseen[baddr] = time.ctime()
					print "Avem link cu {0}::{1} la {2}".format(b, link, lastseen[baddr])


def run():
	with daemon.DaemonContext():
		proximity()

if __name__ == "__main__":
	run()