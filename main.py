#!/usr/bin/python3

import time, sys, signal

from intra.system import system_manager
from intra.smart import smart_controller
from intra.cgroup import cgroup_manager
from daemon.http import cg_http_server

if __name__ == '__main__':
	
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	
	system_manager.set_db_prefix('/home/docklet/meter')
	system_manager.resize_swap(32)
	
	from policy.builtin import etime_policy
	smart_controller.set_policy(etime_policy)
	
	cg_http_server.start()
	smart_controller.smart_control_forever()
