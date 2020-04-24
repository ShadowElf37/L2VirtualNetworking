import platform
from threading import Thread
from queue import SimpleQueue

if platform.system() == 'Windows':
    import winpcapy as _wpc

    def get_devices():
        return _wpc.WinPcapDevices.list_devices()

    class socket:
        def __init__(self, device_pattern, promiscuous=1, timeout=1000):
            self.interface_id, self.interface = _wpc.WinPcapDevices.get_matching_device('*'+device_pattern+'*')
            if self.interface is None:
                raise FileNotFoundError('No network device fits that pattern')
            self.socket = _wpc.WinPcap(self.interface_id, promiscuous=promiscuous, timeout=timeout)
            self.socket.__enter__()
            self.rthread = Thread(target=self.recv_all, daemon=True)
            self.rbuffer = SimpleQueue()
            self.listening = False

        def send(self, bytestr: bytes):
            self.socket.send(bytestr)

        def recv_all_thread(self):
            self.rthread.start()
        def recv_all(self, limit=0):
            self.listening = True
            self.socket.run(self._cb, limit=limit)
            self.listening = False
            self.rthread = Thread(target=self.recv_all, daemon=True)

        def read(self, count=1):
            if count == 1:
                return self.rbuffer.get()
            else:
                packets = []
                for _ in range(count):
                    packets.append(self.rbuffer.get())
                return packets

        def stop(self):
            self.socket.stop()

        def _cb(self, win_pcap, param, header, data):
            self.rbuffer.put(data)

        def close(self):
            self.socket.__exit__(None, None, None)

else:
    import socket as _s
    class socket:
        def __init__(self, device, promiscuous=1, timeout=1000):
            self.interface = self.interface_id = device
            self.socket = _s.socket(_s.AF_PACKET, _s.SOCK_RAW)
            self.socket.settimeout(timeout)
            self.socket.bind((device, 0))
            self.rthread = Thread(target=self.recv_all)
            self.rbuffer = SimpleQueue()
            self.listening = False

        def send(self, bytestr: bytes):
            self.socket.send(bytestr)

        def recv_all_thread(self):
            self.rthread.start()
        def recv_all(self, limit=0):
            self.listening = True
            i = 0
            while self.listening and i < limit:
                r = self.socket.recv(65535)
                if r:
                    self.rbuffer.put(r)
                    i += 1
            self.listening = False
            self.rthread = Thread(target=self.recv_all, daemon=True)

        def read(self, count=1):
            if count == 1:
                return self.rbuffer.get()
            else:
                packets = []
                for _ in range(count):
                    packets.append(self.rbuffer.get())
                return packets

        def stop(self):
            self.listening = False

        def close(self):
            self.socket.close()
