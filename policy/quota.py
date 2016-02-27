from intra.system import system_manager
from intra.cgroup import cgroup_manager

class identify_policy:
	
	def get_score_by_uuid(uuid):
		return 1.0

class etime_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		pid = cgroup_manager.get_container_pid(uuid)
		etime = system_manager.get_proc_etime(pid)
		return 1.0 / etime

class mem_usage_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		sample = cgroup_manager.get_container_sample(uuid)
		return sample["mem_page_sample"]

class mem_quota_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		sample = cgroup_manager.get_container_limit(uuid)
		return sample["mem_page_quota"]

class cpu_usage_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		sample = cgroup_manager.get_container_sample(uuid)
		return sample["cpu_sample"]

class cpu_usage_rev_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		sample = cgroup_manager.get_container_sample(uuid)
		return 1.0 / sample["cpu_sample"]

class cpu_speed_policy(identify_policy):
	
	def get_score_by_uuid(uuid):
		sample = cgroup_manager.get_container_sample(uuid)
		pid = cgroup_manager.get_container_pid(uuid)
		etime = system_manager.get_proc_etime(pid)
		return sample["cpu_sample"] / etime

class fixed_policy(identify_policy):
	
	active_list = set()

	def get_score_by_uuid(uuid):
		return 4.0 if uuid in fixed_policy.active_list else 1.0
