import subprocess, time, os, threading, math

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
			try:
				mem_usage_mapping = {}
				live = cgroup_manager.get_cgroup_containers()
				for item in live:
					try:
						last_live.remove(item)
					except:
						pass
					try:
						cgroup_manager.protect_container_oom(item)
						sample = cgroup_manager.get_container_sample(item)
						mem_usage_mapping[item] = math.ceil(sample['mem_page_sample'] * 1e-6)
						billing_manager.add_usage_sample(item, sample)
					except:
						pass
				for item in last_live:
					billing_manager.clean_dead_node(item)
				last_live = live
				is_ready = True
				
				memory_available = system_manager.get_available_memsw()
				if memory_available['Mbytes'] <= 0:
					size_in_gb = int(math.ceil(-memory_available['Mbytes'] / 1024 / 16) * 16)
					print("[warning]", 'overloaded containers, auto-extending %d G memsw.' % size_in_gb)
					system_manager.extend_swap(size_in_gb)
				
				print("-------------------------------")
				
				total_score = 0.0
				score_mapping = {}
				for item in live:
					score = max(1e-8, smart_controller.policy.get_score_by_uuid(item))
					score_mapping[item] = score
					print(item, "(score/cpu)", score)
					total_score += score
				
				# CPU Scoring
				for item in live:
					ceof = score_mapping[item] / total_score
					cgroup_manager.set_container_cpu_priority_limit(item, ceof)
				
				# Iterative Memory Scoring
				free_mem = system_manager.get_total_physical_memory_for_containers()['Mbytes']
				local_nodes = live
				mem_alloc = {}
				for item in live:
					mem_alloc[item] = 0
				
				while free_mem > 0 and len(local_nodes) > 0:
					excess_mem = 0
					next_local_nodes = []
					for item in local_nodes:
						mem_alloc[item] += int(math.floor(free_mem * score_mapping[item] / total_score))
						if mem_alloc[item] >= mem_usage_mapping[item]:
							excess_mem += mem_alloc[item] - mem_usage_mapping[item]
							mem_alloc[item] = mem_usage_mapping[item]
						else:
							next_local_nodes.append(item)
					free_mem = excess_mem
					local_nodes = next_local_nodes
				
				for item in live:
					mem_alloc[item] += int(math.floor(free_mem * score_mapping[item] / total_score))
					cgroup_manager.set_container_physical_memory_limit(item, mem_alloc[item])
					print(item, "(malloc:usage)", mem_alloc[item], mem_usage_mapping[item])
				
			except:
				pass

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
