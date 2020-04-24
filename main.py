from ops import ltb
import rawsocket
import data
from layer2 import *
from layer3 import *
from layer4 import *
import tcp
from packet import Packet

MAC = 0xf8b156fe741e
IP = ltb([192, 168, 1, 226])
ROUTER = ltb([192, 168, 1, 1])
ROUTER_MAC = 0x58ef6870d132

socket = rawsocket.socket('Realtek')
eth = EthernetFrame(
    ROUTER_MAC,
    MAC,
    data.EtherType.ipv4
)

ip = IPv4(
    data.IGNORE,
    5,
    0b000000,
    0b00,
    30,  # packet len in bytes
    0,
    0b010,  # fragmentation might be cool
    0,  # frag offset
    255,  # ttl
    data.IPPROTO.udp,
    data.IGNORE,
    IP,
    ROUTER
)

icmp = ICMP(
    data.ICMP.echo1,
    0,
    0,
    0
)

udp = UDP(
    0,
    80,
    10,
    0
)

session = tcp.Session(MAC, IP, 80, ROUTER_MAC, ROUTER, 80)
session.send('hi', TCPFlags(syn=1))
p = session.recv()
if p.flags.syn and p.flags.ack:
    session.seq = p.get_header(TCP).get('ack').data+1
    session.ack = p.get_header(TCP).get('seq').data+1
    session.send('', TCPFlags(ack=1))
print(session.recv().headers)

"""
packet = Packet(eth, ip, udp, payload=b'hi')

socket.send(packet.compile())

socket.recv_all(5)
received = socket.read(5)

dec = Deconstructor(EthernetFrame, IPv4, ICMP)
packets = []
for p in received:
    packets.append(dec.parse(p))

for p in packets:
    #print(hex(p.get_header(EthernetFrame).get('dst').data))
    if p.get_header(EthernetFrame).get('dst') == MAC and p.get_header(IPv4).get('protocol') == data.IPPROTO.icmp:
        print(p.get_header(ICMP).fields)
"""
socket.close()