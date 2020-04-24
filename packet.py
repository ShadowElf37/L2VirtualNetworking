from fields import DynamicField, GlobalField
from copy import deepcopy
from ops import bin_to_bytes, force_bits


class Header:
    FIELDS = ()

    def __init__(self, *fields, **kwfields):
        self.packet = None  # will be needed for udp checksum
        # we want NEW FIELDS that we can fill in however we want
        self.fields = list(deepcopy(self.FIELDS))
        for i, value in enumerate(fields):
            self.fields[i].set(value)

        for name, value in kwfields.items():
            self.get(name).set(value)

    def __repr__(self):
        return '<%s %d bytes | %s...>' % (self.__class__.__qualname__, sum(f.size/8 for f in self.fields), hex(int(self.pack(True)[:32], 2)))

    def pack(self, nocalc=False):
        # stuff all the fields together in a long binary string
        if nocalc is False:  # nocalc means no checksums will be calculated
            for field in self.fields:
                if issubclass(field.__class__, GlobalField):
                    # tcp checksum
                    field.recalculate(self.packet)
                elif issubclass(field.__class__, DynamicField):
                    # ip checksum etc.
                    field.recalculate(*self.fields)
        return ''.join(field.pack() for field in self.fields)

    def get(self, name):
        # return a field by its name if you've set that up
        for field in self.fields:
            if field.name.lower() == name.lower():
                return field
        return None


class Packet:
    def __init__(self, *headers, payload=b'', encoding='utf-8', layer=2):
        self.layer = layer
        self.encoding = encoding
        self.headers = list(headers)
        for header in self.headers:
            header.packet = self
        self.set_payload(payload)

    def __repr__(self):
        return '<%s Packet %d bytes>' % ('+'.join(h.__class__.__qualname__ for h in self.headers), sum(sum(f.size/8 for f in h.fields) for h in self.headers))

    def set_payload(self, payload):
        if type(payload) is str:
            self.payload = payload.encode(self.encoding)
        else:
            self.payload = payload

    def add_header(self, header):
        self.headers.append(header)
    def get_header(self, htype) -> Header:
        # get a header by header type, assuming no duplicates (i.e. encapsulation)
        for header in self.headers:
            if type(header) is htype:
                return header
        return None

    def compile(self):
        # pack all the headers and make bit stream into bytes for sending
        data = ''.join(h.pack() for h in self.headers)
        # print('HEADER BITS:', data)
        # print('FULL PACKET:', bin_to_bytes(data) + self.payload)
        return bin_to_bytes(data) + self.payload


class Deconstructor:
    def __init__(self, *header_types):
        self.types = header_types

    def parse(self, data):
        headers = []
        bins = []
        for char in data:
            bins.append(force_bits(char, 8))  # basically we are going to take all the data and make it into a binary string
        binstr = ''.join(bins)
        index = 0

        # then we are going to loop through all the header types we wer given
        for header in self.types:
            # we're gonna instantiate a new one to fill in
            headers.append(h := header())
            # and then go through all the fields and pull the needed bits from our bit stream BY FIELD SIZE
            for field in h.fields:
                # this all gets thrown in our new headers' fields
                next = binstr[index:index+field.size]
                if not next:
                    break
                field.set(int(next, 2))
                index += field.size

        # check for payload, i.e. we haven't reached the end of the packet using only headers
        if index != len(data)*8:
            payload = data[index*8:]
        else:
            payload = b''

        # and boom return a fully formed packet
        return Packet(*headers, payload=payload)
