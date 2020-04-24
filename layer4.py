from packet import *
from fields import *

class UDP(Header):
    FIELDS = (
        Field(16, name='src_port'),
        Field(16, name='dst_port'),
        Field(16, name='length'),  # header + data in bytes
        TCPChecksum(16)
    )

class TCP(Header):
    FIELDS = (
        Field(16, name='src'),  # port
        Field(16, name='dst'),  # port
        Field(32, name='seq'),
        Field(32, name='ack'),
        Field(4, name='header_size'),  # 5-15, usually 5
        Fixed(3, value=0),  # reserved
        Field(9, name='flags'),
        Field(16, name='window'),
        TCPChecksum(16),
        Field(16, name='urgent')
    )

class TCPFlags:
    def __init__(self, full_int=0, ns=0, cwr=0, ece=0, urg=0, ack=0, psh=0, rst=0, syn=0, fin=0):
        if full_int:
            self.ns, self.cwr, self.ece, self.urg, self.ack, self.psh, self.rst, self.syn, self.fin = map(int, list(force_bits(full_int, 9)))
        else:
            self.ns = ns
            self.cwr = cwr
            self.ece = ece
            self.urg = urg
            self.ack = ack
            self.psh = psh
            self.rst = rst
            self.syn = syn
            self.fin = fin
    def pack(self):
        return (self.ns << 8) + (self.cwr << 7) + (self.ece << 6) + (self.urg << 5) + (self.ack << 4) + (self.psh << 3) + (self.rst << 2) + (self.syn << 1) + self.fin