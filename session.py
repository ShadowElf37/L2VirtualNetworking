from rawsocket import socket
from packet import Packet

class BaseSession:
    def __init__(self, device):
        self.socket = socket(device)
        self.wbuffer = []
        self.rbuffer = []

    def write(self, data):
        self.wbuffer.append(data)

    def flush(self, count=0):
        for _ in range(count or len(self.wbuffer)):
            self.send_raw(self.wbuffer.pop(0))

    def read(self):
        return self.rbuffer.pop(0)

    def send_raw(self, data):
        self.socket.send(data)

    def send_packet(self, packet: Packet):
        self.socket.send(packet.compile())

    def _recv(self, count=1):
        self.socket.recv_all(count)
        self.rbuffer.append(self.socket.read(1))
