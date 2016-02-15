#!/usr/bin/python3

import socket, time

if __name__ == "__main__":
	fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	fd.connect(("0.0.0.0", 2003))
	
	for i in range(1, 11):
		data = ("The Number is %d" % i).encode()
		if fd.send(data) != len(data):
			break
		readData = fd.recv(1024)
		print(readData)
		time.sleep(1)
	
	fd.close()
