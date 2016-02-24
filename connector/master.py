#!/usr/bin/python3

import socket, select, errno, threading

class master_connector:
	
	tcp_port = 1727
	conn = {}
	epoll_fd = select.epoll()

	def close_connection(fd):
		master_connector.epoll_fd.unregister(fd)
		master_connector.conn[fd][0].close()
		addr = master_connector.conn[fd][1]
		master_connector.conn.pop(fd)
		print("close conn '%s', remaining %d conn." % (addr, len(master_connector.conn)))

	def do_message_response(input_buffer):
		assert(input_buffer == b'ack')
		return b'ack'
	
	def start():
		thread = threading.Thread(target = master_connector.run_forever, args = [])
		thread.setDaemon(True)
		thread.start()
		return thread
	
	def run_forever():
		listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listen_fd.bind(('', 1726))
		listen_fd.listen(10)
		
		master_connector.epoll_fd.register(listen_fd.fileno(), select.EPOLLIN)
		
		datalist = {}
		
		while True:
			epoll_list = master_connector.epoll_fd.poll()
			for fd, events in epoll_list:
				if fd == listen_fd.fileno():
					fileno, addr = listen_fd.accept()
					fileno.setblocking(0)
					master_connector.epoll_fd.register(fileno.fileno(), select.EPOLLIN | select.EPOLLET)
					master_connector.conn[fileno.fileno()] = (fileno, addr[0])
				elif select.EPOLLIN & events:
					datas = b''
					while True:
						try:
							data = master_connector.conn[fd][0].recv(10)
							if not data and not datas:
								master_connector.close_connection(fd)
								break
							else:
								datas += data
						except socket.error as msg:
							if msg.errno == errno.EAGAIN:
								try:
									datalist[fd] = master_connector.do_message_response(datas)
									master_connector.epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
								except:
									master_connector.close_connection(fd)
							else:
								master_connector.close_connection(fd)
							break
				elif select.EPOLLOUT & events:
					sendLen = 0
					while True:
						sendLen += master_connector.conn[fd][0].send(datalist[fd][sendLen:])
						if sendLen == len(datalist[fd]):
							break
					master_connector.epoll_fd.modify(fd, select.EPOLLIN | select.EPOLLET)
				elif select.EPOLLHUP & events:
					master_connector.close_connection(fd)
				else:
					continue
