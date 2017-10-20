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
ADDR = ('localhost', port)
# server side
if(sys.argv[1:] == ['-server']):
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
	udpsock.sendto(sys.argv[2].encode(), ADDR)
	print("Address of the client", udpsock.getsockname())
	data, address = udpsock.recvfrom(bufsize)
	print("The server", ADDR, "says", data)
	# it is not like there is something wrong with this server but also the authentity is worth being noted
elif(sys.argv[1] == '-'):
	print(" -server : Turn on the server \n" +
	" -client Hello! : Ask server to send timestamp \n" +
	" -client WhoAreYou? : Ask server to identify itself ")
else:
	print(sys.stderr)


