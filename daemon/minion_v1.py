from intra.system import system_manager
from intra.billing import billing_manager
from intra.cgroup import cgroup_manager

class case_handler:
	# [Order-by] lexicographic order
	
	# curl -L -X POST -F uuid=docklet-1-0 http://[ip:port]/v1/billing/increment
	def billing_increment(form, args):
		return billing_manager.fetch_increment_and_clean(form['uuid'])
	
	# curl -L -X POST http://[ip:port]/v1/cgroup/container/list
	def cgroup_container_list(form, args):
		return cgroup_manager.get_cgroup_containers()
	
	# curl -L -X POST -F uuid=n1 http://[ip:port]/v1/cgroup/container/limit
	def cgroup_container_limit(form, args):
		return cgroup_manager.get_container_limit(form['uuid'])
	
	# curl -L -X POST -F uuid=n1 http://[ip:port]/v1/cgroup/container/sample
	def cgroup_container_sample(form, args):
		return cgroup_manager.get_container_sample(form['uuid'])
	
	# curl -L -X POST http://[ip:port]/v1/system/loads
	def system_loads(form, args):
		return system_manager.get_system_loads()
	
	# curl -L -X POST http://[ip:port]/v1/system/memsw/available
	def system_memsw_available(form, args):
		return system_manager.get_available_memsw()
	
	# curl -L -X POST -F size=20 http://[ip:port]/v1/system/swap/resize
	def system_swap_resize(form, args):
		return system_manager.resize_swap(int(form['size']))
	
	# curl -L -X POST http://[ip:port]/v1/system/total/physical/memory
	def system_total_physical_memory(form, args):
		return system_manager.get_total_physical_memory_for_containers()

	'''
	# curl -X POST -F uuid=n1 http://[ip:port]/v1/blacklist/add
	def blacklist_add(form):
		exists = form['uuid'] in smart_controller.blacklist
		if not exists:
			smart_controller.blacklist.add(form['uuid'])
		return {"changed": not exists}
	
	# curl -X POST -F uuid=n1 http://[ip:port]/v1/blacklist/remove
	def blacklist_remove(form):
		exists = form['uuid'] in smart_controller.blacklist
		if exists:
			smart_controller.blacklist.remove(form['uuid'])
		return {"changed": exists}
	
	# curl -X POST http://[ip:port]/v1/blacklist/show
	def blacklist_show(form):
		blacklist = []
		for item in smart_controller.blacklist:
			blacklist.append(item)
		return blacklist
	'''
