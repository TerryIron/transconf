import socket
import codecs


## TCP
#SOCK_TYPE=socket.SOCK_STREAM
## UDP
#SOCK_TYPE=socket.SOCK_DGRAM


class Protocol(object):
    FAMILY = socket.AF_INET
    TYPE = socket.SOCK_RAW
    PROTO = None
    HEAD_SIZE = 0
    SIZE = 0

    def __init__(self, ip, port):
        self.sock = socket.socket(self.FAMILY, self.TYPE, self.PROTO)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def catch(self):
        return self.sock.recv(self.SIZE)


class IPPacket(Protocol):
    # IP procotol
    PROTO = socket.IPPROTO_IP
    SIZE = 1500
    HEAD_SIZE = 20


class TCPPacket(Protocol):
    # TCP procotol
    PROTO=socket.IPPROTO_TCP
    SIZE = 1460
    HEAD_SIZE = 20


class UDPPacket(Protocol):
    # UDP procotol
    PROTO=socket.IPPROTO_UDP
    SIZE = 1472
    HEAD_SIZE = 8


class RoutePacket(Protocol):
    # ROUTING procotol
    PROTO=socket.IPPROTO_ROUTING
    SIZE = 64 
    HEAD_SIZE = 24


class ICMPPacket(Protocol):
    # ICMP procotol
    PROTO=socket.IPPROTO_ICMP
    SIZE = 64 
    HEAD_SIZE = 8


class GREPacket(Protocol):
    # GRE procotol
    PROTO=socket.IPPROTO_GRE


class RawPacket(Protocol):
    # RAW procotol
    PROTO=socket.IPPROTO_RAW


IP='10.3.3.152'
PORT=0


def main():
    s = ICMPPacket(IP, PORT)
    while True:
        buf = [st for st in s.catch()]
        print 'LENGTH:{0}, DATA:{1}'.format(len(buf), buf)


if __name__ == '__main__':
    main()
