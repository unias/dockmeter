#!/usr/bin/python3

import socket, select, errno

conn = {}
epoll_fd = select.epoll()

def close_connection(fd):
	epoll_fd.unregister(fd)
	conn[fd][0].close()
	addr = conn[fd][1]
	conn.pop(fd)
	print("close conn '%s', remaining %d conn." % (addr, len(conn)))

def do_message_response(input_buffer):
	return b'ack'

if __name__ == "__main__":
	listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_fd.bind(('', 2003))
	listen_fd.listen(10)
	
	epoll_fd.register(listen_fd.fileno(), select.EPOLLIN)
	
	datalist = {}
	
	while True:
		epoll_list = epoll_fd.poll()
		for fd, events in epoll_list:
			if fd == listen_fd.fileno():
				fileno, addr = listen_fd.accept()
				fileno.setblocking(0)
				epoll_fd.register(fileno.fileno(), select.EPOLLIN | select.EPOLLET)
				conn[fileno.fileno()] = (fileno, addr[0])
			elif select.EPOLLIN & events:
				datas = b''
				while True:
					try:
						data = conn[fd][0].recv(10)
						if not data and not datas:
							close_connection(fd)
							break
						else:
							datas += data
					except socket.error as msg:
						if msg.errno == errno.EAGAIN:
							datalist[fd] = do_message_response(datas)
							epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
							break
						else:
							close_connection(fd)
							break
			elif select.EPOLLOUT & events:
				sendLen = 0
				while True:
					sendLen += conn[fd][0].send(datalist[fd][sendLen:])
					if sendLen == len(datalist[fd]):
						break
				epoll_fd.modify(fd, select.EPOLLIN | select.EPOLLET)
			elif select.EPOLLHUP & events:
				close_connection(fd)
			else:
				continue
