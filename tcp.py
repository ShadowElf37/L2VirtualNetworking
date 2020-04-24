from layer2 import EthernetFrame
from layer3 import IPv4
from layer4 import TCP, TCPFlags
from packet import Packet as BasePacket, Deconstructor
from session import BaseSession
import data
import socket
import sys

class Packet(BasePacket):
    reader = Deconstructor(EthernetFrame, IPv4, TCP)

    def __init__(self, *headers, payload=b'', encoding='utf-8'):
        if len(headers) == 1 and type(headers[0]) is bytes:
            parsed = self.reader.parse(headers[0])
            super().__init__(*parsed.headers, payload=parsed.payload)
        else:
            super().__init__(*headers, payload=payload, encoding=encoding, layer=4)

    @property
    def flags(self):
        return TCPFlags(self.get_header(TCP).get('flags').data)

    def to_mac(self, mac):
        return self.get_header(EthernetFrame).get('dst') == mac
    def to_ip(self, ip):
        return self.get_header(IPv4).get('dst') == ip
    def to_port(self, port):
        return self.get_header(TCP).get('dst') == port

    def from_mac(self, mac):
        return self.get_header(EthernetFrame).get('src') == mac
    def from_ip(self, ip):
        return self.get_header(IPv4).get('src') == ip
    def from_port(self, port):
        return self.get_header(TCP).get('src') == port


class Session(BaseSession):
    def __init__(self, from_mac, from_ip, from_port, to_mac, to_ip, to_port, encoding='utf-8'):
        super().__init__('Realtek')
        self.mac = from_mac
        self.ip = from_ip
        self.port = from_port
        self.dst_mac = to_mac
        self.dst_ip = to_ip
        self.dst_port = to_port
        self.encoding = encoding
        self.seq = 0
        self.ack = 0
        self.state = 0
        self.recv_window = 65535

    @property
    def host(self):
        return self.ip, self.port

    def recv(self, check_mac=True, check_ip=True, check_port=True):
        while True:
            self._recv(1)
            packet = Packet(self.read())
            print(packet.headers)
            if (packet.to_mac(self.mac) or not check_mac) and (packet.to_ip(self.ip) or not check_ip) and (packet.to_port(self.port) or not check_port):
                return packet

    def send(self, msg='', flags: TCPFlags = TCPFlags(), urg_field=0, dscp=0, ecn=0, ipflags=0, ipfrag=0):
        msg = bytes(msg, self.encoding)
        eth = EthernetFrame(
            self.dst_mac,
            self.mac,
            data.EtherType.ipv4
        )
        ip = IPv4(
            data.IGNORE,
            5,
            dscp,
            ecn,
            40 + len(msg),
            data.IGNORE,
            ipflags,
            ipfrag,
            255,
            data.IPPROTO.tcp,
            data.IGNORE,
            self.ip,
            self.dst_ip
        )
        tcp = TCP(
            self.port,
            self.dst_port,
            self.seq,
            self.ack,
            5,
            data.IGNORE,
            flags.pack(),
            self.recv_window,
            data.IGNORE,
            urg_field
        )
        packet = Packet(eth, ip, tcp, payload=msg, encoding=self.encoding)
        self.send_packet(packet.compile())


if __name__ == "__main__":
    import virtual

    tcp_connector

    device = virtual.Machine()

