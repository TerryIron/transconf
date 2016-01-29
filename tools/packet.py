#!/usr/bin/env python

import struct
from offset import *


def lazy_packs(datas):
    return struct.pack(''.join([str(chr(len(i))) + 's' for i in datas]), *datas)


def packs(datas, lengths):
    return struct.pack(''.join([str(chr(i)) + 's' for i in lengths]), *datas)


def pack(data, length):
    return struct.pack('{0}s'.format(length), str(data))


def unpack(data, length):
    return struct.unpack('{0}s'.format(length), data)[0]


def append(old_packdata, packdata):
    return struct.pack('{0}s{1}s'.format(len(old_packdata), len(packdata)),
                       old_packdata,
                       packdata)


def pop(length, packdata):
    return struct.unpack('{0}s{1}s'.format(length, len(packdata) - length),
                         packdata)[0]


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

    def pack(self):
        raise NotImplementedError()

    @classmethod
    def force_unpack(cls, data):
        raise NotImplementedError()

    @classmethod
    def safe_unpack(cls, data):
        raise NotImplementedError()


class IP4_Packet(Packet):
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
        ('dst_address', 32),
    ]

    def __init__(self, dest_ip, src_ip, version=4):
        super(IP4_Packet, self).__init__()
        pass

i = IP4_Packet('1.2.3.4', '4.4.4.4')
i['version'] = 4
i['header_length'] = 8
offset_chat(i.struct)


class IP6_Packet(Packet):
    FORMAT = [
        ('version', 4),
        ('traffic_class', 8),
        ('flow_label', 20),
        ('payload_len', 16),
        ('next_header', 8),
        ('hop_limit', 8),
        ('src_address0', 32),
        ('src_address1', 32),
        ('src_address2', 32),
        ('src_address3', 32),
        ('dst_address0', 32),
        ('dst_address1', 32),
        ('dst_address2', 32),
        ('dst_address3', 32),
    ]

    def __init__(self, dest_ip, src_ip, version=6):
        super(IP6_Packet, self).__init__()
        pass


class TCP_Packet(Packet):
    FORMAT = [
        ('src_port', 16),
        ('dst_port', 16),
        ('seq_num', 32),
        ('ack_num', 32),
        ('offset', 4),
        ('reserved', 4),
        ('flags', 8),
        ('window', 8),
        ('checksum', 16),
        ('urgent_pointer', 16),
    ]

    def __init__(self, dest_port, src_port):
        super(TCP_Packet, self).__init__()
        pass


class UDP_Packet(Packet):
    FORMAT = [
        ('src_port', 16),
        ('dst_port', 16),
        ('length', 16),
        ('checksum', 16),
    ]

    def __init__(self, dest_port, src_port):
        super(UDP_Packet, self).__init__()
        pass


class ICMP_Packet(Packet):
    FORMAT = [
        ('type', 8),
        ('code', 8),
        ('checksum', 16),
        ('spec_info', 32),
    ]

    def __init__(self, typ, code):
        super(ICMP_Packet, self).__init__()
        pass

