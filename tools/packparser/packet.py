#!/usr/bin/env python

import struct
import logging


LOG = logging.getLogger(__name__)


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


from offset import *


class PacketError(Exception):
    pass


class PacketErrorMsg(PacketError):
    pass


class PacketVerError(PacketError):
    pass


class PacketItemUnexpected(PacketError):
    def __init__(self, target, name, unexpected_val):
        self.target = target
        self.name = name
        self.unexpected_val = unexpected_val

    def __str__(self):
        return "Packet {0} item {1} is unexcepted".format(self.target.__class__, self.name, self.unexpected_val)


class PacketWarn(Exception):
    pass


class PacketWarnMsg(PacketWarn):
    pass


class Packet(object):
    FORMAT = None

    def __init__(self):
        self.struct = [[k, l, None] for k, l in self.FORMAT]
        self.status = {}
        self.len = None

    def __getitem__(self, key):
        k_b = []
        for k, l, v in self.struct:
            if k.startswith(key):
                k_b.append(v)
            elif len(k_b) > 0:
                break
        return ''.join(k_b) or None

    def __setitem__(self, key, value):
        i = 0
        for k, l, v in self.struct:
            if k == key:
                self.struct[i][2] = value
                return True
            i += 1
        return False

    def iterate_packet_itemkey(self):
        return [k for k, l, v in self.struct]

    def iterate_packet_itemval(self):
        return [v for k, l, v in self.struct]

    def is_expected(self, name):
        try:
            with self.__getitem__(name) as it:
                _func = getattr(self, '_parse_{0}')
                if callable(_func):
                    return _func()
                else:
                    self.status[name] = it
        except e as PacketError:
            LOG.error(e)
            raise e
        except e as PacketWarn:
            LOG.warn(e)

    def pack(self, header, data):
        raise NotImplementedError()

    @classmethod
    def force_unpack(cls, data):
        raise NotImplementedError()

    @classmethod
    def safe_unpack(cls, data):
        raise NotImplementedError()


class packetIPv4(Packet):
    """
    IP V4 Header

    See details in RFC791.
    """
    FORMAT = [
        ('version', 4),
        ('header_length', 4),
        ('servcie_type', 8),
        ('total_length', 16),
        ('ident', 16),
        ('flag', 3),
        ('fragment_offset', 13),
        ('time_to_live', 8),
        ('protocol', 8),
        ('checksum', 16),
        ('src_addr', 32),
        ('dst_addr', 32),
    ]

    def _check_version(self):
        val = self.__getitem__('version')
        if val != 4:
            raise PacketVerError('Expected version 4, but it is {0}.'.format(val))
        self.status['version'] = 4

    def _check_header_length(self):
        val = self.__getitem__('header_length')
        if not (val >= 5):
            raise PacketErrorMsg('Dont need this packet because of its length is {0}'.format(val))
        self.status['header_length'] = val

    def _check_service_type(self):
        val = self.__getitem__('service_type')
        precedence_dict = {
            0: 'Routine',
            1: 'Priority',
            2: 'Immediate',
            3: 'Flash',
            4: 'Flash Override',
            5: 'CRITIC/ECP',
            6: 'Internetwork Control',
            7: 'Network Control'
        }
        precedence = (val & 224) >> 5
        self.status['precedence'] = precedence_dict.get(precedence, None)
        if not self.status['precedence']:
            raise PacketItemUnexpected(self, 'service_type', val)
        self.status['delay'] = 'Low' if (val & 16) >> 4 else 'Normal'
        self.status['throughput'] = 'Low' if (val & 8) >> 3 else 'Normal'
        self.status['relibility'] = 'Low' if (val & 4) >> 2 else 'Normal'

    def _parse_total_length(self):
        val = self.__getitem__('service_type')
        if val > 382:
            raise PacketWarnMsg('IP4 Packet length is too longger, val:{0}'.format(val))
        self.status['total_length'] = val

    def _parse_flag(self):
        val = self.__getitem__('flag')
        if (val & 4) >> 2:
            raise PacketItemUnexpected(self, 'flag', val)
        self.status['can_flagged'] = True if not (val & 2) >> 1 else False
        self.status['is_last'] = True if not val & 1 else False

    def _parse_protocol(self):
        """
        Copy choice from RFC790.
        """
        from ip_protocol import parse_protocol
        val = self.__getitem__('protocol')
        self.status['protocol'] = parse_protocol(val)
        if self.status['protocol']:
            self.status['protocol'] = 'Unassigned'

    def _parse_src_address(self):
        val = self.__getitem__('src_addr')
        self.status['src_addr'] = '.' .join(str((val >> 24) & 15),
                                            str((val >> 16) & 15),
                                            str((val >> 8) & 15),
                                            str(val & 15))

    def _parse_dst_address(self):
        val = self.__getitem__('dst_addr')
        self.status['dst_addr'] = '.' .join(str((val >> 24) & 15),
                                            str((val >> 16) & 15),
                                            str((val >> 8) & 15),
                                            str(val & 15))


class packetIPv4Tunnel(Packet):
    FORMAT = [
        ('tunnel_id1', 32),
        ('tunnel_id2', 32),
        ('src_addr', 32),
        ('dst_addr', 32),
        ('tunnel_flags', 16),
        ('tos', 8),
        ('ttl', 8),
        ('tp_src', 16),
        ('tp_dst', 16),
    ]


class packetGRE(Packet):
    FORMAT = [
        ('present', 1),
        ('reserved1', 12),
        ('version', 3),
        ('protocol', 16),
        ('checksum', 16),
        ('reserved2', 16),
    ]


i = packetIPv4()
i['version'] = 4
i['header_length'] = 8
offset_chat(i.struct)


class packetIPv6(Packet):
    FORMAT = [
        ('version', 4),
        ('traffic_class', 8),
        ('flow_label', 20),
        ('payload_len', 16),
        ('next_header', 8),
        ('hop_limit', 8),
        ('src_addr0', 32),
        ('src_addr1', 32),
        ('src_addr2', 32),
        ('src_addr3', 32),
        ('dst_addr0', 32),
        ('dst_addr1', 32),
        ('dst_addr2', 32),
        ('dst_addr3', 32),
    ]


class packetTCP(Packet):
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


class packetUDP(Packet):
    FORMAT = [
        ('src_port', 16),
        ('dst_port', 16),
        ('length', 16),
        ('checksum', 16),
    ]


class packetICMP(Packet):
    FORMAT = [
        ('type', 8),
        ('code', 8),
        ('checksum', 16),
        ('spec_info', 32),
    ]


