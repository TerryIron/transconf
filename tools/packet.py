#!/usr/bin/env python

import struct
from offset import offsetchat


class Packet(object):
    FORMAT = None

    def __init__(self):
        self.struct = [[k, l, None] for k, l in self.FORMAT]
        self.len = None

    def __getitem__(self, key):
        for k, l, v in self.struct:
            if k == key:
                return v

    def __setitem__(self, key, value):
        i = 0
        for k, l, v in self.struct:
            if k == key:
                self.struct[i][2] = value
                return True
            i += 1
        return False

    def lazy_packs(self, datas):
        return struct.pack(''.join([str(chr(len(i))) + 's' for i in datas]), *datas)

    def packs(self, lengths, datas):
        return struct.pack(''.join([str(chr(i)) + 's' for i in lengths]), *datas)

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
    FORMAT = [
        ('version', 4),
        ('header_length', 4),
        ('servcie_type', 8),
        ('total_length', 16),
        ('ident', 16),
        ('ip_flag', 3),
        ('fragment_offset', 13),
        ('time_to_live', 8),
        ('protocol', 8),
        ('checksum', 16),
        ('src_address', 32),
        ('dest_address', 32),
    ]

    def __init__(self, dest_ip, src_ip, version=4):
        super(IP_Packet, self).__init__()
        pass

i = IP_Packet('1.2.3.4', '4.4.4.4')
i['version'] = 4
offsetchat(i.struct)


class TCP_Packet(Packet):
    def __init__(self, dest_port, src_port):
        super(TCP_Packet, self).__init__()
        pass


class UDP_Packet(Packet):
    def __init__(self, dest_port, src_port):
        super(UDP_Packet, self).__init__()
        pass


class ICMP_Packet(Packet):
    def __init__(self, typ, code):
        super(ICMP_Packet, self).__init__()
        pass

