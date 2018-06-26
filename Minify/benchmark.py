# coding=utf-8
import socket
import struct
import sys
import time
import select
import os
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
        self.ICMP_ECHO_REQUEST = 8
        self.DEFAULT_TIMEOUT = 4
        self.count = 4 # ping times
        self.res ={"hop_counter": 0, "overall_latency": 0, "retry_times":0}
    # First Implement a traceroute
    def traceroute(self):
        dest_addr = socket.gethostbyname(self.destination)
        port = 33434
        max_hops = 30

        icmp = socket.getprotobyname('icmp')
        udp = socket.getprotobyname('udp')
        ttl = 1

        # Final benchmarking result

        retry_counter = 0 # how many times retried
        duration = 0.0 # overall latency


        while True:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # ICMP packet
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp) # UDP packet
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl) # TTL setting

            # Build the GNU timeval struct (seconds, microseconds)
            timeout = struct.pack('ll', 2, 0)

            # Set recv timeout
            recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

            recv_socket.bind(("", port))
            sys.stdout.write(" %d "  %ttl)
            start = time.time()
            send_socket.sendto("", (dest_addr, port))
            curr_addr = None
            curr_name = None
            finished = False
            tries = 3

            while not finished and tries > 0:
                try:
                    _, curr_addr = recv_socket.recvfrom(512)
                    finished = True
                    # sys.stdout.write(str((time.time() - start) * 1000))
                    duration += (time.time() - start) * 1000 # Get duration here
                    curr_addr = curr_addr[0]
                    try:
                        curr_name = socket.gethostbyaddr(curr_addr)[0]

                    except socket.error:
                        curr_name = curr_addr

                except socket.error as (errno, errmsg):
                    tries -= 1
                    sys.stdout.write(" *")
                    retry_counter += 1
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

        self.res["hop_counter"] = ttl
        # self.res["overall_latency"] = duration
        self.res["retry_times"] = retry_counter

    # Create a ping method
    # Get checksum
    """
    把校验和字段置为0
    将icmp包（包括header和data）以16bit（2个字节）为一组，并将所有组相加（二进制求和）
    若高16bit不为0，则将高16bit与低16bit反复相加，直到高16bit的值为0，从而获得一个只有16bit长度的值
    将此16bit值进行按位求反操作，将所得值替换到校验和字段
    """
    def do_checksum(self, source_string):
        # Used to verify the packet
        sum = 0
        max_count = (len(source_string) / 2) * 2
        count = 0
        # pair the string, 2Byte as a pir
        while count < max_count:
            val = ord(source_string[count + 1])*256 + ord(source_string[count])
            sum += val
            sum &= 0xffffffff
            count += 2
        if max_count<len(source_string):
            # if the length is odd number, add </span> to the last char
            sum += ord(source_string[len(source_string) - 1])
            sum &= 0xffffffff

        sum = (sum >> 16) + (sum & 0xffff) # Add lower 16bit to higher 16bit
        sum += sum>>16

        answer = ~sum
        answer &= 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def recv_ping(self, sock, ID, timeout):
        # Receive ping from socket
        time_remaining = timeout
        while True:
            start_time = time.time()
            readable = select.select([sock],[],[],time_remaining)
            time_spent = (time.time() - start_time)
            print(time_spent)
            if readable[0] == []:
                # Timeout
                return None

            time_received = time.time()
            recv_packet, addr = sock.recvfrom(1024)
            icmp_header = recv_packet[20:28]
            # get ICMP header
            type, code, checksum, packet_ID, sequence = struct.unpack(
                "bbHHh", icmp_header
            )
            if packet_ID == ID:
                # Get latency here
                bytes_In_double = struct.calcsize('d')
                time_sent = struct.unpack("d", recv_packet[28:28 + bytes_In_double])[0]
                return time_received - time_sent
            time_remaining -= time_spent
            if time_remaining <= 0:
                return None

    def send_ping(self,sock, ID):
        target_addr = socket.gethostbyname(self.destination)
        checksum = 0
        # Create a dummy header with a 0 checksum
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, checksum, ID, 1)
        bytes_In_double = struct.calcsize("d")
        # data = sent time, then filled with Q(not really matter!)
        data = struct.pack("d", time.time()) + (192 - bytes_In_double) * "Q"

        # Get the checksum on the data and the dummy header
        checksum = self.do_checksum(header+data)
        header = struct.pack(
            "bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(checksum), ID, 1)
        packet = header + data
        sock.sendto(packet, (target_addr, 1))

    def ping_once(self):
        icmp = socket.getprotobyname("icmp")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as (errno, errmsg):
            if errno == 1:
                # Must run as root!
                errmsg += "ICMP Message must be run as root user!"
                raise socket.error(errmsg)
        except Exception as e:
            print("Exception: " + str(e))

        ID = os.getpid() & 0xFFFF
        self.send_ping(sock, ID)
        delay = self.recv_ping(sock, ID, self.DEFAULT_TIMEOUT)
        return delay

    def ping(self):
        # start the ping process
        overall_time = 0.0
        for i in range(self.count):
            print("Ping to %s..." %self.destination)
            try:
                delay = self.ping_once()
            except socket.gaierror as  e:
                print("Ping failed.(Socket Error: %s)" %e[1])

            if delay == None:
                print("Ping failed. Timeout")
            else:
                delay = delay * 1000 # convert into ms
                overall_time += delay
                print("Get ping in %0.4f ms" %delay)
        mean_latency = overall_time / self.count
        self.res["overall_latency"] = round(mean_latency,3)

    def start_benchmarking(self):
        self.traceroute()
        self.ping()
        return self.res # benchmark result


if __name__ == "__main__":
    # Test Sites: Alexa Top 50 Sites
    test_sites = [
        'www.google.com',
        'www.youtube.com',
        'www.facebook.com',
        'www.baidu.com',
        'www.wikipedia.org',
        'www.yahoo.com',
        'www.reddit.com',
        'www.qq.com',
        'www.taobao.com',
        'www.amazon.com',
        'www.tmall.com',
        'www.twitter.com',
        'www.sohu.com',
        'www.live.com',
        'www.vk.com',
        'www.instagram.com',
        'www.sina.com.cn',
        'www.360.cn',
        'www.jd.com',
        'www.linkedin.com',
        'www.weibo.com',
        'www.yahoo.co.jp',
        'www.yandex.ru',
        'www.netflix.com',
        'www.t.co',
        'www.hao123.com',
        'www.imgur.com',
        'www.wordpress.com',
        'www.msn.com',
        'www.aliexpress.com',
        'www.bing.com',
        'www.tumblr.com',
        'www.microsoft.com',
        'www.stackoverflow.com',
        'www.twitch.tv',
        'www.amazon.co.jp',
        'www.soso.com',
        'www.apple.com',
        'www.naver.com',
        'www.imdb.com',
        'www.tianya.cn',
        'www.office.com',
        'www.github.com',
        'www.pinterest.com',
        'www.paypal.com',
        'www.adobe.com',
        'www.wikia.com',
        'www.cnzz.com',
        'www.rakuten.co.jp',
        'www.soundcloud.com',
        'www.bilibili.com'
    ]
    test_site = ['www.google.com']
    for site in test_site:
        sys.stdout.write("Currently Benchmarking "+site+"\n")
        test_measure = NetworkMeasure(source="localhost", destination=site)
        # res = test_measure.measure_hops()
        # print(res)
        res = test_measure.start_benchmarking()
        print(res)
        print("\n\n\n")