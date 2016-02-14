from intra.system import system_manager
from intra.cgroup import cgroup_manager
from intra.smart import smart_controller
from intra.billing import billing_manager

# lexicographic order

class case_handler:
	
	# curl -X POST -F uuid=n1 http://0.0.0.0:1725/v1/billing/increment
	def billing_increment(form):
		return billing_manager.fetch_increment_and_clean(form['uuid'])
	
	'''
	# curl -X POST -F uuid=n1 http://0.0.0.0:1725/v1/blacklist/add
	def blacklist_add(form):
		exists = form['uuid'] in smart_controller.blacklist
		if not exists:
			smart_controller.blacklist.add(form['uuid'])
		return {"changed": not exists}
	
	# curl -X POST -F uuid=n1 http://0.0.0.0:1725/v1/blacklist/remove
	def blacklist_remove(form):
		exists = form['uuid'] in smart_controller.blacklist
		if exists:
			smart_controller.blacklist.remove(form['uuid'])
		return {"changed": exists}
	
	# curl -X POST http://0.0.0.0:1725/v1/blacklist/show
	def blacklist_show(form):
		blacklist = []
		for item in smart_controller.blacklist:
			blacklist.append(item)
		return blacklist
	'''
	
	# curl -X POST http://0.0.0.0:1725/v1/cgroup/containers
	def cgroup_containers(form):
		return cgroup_manager.get_cgroup_containers()
	
	# curl -X POST http://0.0.0.0:1725/v1/system/loads
	def system_loads(form):
		return system_manager.get_system_loads()
	
	# curl -X POST http://0.0.0.0:1725/v1/system/memsw/available
	def system_memsw_available(form):
		return system_manager.get_available_memsw()
	
	# curl -X POST -F size=20 http://0.0.0.0:1725/v1/system/swap/resize
	def system_swap_resize(form):
		return system_manager.resize_swap(int(form['size']))
