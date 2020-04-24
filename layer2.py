from packet import *
from fields import *

class EthernetFrame(Header):
    FIELDS = (
        Field(6*8, name='dst'),
        Field(6*8, name='src'),
        Field(2*8, name='protocol')
    )

class ARP(Header):
    FIELDS = (
        Field(2*8),
        Field(2*8),
        Field(1*8),
        Field(1*8),
        Field(2*8),
        Field(6*8),
        Field(4*8),
        Field(6*8),
        Field(4*8)
    )

"""
arp = ARP(
    0x01,
    data.EtherType.ipv4,
    0x06,
    0x04,
    0x01,
    MAC,
    IP,
    0x0,
    ltb([192, 168, 1, 1])
)
"""