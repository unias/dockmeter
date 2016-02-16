class candidates_selector:
	
	def select(candidates):
		return min(candidates, key=lambda addr: candidates[addr]['load'])