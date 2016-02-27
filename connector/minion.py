#!/usr/bin/python3

import socket, time, threading

class minion_connector:
	
	def connect(server_ip):
		from connector.master import master_connector
		while True:
			try:
				fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
				fd.connect((server_ip, master_connector.tcp_port))
				print("[info]", "connected to master.")
				while True:
					data = b'ack'
					if fd.send(data) != len(data):
						break
					readData = fd.recv(1024)
					time.sleep(1)
				fd.close()
			except socket.error as e:
				print("[info]", "released from master.")
				pass
			except Exception as e:
				print("[warn]", e)
			finally:
				time.sleep(4)
	
	def start(server_ip):
		thread = threading.Thread(target = minion_connector.connect, args = [server_ip])
		thread.setDaemon(True)
		thread.start()
		return thread
