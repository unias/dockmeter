#!/usr/bin/python3

import time, sys, signal, json

if __name__ == '__main__':
	
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	
	if len(sys.argv) > 1:
		from intra.cgroup import cgroup_manager
		cgroup_manager.auto_detect_prefix()
		cgroup_manager.set_default_memory_limit(4)

		from intra.system import system_manager
		system_manager.set_db_prefix('/home/docklet/meter')
		system_manager.resize_swap(32)
		
		from connector.minion import minion_connector
		minion_connector.start(sys.argv[1])

		from policy.builtin import etime_policy
		from intra.smart import smart_controller
		
		smart_controller.set_policy(etime_policy)
		smart_controller.smart_control_forever()
		
		# from daemon.http import cg_http_server
		# cg_http_server.start()
	else:
		from connector.master import master_connector
		master_connector.start()
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
