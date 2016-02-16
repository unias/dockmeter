#!/usr/bin/python3

# billing collector;
# load balancer;

import time, sys, signal, json

from intra.system import system_manager
from intra.smart import smart_controller
from intra.cgroup import cgroup_manager
from daemon.http import cg_http_server

if __name__ == '__main__':
	
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	
	if len(sys.argv) > 1:
		from server.common import master_minion_connector
		system_manager.set_db_prefix('/home/docklet/meter')
		system_manager.resize_swap(32)
		
		from policy.builtin import etime_policy
		smart_controller.set_policy(etime_policy)
		
		cg_http_server.start()
		master_minion_connector.start(sys.argv[1])
		smart_controller.smart_control_forever()
	else:
		from server.server import master_minion_server
		master_minion_server.start()
		while True:
			line = sys.stdin.readline().strip()
			if line == 'list':
				minions = []
				for item in master_minion_server.conn:
					minions.append(master_minion_server.conn[item][1])
				print(minions)
			elif line.startswith('alloc '):
				[alloc, cpu, mem] = line.split()
				mem = int(mem)
				cpu = int(cpu)
				candidates = {}
				for item in master_minion_server.conn:
					addr = master_minion_server.conn[item][1]
					
					import urllib.request, urllib.parse
					response = urllib.request.urlopen('http://0.0.0.0:%d/v1/system/memsw/available' % cg_http_server.port, urllib.parse.urlencode({}).encode())
					obj = json.loads(response.read().decode().strip())
					if obj['data']['Mbytes'] >= mem:
						candidates[addr] = obj['data']
					response.close()
				if len(candidates_selector) <= 0:
					print("no minions")
				else:
					from policy.allocation import candidates_selector
					one = candidates_selector.select(candidates)
					print("selected:", one)
