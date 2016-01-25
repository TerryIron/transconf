#!/usr/bin/env python

import urllib
import json
import sys
import commands
import struct


class Packet(object):
    def __init__(self):
        self.struct = None

    def lazy_packs(self, datas):
        return struct.pack(''.join([str(chr(len(i))) + 's' for i in lengths), *datas)

    def packs(self, lengths, datas):
        return struct.pack(''.join([str(chr(i)) + 's' for i in lengths), *datas)

    def pack(self, length, data):
        return struct.pack('{0}s'.format(length), str(data))

    def unpack(self, length, data):
        return struct.unpack('{0}s'.format(length), data)[0]

    def append(self, old_packdata, packdata):
        return struct.pack('{0}s{1}s'.format(len(old_packdata), len(packdata)), 
                           old_packdata, 
                           packdata)

    def pop(self, length, packdata):
        return struct.unpack('{0}s{1}s'.format(length, len(packdata) - length), 
                             packdata)

    def translate(self):
        raise NotImplementedError()


class IP_Packet(Packet):
    def __init__(self, dest_ip, src_ip, version=4):
        version = self.packs([1, 1, 2], [version, 4, 0xc0])
        dest_ip = self.packs([1, 1, 1, 1], dest_ip.split('.'))
        src_ip = self.packs([1, 1, 1, 1], src_ip.split('.'))
        pass


class TCP_Packet(Packet):
    def __init__(self, dest_port, src_port):
        pass


class UDP_Packet(Packet):
    def __init__(self, dest_port, src_port):
        pass


class ICMP_Packet(Packet):
    def __init__(self, typ, code):
        pass


def traceroute(url):
    output = commands.getoutput('traceroute {0}'.format(url))
    output = [i for i in output.split(' ')[7:] if len(i.split('.')) == 4]
    j = []
    for i in output:
        if i not in j:
            ip_location(i)
        j = [i]


def ip_location(ip):
    f = urllib.urlopen('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip={0}'.format(ip)).read()
    j = json.loads(f.split('=')[1][:-1])
    if j.get('ret', 0) != 1:
        location = 'local'
    else:
        location = '{0}:{1}:{2}'.format(j.get('country', '').encode('utf8'), 
                                        j.get('province', '').encode('utf8'), 
                                        j.get('city', '').encode('utf8'))
        if location.endswith('::'):
            location = location[:-2]
    print 'IP:{0}, Location:{1}'.format(ip, location)


if __name__ == "__main__":
    traceroute(sys.argv[1])
