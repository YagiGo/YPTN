#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2012 Alexandre Fiori 2018 Zhaoxin Wu
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

import json
import operator
import os
import socket
import struct
import sys
import time
import random

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import threads
from twisted.python import usage
from twisted.web.client import getPage
from DataProcess import DbDataAccess
from pymongo import MongoClient
import traceback


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
        self.dport = 4242 # set to 4242
        self.sport = 4242 # set to 4242

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
        self.dport = 4242 # set to 4242
        self.sport = 4242 # set to 4242
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


def pprintp(packet):
    """
    Used to pretty print packets.
    """
    lines = []
    line = []
    for i, byte in enumerate(packet):
        line.append(("%.2x" % ord(byte), byte))
        if (i + 1) % 8 == 0:
            lines.append(line)
            line = []

    lines.append(line)

    for row in lines:
        left = ""
        right = "   " * (8 - len(row))
        for y in row:
            left += "%s " % y[0]
            right += "%s" % y[1]

        print(left + "     " + right)


@defer.inlineCallbacks
def geoip_lookup(ip):
    try:
        r = yield getPage("http://freegeoip.net/json/%s" % ip)
        d = json.loads(r)
        items = [d["country_name"], d["region_name"], d["city"]]
        text = ", ".join([s for s in items if s])
        defer.returnValue(text.encode("utf-8"))
    except Exception as error:
        # print(str(error))
        defer.returnValue("Unknown location")


@defer.inlineCallbacks
def reverse_lookup(ip):
    try:
        r = yield threads.deferToThread(socket.gethostbyaddr, ip)
        defer.returnValue(r[0])
    except Exception:
        defer.returnValue(None)


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
            self.ip.data = self.tcp.assemble()  # Something went wrong here, need fix!
            # Updated, fixed, port numbers were not fed into the class
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


class TracerouteProtocol(object):
    def __init__(self, target, **settings):
        self.target = target
        self.settings = settings
        self.verbose = settings.get("verbose")
        self.proto = settings.get("proto")
        # print("PROTOCOL IS " + self.proto)
        self.rfd = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                socket.IPPROTO_ICMP)
        if self.proto == "icmp":
            print("Benchmark using ICMP")
            self.sfd = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_ICMP)
        elif self.proto == "udp":
            print("Benchmark using UDP")
            self.sfd = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_UDP)
            # Fix bugs in UDP
        elif self.proto == "tcp":
            print("Benchmark using TCP")
            # print ("THIS SHOULD ACTIVATE")
            self.sfd = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.IPPROTO_TCP)

        self.rfd.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.sfd.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        self.hops = []
        self.out_queue = []
        self.waiting = True
        self.deferred = defer.Deferred()

        reactor.addReader(self)
        reactor.addWriter(self)

        # send 1st probe packet
        self.out_queue.append(Hop(self.target, 1,
                                  settings.get("proto"),
                                  self.settings.get("dport"),
                                  self.settings.get("sport")))

    def logPrefix(self):
        return "TracerouteProtocol(%s)" % self.target

    def fileno(self):
        return self.rfd.fileno()

    @defer.inlineCallbacks
    def hopFound(self, hop, ip, icmp):
        hop.remote_ip = ip
        hop.remote_icmp = icmp

        if (ip and icmp):
            hop.found = time.time()
            if self.settings.get("geoip_lookup") is True:
                hop.location = yield geoip_lookup(ip.src)

            if self.settings.get("reverse_lookup") is True:
                hop.remote_host = yield reverse_lookup(ip.src)

        ttl = hop.ttl + 1
        last = self.hops[-2:]
        if (ip is not None and len(last) == 2 and last[0].remote_ip == ip) or \
           (ttl > (self.settings.get("max_hops", 30) + 1)):
            done = True
        else:
            done = False

        if not done:
            cb = self.settings.get("hop_callback")
            if callable(cb):
                yield defer.maybeDeferred(cb, hop)

        if not self.waiting or done:
            if self.deferred:
                self.deferred.callback(self.hops)
                self.deferred = None
        else:
            self.out_queue.append(Hop(self.target, ttl,
                                      self.settings.get("proto"),
                                      self.settings.get("dport"),
                                      self.settings.get("sport")))

    def doRead(self):
        if not self.waiting or not self.hops:
            return

        pkt = self.rfd.recv(4096)
        # disassemble ip header
        ip = iphdr.disassemble(pkt[:20])

        # print("Got this packet:")
        # print("src %s" % ip.src)
        # pprintp(pkt)

        if ip.proto != socket.IPPROTO_ICMP:
            return

        found = False

        # disassemble icmp header
        icmp = icmphdr.disassemble(pkt[20:28])
        if icmp.type == 0 and icmp.id == self.hops[-1].icmp.id:
            found = True
        elif icmp.type == 11:
            # disassemble referenced ip header
            ref = iphdr.disassemble(pkt[28:48])
            if ref.dst == self.target:
                found = True

        if ip.src == self.target:
            self.waiting = False

        if found:
            self.hopFound(self.hops[-1], ip, icmp)

    def hopTimeout(self, hop, *ign):
        if not hop.found:
            if hop.tries < self.settings.get("max_tries", 3):
                # retry
                self.out_queue.append(hop)
                # count retry times here
            else:
                # give up and move forward
                self.hopFound(hop, None, None)

    def doWrite(self):
        if self.waiting and self.out_queue:
            hop = self.out_queue.pop(0)
            pkt = hop.pkt
            if not self.hops or (self.hops and hop.ttl != self.hops[-1].ttl):
                self.hops.append(hop)

            self.sfd.sendto(pkt, (hop.ip.dst, 0))

            timeout = self.settings.get("timeout", 1)
            reactor.callLater(timeout, self.hopTimeout, hop)

    def connectionLost(self, why):
        pass


def traceroute(target, **settings):
    tr = TracerouteProtocol(target, **settings)
    return tr.deferred


@defer.inlineCallbacks
def start_trace(targets, **settings):
    result = []
    for target in targets:
        benchmark_result = {} # init dict for storing benchmark result
        time_cost = 0.0 # init time counter
        print("currently benchmarking " + target )
        benchmark_result['url'] = target
        try:
            target = socket.gethostbyname(target)
            benchmark_result['url_host'] = target
        except Exception as e:
            print("could not resolve '%s': %s" % (target, str(e)))
            sys.exit(1)
        # print("This works!")
        hops = yield traceroute(target, **settings)
        # time_cost += hops.get()['ping']
        for hop in hops:
            try:
                # print(hop)
                time_cost += hop.get()['ping'] * 1000
                # print(time_cost)
            except Exception:
                print("opps, something broke here")
                traceback.print_exc()
                pass # To prevent unresponsive or unreachable ones
        last_hop = hops[-1]
        last_stats = last_hop.get()
        # benchmark_result['last_hop_ip'] = socket.gethostbyname(last_stats['ip'])
        hop_counter = last_stats['ttl']
        if settings["hop_callback"] is None:
            print(last_hop)

        if settings['serial']:
            import serial
            ser = serial.Serial(
                    port=settings['serial'],
                    baudrate=9600)
            ser.open()
            ser.write('?f')
            ser.write(last_hop.remote_ip.src)
            ser.write('?n')
            ser.write("%0.3fs" % last_stats['ping'])
            ser.close()
        benchmark_result['time_cost'] = time_cost
        benchmark_result['hops'] = hop_counter
        print(benchmark_result)
        print('\n')
    result.append(benchmark_result)
    # print(result)
        # time.sleep(1)
    reactor.stop()

class Options(usage.Options):
    optFlags = [
        ["quiet", "q", "Only print results at the end."],
        ["no-dns", "n", "Show numeric IPs only, not their host names."],
        ["no-geoip", "g", "Do not collect and show GeoIP information"],
        ["verbose", "v", "Be more verbose"],
        ["help", "h", "Show this help"],
    ]
    optParameters = [
        ["timeout", "t", 2, "Timeout for probe packets"],
        ["tries", "r", 3, "How many tries before give up probing a hop"],
        ["proto", "p", "icmp", "What protocol to use (tcp, udp, icmp)"],
        ["dport", "d", random.randint(2 ** 10, 2 ** 16),
                                    "Destination port (TCP and UDP only)"],
        ["sport", "s", random.randint(2 ** 10, 2 ** 16),
                                    "Source port (TCP and UDP only)"],
        ["max_hops", "m", 30, "Max number of hops to probe"],
        ["serial", "S", None, "Output last hop to serial"]
    ]


def network_benchmark(dbAddr, dbPort, dbName, user_agent):
    """

    :param dbAddr: String, db Address
    :param dbPort: int, db port
    :param dbName: String, default db name
    :param user_agent: string, user-agent in header, used for locating user's collection in the db

    :return: benchmark result
    """

    # This function here get most accessed url from the db based on user-agent
    # And perform network condition benchmark to each and every one of them.
    test_obj = DbDataAccess(dbClient=MongoClient(dbAddr, dbPort), dbName=dbName)
    # test_obj.get_url_and_time(user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")
    test_obj = DbDataAccess(dbClient=MongoClient(dbAddr, dbPort), dbName=dbName)
    # test_obj.get_url_and_time(user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")
    benchmark_urls = test_obj.get_url_and_time(user_agent=user_agent)
    main(dest=benchmark_urls)



def main(dest):
    def show(hop):
        print hop

    defaults = dict(hop_callback=show,
                    reverse_lookup=True,
                    geoip_lookup=True,
                    timeout=2,
                    proto="icmp",
                    dport=None,
                    sport=None,
                    serial=None,
                    verbose=False,
                    max_tries=3,
                    max_hops=30)


    """
    if len(sys.argv) < 2:
        print("Usage: %s [options] host" % (sys.argv[0]))
        print("%s: Try --help for usage details." % (sys.argv[0]))
        sys.exit(1)
    """
    # target = sys.argv.pop(-1) if sys.argv[-1][0] != "-" else ""
    # Using the parameters for testing purpose only!
    target = dest
    config = Options()
    try:
        config.parseOptions()
        if not target:
            raise
    except usage.UsageError as e:
        print("%s: %s" % (sys.argv[0], e))
        print("%s: Try --help for usage details." % (sys.argv[0]))
        sys.exit(1)

    settings = defaults.copy()
    settings['proto'] = 'icmp'
    """
    if config.get("quiet"):
        settings["hop_callback"] = None
    if config.get("no-dns"):
        settings["reverse_lookup"] = False
    if config.get("no-geoip"):
        settings["geoip_lookup"] = False
    if config.get("verbose"):
        settings["verbose"] = True
    if "timeout" in config:
        settings["timeout"] = config["timeout"]ping
    if "tries" in config:
        settings["max_tries"] = int(config["tries"])
    if "proto" in config:
        settings["proto"] = config["proto"]
    if "max_hops" in config:
        settings["max_hops"] = config["max_hops"]
    if "dport" in config:
        settings["dport"] = int(config["dport"])
    if "sport" in config:
        settings["sport"] = int(config["sport"])
    if "serial" in config and config['serial']:
        settings["serial"] = config["serial"]
    """
    if hasattr(os, "getuid") and os.getuid():
        print("traceroute needs root privileges for the raw socket")
        sys.exit(1)
    reactor.callWhenRunning(start_trace, target, **settings)
    # You can't restart the reactor, but you should be able to run it more times by forking a separate process
    reactor.run()
    # time.sleep(1)
    # reactor.stop()


if __name__ == "__main__":
    # Alexa top 50 sites test set
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
    test_site = ["www.softlab.cs.tsukuba.ac.jp"]
    test_site2 = ['www.netflix.com']
    test_site3 = ['www.google.com']
    # for site in test_site:
        # main(dest=site)
    # main(dest = test_sites)
    network_benchmark(dbAddr="localhost", dbPort=27017, dbName="test",
        user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")
