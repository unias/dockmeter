import subprocess, time, os, threading

from intra.system import system_manager
from intra.cgroup import cgroup_manager
from intra.billing import billing_manager

class smart_controller:
	
	def set_policy(policy):
		smart_controller.policy = policy
	
	def start(interval = 4):
		thread = threading.Thread(target = smart_controller.smart_control_forever, args = [interval])
		thread.setDaemon(True)
		thread.start()
		return thread
	
	def smart_control_forever(interval):
		last_live = []
		while True:
			time.sleep(interval)
			
			live = cgroup_manager.get_cgroup_containers()
			for item in live:
				try:
					last_live.remove(item)
				except:
					pass
				try:
					cgroup_manager.protect_container_oom(item)
					sample = cgroup_manager.get_container_sample(item)
					billing_manager.add_usage_sample(item, sample)
				except Exception as e:
					print("[exception]", e)
			for item in last_live:
				billing_manager.clean_dead_node(item)
			last_live = live
			is_ready = True
			
			memory_available = system_manager.get_available_memsw()
			if memory_available['Mbytes'] <= 0:
				print("[warning]", 'not recommended for overloaded containers.')
			
			
			total_score = 0.0
			score_mapping = {}
			for item in live:
				score = max(1e-2, smart_controller.policy.get_score_by_uuid(item))
				score_mapping[item] = score
				total_score += score
			
			mem_alloc = system_manager.get_total_physical_memory_for_containers()['Mbytes']
			
			for item in live:
				ceof = score_mapping[item] / total_score
				item_alloc = mem_alloc * ceof
				cgroup_manager.set_container_cpu_priority_limit(item, ceof)
				cgroup_manager.set_container_physical_memory_limit(item, item_alloc)
				print(item if len(item)<10 else item[:10] + "..", "cpu share:", "%.1f%%," % (ceof * 100), "mem alloc:", item_alloc, "mbytes")
			

"""
def lookup_forever():
	assert(BOOK_LEN > 2)
	
	while True:
		time.sleep(INTERVAL)
		
		live_containers = []
		for cont in get_local_live_containers():
			try:
				usage = get_cgroup_usages(prefix + "lxc/" + cont)
				if cont not in ResourceHTTPHandler.lxc_book:
					on_new_lxc_comes(cont)
					ResourceHTTPHandler.lxc_book[cont] = [usage]
				elif usage['oom_killer']:
					on_old_lxc_goes(cont)
					on_new_lxc_comes(cont)
					ResourceHTTPHandler.lxc_book[cont] = [usage]
				else:
					on_lxc_acct_usage(cont, usage['cpu']-ResourceHTTPHandler.lxc_book[cont][-1]['cpu'], usage['phy_mem']+ResourceHTTPHandler.lxc_book[cont][-1]['phy_mem']>>1)
					ResourceHTTPHandler.lxc_book[cont].append(usage)
					if len(ResourceHTTPHandler.lxc_book[cont]) >= BOOK_LEN:
						ResourceHTTPHandler.lxc_book[cont] = judge_lxc_resource_usage(cont, ResourceHTTPHandler.lxc_book[cont])
					
				live_containers.append(cont)
			except Exception as ex:
				print("[warning]", ex)
				pass
		
		lxc_book_new = {}
		for cont in ResourceHTTPHandler.lxc_book:
			if cont in live_containers:
				lxc_book_new[cont] = ResourceHTTPHandler.lxc_book[cont]
			else:
				on_old_lxc_goes(cont)
		ResourceHTTPHandler.lxc_book = lxc_book_new
		if len(ResourceHTTPHandler.system_monitor) >= BOOK_LEN:
			ResourceHTTPHandler.system_monitor = ResourceHTTPHandler.system_monitor[1:]
		ResourceHTTPHandler.system_monitor.append(get_system_usages())

		for cont in ResourceHTTPHandler.lxc_book:
			history = ResourceHTTPHandler.lxc_book[cont]
			if len(history) != BOOK_LEN:
				continue
			w_cpu = w_mem = w_p = 0.0
			for i in range(1, BOOK_LEN):
				w_cpu += i * (history[i]['cpu'] - history[i-1]['cpu']) / 1024 / 1024 / 1024 / INTERVAL;
				w_mem += i * history[i]['phy_mem'] / 1024 / 1024
				w_p += i
			cpu_ceof = w_cpu / w_p
			mem_ceof = w_mem / w_p
			print(time.time(), cont, "%.2f" % cpu_ceof, "%.2f" % mem_ceof)
"""

# echo "8:0 1000" > /sys/fs/cgroup/blkio/lxc/docklet-1-0/blkio.throttle.write_bps_device
# https://www.kernel.org/doc/Documentation/devices.txt
# while true; do clear; cat /sys/fs/cgroup/blkio/lxc/docklet-1-0/blkio.throttle.io_service_bytes; sleep 0.5; done
# hugetlb, net_cls, net_prio, /sbin/tc