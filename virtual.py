from collections import defaultdict
from registry import MACREGISTRY, PIDREGISTRY
from abc import ABC, abstractmethod
import queue
import threading

REGISTER = MACREGISTRY()

class NoEndConnected(BaseException):
    pass
class InterfaceNotOpen(BaseException):
    pass
class InterfaceDoesNotExist(BaseException):
    pass


class Process(ABC):
    def __init__(self, pid):
        self.pid = pid

    def stop(self):
        return

    @abstractmethod
    def update(self, code):
        pass

class Machine:
    def __init__(self):
        self._ports = defaultdict(None)
        self.eth = REGISTER.new()
        self.pid = PIDREGISTRY()
        self.processes = defaultdict(None)
        self.addresses = {}
        self.interfaces = {}
        self.if_buffers = {}
        self._if_listen_threads = {}
        self._conditions = defaultdict(bool)

    def spawn(self, proc_class):
        pid = self.pid.new()
        p = proc_class(pid)
        self.processes[pid] = p
    def kill(self, pid):
        if (p := self.processes[pid]):
            self.pid.remove(pid)
            del self.processes[pid]
    def stop(self, pid):
        if (p := self.processes[pid]):
            p.stop()
            self.pid.remove(pid)

    def socket(self, ifname):
        return Socket(ifname, self)

    def clock(self):
        for proc in self.processes:
            proc.update(0)

    def reserve(self, port, sock):
        if self._ports[port] is None:
            self._ports[port] = sock
    def free(self, port):
        self._ports[port] = None
    def is_open(self, port):
        return self._ports[port] is None

    def check_if(self, ifname):
        if ifname not in self.interfaces.keys():
            raise InterfaceDoesNotExist('interface %s does not exist on this machine' % ifname)

    def _read(self, ifname: str, timeout=5):
        if not self._conditions[ifname]:
            raise InterfaceNotOpen
        return self.interfaces[ifname].recv(self, timeout=timeout)
    def _write(self, ifname: str, data, timeout=1):
        assert type(data) is bytes
        return self.interfaces[ifname].send(self, data, timeout=timeout)

    def hook(self, ifname, interface):
        self.interfaces[ifname] = interface

    def _listen(self, ifname):
        self._conditions[ifname] = True
        self.if_buffers[ifname] = queue.SimpleQueue()
        while self._conditions[ifname]:
            try:
                self.if_buffers[ifname].put((ifname, self._read(ifname)), timeout=1)
            except queue.Full:
                continue
    def listen(self, ifname):
        self._if_listen_threads[ifname] = t = threading.Thread(target=self._listen, args=(ifname,))
        t.start()

    def close(self, ifname):
        if self._conditions[ifname]:
            self._conditions[ifname] = False
            self._if_listen_threads[ifname].join()
            return
        raise InterfaceNotOpen


class Socket:
    def __init__(self, ifname, machine):
        self.ifname = ifname
        self.machine = machine
        self.port = 0

    def send(self, bytes):
        self.machine._write(self.ifname, bytes)
    def recv(self, buffer):
        return self.machine._read(self.ifname)

    def bind(self, port):
        self.port = port
        self.machine.reserve(port, self)
    def unbind(self):
        self.machine.free(self.port)

class Interface:
    def __init__(self, end1: Machine, end2: Machine):
        self.ends = end1, end2
        self.buffers = {end1: queue.Queue(1), end2: queue.Queue(1)}

    def recv(self, end: Machine, timeout=5):
        return self.buffers[end].get(timeout=timeout)

    def send(self, end: Machine, bytes, timeout=1):
        other_end = self.ends[self.ends.index(end)-1]
        try:
            self.buffers[other_end].put(bytes, timeout=timeout)
        except queue.Full as e:
            raise NoEndConnected from e
