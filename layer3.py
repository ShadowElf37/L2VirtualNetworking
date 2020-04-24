from packet import *
from fields import *

class IPv4(Header):
    FIELDS = (
        Fixed(4, value=4, name='version'),  # version
        Field(4, name='ihl'),  # headerlen
        Field(6, name='dscp'),  # dscp
        Field(2, name='ecn'),  # ecn
        Field(16, name='length'),  # len in bytes
        Field(16, name='identification'),  # id
        Field(3, name='flags'),  # flags
        Field(13, name='frag_offset'),  # frag offset
        Field(8, name='ttl'),  # ttl
        Field(8, name='protocol'),  # proto
        IPChecksum(16),
        Field(32, name='src'),  # src ip
        Field(32, name='dst')  # dst ip
    )

class IPv6(Header):
    FIELDS = (
        Fixed(4, value=6),
        Field(6),  # dscp
        Field(2),  # ecn
        Field(20),
        Field(16),
        Field(8),
        Field(8),
        Field(128),
        Field(128)
    )


class ICMP(Header):
    FIELDS = (
        Field(8, name='type'),
        Field(8, name='code'),
        IPChecksum(16),
        Field(32, name='data')
    )

"""
from layer2 import EthernetFrame
sample = b'X\xefhp\xd12\xf8\xb1V\xf3t\x1e\x08\x00E\x00\x00\x14\x00\x00@\x00 =\xd6y\xc0\xa8\x01\xe2\xc0\xa8\x01\x01'
d = Deconstructor(EthernetFrame, IPv4)
p = d.parse(sample)
print(p)
print(p.get_header(EthernetFrame).fields[0])
"""