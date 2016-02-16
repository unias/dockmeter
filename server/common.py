#!/usr/bin/python3

import socket, time, threading

class master_minion_connector:
	
	tcp_port = 1726
	
	def client_connect(server_ip):
		while True:
			try:
				fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
				fd.connect((server_ip, master_minion_connector.tcp_port))
				print("[info]", "connected to master.")
				while True:
					data = b'ack'
					if fd.send(data) != len(data):
						break
					readData = fd.recv(1024)
					time.sleep(1)
				fd.close()
			except:
				print("[warn]", "master not launched.")
				time.sleep(4)
	
	def start(server_ip):
		thread = threading.Thread(target = master_minion_connector.client_connect, args = [server_ip])
		thread.setDaemon(True)
		thread.start()
		return thread

