from ops import force_bits, ltb
from abc import ABC, abstractmethod

class Field:
    def __init__(self, size, name='', default=0):
        self.size = size
        self.data = default
        self.name = name
        self.theoretical = None  # useful for DynamicField subclasses

    def __repr__(self):
        return '<%s bits: %s>' % (self.size, hex(self.data))

    def __eq__(self, other):
        if type(other) is Field:
            return self.data == other.data
        return self.data == other

    def set(self, i: int):
        self.data = i

    def get(self):
        return self.data

    def pack(self):
        return force_bits(self.data, self.size)


class DynamicField(ABC, Field):
    @abstractmethod
    def recalculate(self, *packet):
        pass

    def set(self, i):
        self.theoretical = i  # can be used to check the checksum of a received packet

class GlobalField(DynamicField):
    def recalculate(self, packet):
        pass


class Fixed(DynamicField):
    def __init__(self, size, value, name=''):
        super().__init__(size, name=name)
        self.data = value

    def recalculate(self, *packet):
        # Useful for IP version number etc. that really should have one and only one value, or for padding / reserved
        pass


class IPChecksum(DynamicField):
    def __init__(self, *args, **kwargs):
        super().__init__(size=16, name='checksum')

    @classmethod
    def checksum(self, bitstream):
        tempsum = 0
        for i in range(len(bitstream) // 16):  # add up all the 16-bit words
            tempsum += int(bitstream[i * 16:(i + 1) * 16], 2)
        while tempsum > 0xffff:  # add the first digits that aren't part of the last 16, i.e. "carry bits", until there are no carry bits
            tempsum = int(bin(tempsum)[:-16], 2) + int(bin(tempsum)[-16:], 2)
        return tempsum ^ 0xffff  # one's complement

    def recalculate(self, *fields):
        self.data = 0
        header = ''.join(field.pack() for field in fields)  # bit stream
        self.data = self.checksum(header)


class TCPChecksum(IPChecksum, GlobalField):
    def recalculate(self, packet):
        self.data = 0
        # this will work for UDP as well
        ip = packet.headers[1]
        tcp = ''.join(field.pack() for field in packet.headers[2].fields)
        print(packet.headers[2].fields)
        data = ''.join([h.pack() for h in packet.headers[3:]]) + force_bits(ltb([char for char in packet.payload]), len(packet.payload)*8)

        if ip.get('version') == 4:
            ip_pseudo = ip.get('src').pack() + ip.get('dst').pack() + force_bits(0, n=8) + ip.get(
                'protocol').pack() + force_bits(len(tcp+data) // 8, 16)
        elif ip.get('version') == 6:
            ip_pseudo = ip.get('src').pack() + ip.get('dst').pack() + force_bits(len(tcp+data) // 8, 32) + force_bits(0,n=24) + ip.get('protocol').pack()

        header = ip_pseudo + tcp + data
        while len(header) % 16 != 0:  # whole thing should be 2 octets wide
            header += '0'

        self.data = IPChecksum.checksum(header)
