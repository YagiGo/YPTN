import sys, socket
import time
# A Pain in the ass of Python 3
# Encoding Problem:
# to use socket sendto/sendall/recvfrom
# Transfer using byte-like object not str
# therefore, you need to write your code like print(b"This is a test of the shitty encoding problem %s" %somethingyouwanttoadd.encode())
udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 2017
bufsize = 65535
# server side
if(sys.argv[1] == '-server'):
	interface = sys.argv[2]
	ADDR = (interface, port)
	udpsock.bind(ADDR)
	print("Listening to ", udpsock.getsockname())
	while(True):
		data, address = udpsock.recvfrom(bufsize)
		if(data == b'Hello!'):
			print("The Client ", address, "said hello to the server")
			timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
			udpsock.sendto(b"Hello to you! it is now %s" %timestamp.encode(), address)
		elif(data == b'WhoAreYou?'):
			print("The Client ", address, "Asked to identify the server")
			udpsock.sendto(ADDR.encode(),  address)
elif(sys.argv[1] == '-client'):
	interface = sys.argv[2] if(len(sys.argv) > 3) else ''
	ADDR = (interface, port)
	print(ADDR)
	udpsock.sendto(sys.argv[3].encode(), ADDR)
	print("Address of the client", udpsock.getsockname())
	data, address = udpsock.recvfrom(bufsize)
	print("The server", ADDR, "says", data)
	# it is not like there is something wrong with this server but also the authentity is worth being noted
elif(sys.argv[1] == '-'):
	print(" -server IPAddress  : Turn on the server \n" +
	" -client IPAddress Hello! : Ask server to send timestamp \n" +
	" -client IPAddress WhoAreYou? : Ask server to identify itself ")

