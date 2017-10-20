#!/usr/bin/env python
# UDP client and server on Local Host
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MAX = 65535 # MAXIMUM ALLOWED PACKET LENGTH
port = 1060 # Using port 1060
if (sys.argv[1:] == ['server']):
	s.bind(('127.0.0.1', port))
	print("Listening at ", s.getsockname())
	while(True):
		data, address = s.recvfrom(MAX)
		print("The client is at", address, "saying", repr(data))
		s.sendto(b"Your data is %d bytes at" %len(data), address)
elif (sys.argv[1:] == ['client']):
	# print("Address before sending: ", s.getsockname())
	s.sendto("This is my Message:".encode(), ('127.0.0.1', port)) # 如果用的是Python 3.x，sendall 的参数是bytes，所以正确的写法是b"xxx" 或者"xxx".encode().
	print("Address after sending", s.getsockname())
	data, address = s.recvfrom(MAX)
	print("The server ", address, "says", repr(data))

else:
	print(sys.stderr)