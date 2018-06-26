import socket
import struct
import sys

# We want unbuffered stdout so that live feedback can be provided for each TTL

class FlushFile:
    def __int__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()


class NetworkMeasure:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
    # First Implement a traceroute
    def measure_hops(self):
        dest_addr = socket.gethostbyname(self.destination)
        port = 33434
        max_hops = 30

        icmp = socket.getprotobyname('icmp')
        udp = socket.getprotobyname('udp')
        ttl = 1

        while True:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # ICMP packet
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp) # UDP packet
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl) # TTL setting

            # Build the GNU timeval struct (seconds, microseconds)
            timeout = struct.pack('ll', 5, 0)

            # Set recv timeout
            recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

            recv_socket.bind(("", port))
            sys.stdout.write(" %d"  %ttl)
            send_socket.sendto("", (dest_addr, port))
            curr_addr = None
            curr_name = None
            finished = False
            tries = 3

            while not finished and tries > 0:
                try:
                    _, curr_addr = recv_socket.recvfrom(512)
                    finished = True
                    curr_addr = curr_addr[0]
                    try:
                        curr_name = socket.gethostbyaddr(curr_addr)[0]

                    except socket.error:
                        curr_name = curr_addr

                except socket.error as (errno, errmsg):
                    tries -= 1
                    sys.stdout.write(" *")
            send_socket.close()
            recv_socket.close()

            if not finished:
                pass

            if curr_addr is not None:
                curr_host = "%s(%s)" %(curr_name, curr_addr)
            else:
                curr_host = ""
            sys.stdout.write(" %s\n" %(curr_host))

            ttl += 1

            if curr_addr == dest_addr or ttl > max_hops:
                break

test_measure = NetworkMeasure(source="localhost", destination="www.zhaoxinwublog.com")
test_measure.measure_hops()