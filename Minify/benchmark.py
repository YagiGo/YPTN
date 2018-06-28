# coding: utf-8
# We want unbuffered stdout so that live feedback can be provided for each TTL

#!/usr/bin/env python
#
# Copyright (c) 2018 Zhaoxin Wu
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import socket
import struct
import sys
import time
import select
import os
import random
from twisted.internet import defer, reactor


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
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # UDP packet
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
###############################################################################################################

# Create ICMP, TCP, UDP headers down below
#

###############################################################################################################

class iphdr(object):
    """
    This represents an IP packet header.
    @assemble packages the packet
    @disassemble disassembles the packet
    """
    def __init__(self, proto=socket.IPPROTO_ICMP, src="0.0.0.0", dst=None):
        self.version = 4
        self.hlen = 5
        self.tos = 0
        self.length = 20
        self.id = random.randint(2 ** 10, 2 ** 16)
        self.frag = 0
        self.ttl = 255
        self.proto = proto
        self.cksum = 0
        self.src = src
        self.saddr = socket.inet_aton(src)
        self.dst = dst or "0.0.0.0"
        self.daddr = socket.inet_aton(self.dst)
        self.data = ""

    def assemble(self):
        header = struct.pack('BBHHHBB',
                             (self.version & 0x0f) << 4 | (self.hlen & 0x0f),
                             self.tos, self.length + len(self.data),
                             socket.htons(self.id), self.frag,
                             self.ttl, self.proto)
        self._raw = header + "\x00\x00" + self.saddr + self.daddr + self.data
        return self._raw

    @classmethod
    def disassemble(self, data):
        self._raw = data
        ip = iphdr()
        pkt = struct.unpack('!BBHHHBBH', data[:12])
        ip.version = (pkt[0] >> 4 & 0x0f)
        ip.hlen = (pkt[0] & 0x0f)
        ip.tos, ip.length, ip.id, ip.frag, ip.ttl, ip.proto, ip.cksum = pkt[1:]
        ip.saddr = data[12:16]
        ip.daddr = data[16:20]
        ip.src = socket.inet_ntoa(ip.saddr)
        ip.dst = socket.inet_ntoa(ip.daddr)
        return ip

    def __repr__(self):
        return "IP (tos %s, ttl %s, id %s, frag %s, proto %s, length %s) " \
               "%s -> %s" % \
               (self.tos, self.ttl, self.id, self.frag, self.proto,
                self.length, self.src, self.dst)


class tcphdr(object):
    def __init__(self, data="", dport=4242, sport=4242):
        self.seq = 0
        self.hlen = 44
        self.flags = 2
        self.wsize = 200
        self.cksum = 123
        self.options = 0
        self.mss = 1460
        self.dport = dport
        self.sport = sport

    def assemble(self):
        header = struct.pack("!HHL", self.sport, self.dport, self.seq)
        header += '\x00\x00\x00\x00'
        header += struct.pack("!HHH", (self.hlen & 0xff) << 10 | (self.flags &
            0xff), self.wsize, self.cksum)
        header += "\x00\x00"
        options = '\x02\x04\x05\xb4\x01\x03\x03\x01\x01\x01\x08\x0a'
        options += '\x4d\xcf\x52\x33\x00\x00\x00\x00\x04\x02\x00\x00'
        # XXX There is something wrong here fixme
        # options = struct.pack("!LBBBBBB", self.mss, 1, 3, 3, 1, 1, 1)
        # options += struct.pack("!BBL", 8, 10, 1209452188)
        # options += '\00'*4
        # options += struct.pack("!BB", 4, 2)
        # options += '\00'
        self._raw = header + options
        return self._raw

    @classmethod
    def checksum(self, data):
        pass

    def disassemble(self, data):
        self._raw = data
        tcp = tcphdr()
        pkt = struct.unpack("!HHLH", data[:20])
        tcp.sport, tcp.dport, tcp.seq = pkt[:3]
        tcp.hlen = (pkt[4] >> 10) & 0xff
        tcp.flags = pkt[4] & 0xff
        tcp.wsize, tcp.cksum = struct.unpack("!HH", data[20:28])
        return tcp


class udphdr(object):
    def __init__(self, data="", dport=4242, sport=4242):
        self.dport = dport
        self.sport = sport
        self.cksum = 0
        self.length = 0
        self.data = data

    def assemble(self):
        self.length = len(self.data) + 8
        part1 = struct.pack("!HHH", self.sport, self.dport, self.length)
        cksum = self.checksum(self.data)
        cksum = struct.pack("!H", cksum)

        self._raw = part1 + cksum + self.data
        return self._raw

    @classmethod
    def checksum(self, data):
        # XXX implement proper checksum
        cksum = 0
        return cksum

    def disassemble(self, data):
        self._raw = data
        udp = udphdr()
        pkt = struct.unpack("!HHHH", data)
        udp.src_port, udp.dst_port, udp.length, udp.cksum = pkt
        return udp


class icmphdr(object):
    def __init__(self, data=""):
        self.type = 8
        self.code = 0
        self.cksum = 0
        self.id = random.randint(2 ** 10, 2 ** 16)
        self.sequence = 0
        self.data = data

    def assemble(self):
        part1 = struct.pack("BB", self.type, self.code)
        part2 = struct.pack("!HH", self.id, self.sequence)
        cksum = self.checksum(part1 + "\x00\x00" + part2 + self.data)
        cksum = struct.pack("!H", cksum)
        self._raw = part1 + cksum + part2 + self.data
        return self._raw

    @classmethod
    def checksum(self, data):
        if len(data) & 1:
            data += "\x00"
        cksum = reduce(operator.add,
                       struct.unpack('!%dH' % (len(data) >> 1), data))
        cksum = (cksum >> 16) + (cksum & 0xffff)
        cksum += (cksum >> 16)
        cksum = (cksum & 0xffff) ^ 0xffff
        return cksum

    @classmethod
    def disassemble(self, data):
        self._raw = data
        icmp = icmphdr()
        pkt = struct.unpack("!BBHHH", data)
        icmp.type, icmp.code, icmp.cksum, icmp.id, icmp.sequence = pkt
        return icmp

    def __repr__(self):
        return "ICMP (type %s, code %s, id %s, sequence %s)" % \
                (self.type, self.code, self.id, self.sequence)
##################################################################################################################

# Create a TCP traceroute here.

##################################################################################################################
class Hop(object):
    def __init__(self, target, ttl, proto, dport=None, sport=None):
        self.proto = proto
        self.dport = dport
        self.sport = sport

        self.found = False
        self.tries = 0
        self.last_try = 0
        self.remote_ip = None
        self.remote_icmp = None
        self.remote_host = None
        self.location = ""

        self.ttl = ttl
        self.ip = iphdr(dst=target)
        self.ip.ttl = ttl
        self.ip.id += ttl
        if self.proto == "icmp":
            self.icmp = icmphdr('\x00' * 20)
            self.icmp.id = self.ip.id
            self.ip.data = self.icmp.assemble()
        elif self.proto == "udp":
            self.udp = udphdr('\x00' * 20, self.dport, self.sport)
            self.ip.data = self.udp.assemble()
            self.ip.proto = socket.IPPROTO_UDP
        else:
            self.tcp = tcphdr('\x42' * 20, self.dport, self.sport)
            self.ip.data = self.tcp.assemble()
            self.ip.proto = socket.IPPROTO_TCP

        self._pkt = self.ip.assemble()

    @property
    def pkt(self):
        self.tries += 1
        self.last_try = time.time()
        return self._pkt

    def get(self):
        if self.found:
            if self.remote_host:
                ip = self.remote_host
            else:
                ip = self.remote_ip.src
            ping = self.found - self.last_try
        else:
            ip = None
            ping = None

        location = self.location if self.location else None
        return {'ttl': self.ttl, 'ping': ping, 'ip': ip, 'location': location}

    def __repr__(self):
        if self.found:
            if self.remote_host:
                ip = ":: %s" % self.remote_host
            else:
                ip = ":: %s" % self.remote_ip.src
            ping = "%0.3fs" % (self.found - self.last_try)
        else:
            ip = "??"
            ping = "-"

        location = ":: %s" % self.location if self.location else ""
        return "%02d. %s %s %s" % (self.ttl, ping, ip, location)


class TCPTraceroute:
    def __init__(self, destination):
        self.destination = destination
        self.protocol = "tcp"
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        self.hops = []
        self.out_queue = []
        self.waiting = True
        self.deferred = defer.Deferred()

        reactor.addReader(self)
        reactor.addWriter(self)

        # send 1st probe packet
        self.out_queue.append(Hop(self.destination, ttl=1, proto='tcp',
                                  dport=random.randint(2**10, 2**16),
                                  sport=random.randint(2**10, 2**16)))

    def log_prefix(self):
        return "Traceroute Protocol(%s)" %self.destination

    def fileno(self):
        return self.recv_socket.fileno()

    @defer.inlineCallbacks
    def hop_found(self, hop, ip, icmp):
        hop.remote_ip =ip
        hop







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