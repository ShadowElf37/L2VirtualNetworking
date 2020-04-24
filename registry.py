from random import randint


class _REGISTRY:
    def __init__(self):
        self.REGISTER = set()

    def _generate(self):
        return 0

    def register(self, address):
        if address not in self.REGISTER:
            self.REGISTER.add(address)
            return 0
        return 1

    def new(self):
        while self.register(a := self._generate()):
            continue
        return a

    def remove(self, item):
        self.REGISTER.remove(item)


class MACREGISTRY(_REGISTRY):
    def _generate(self):
        return randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)

class PIDREGISTRY(_REGISTRY):
    def _generate(self):
        return randint(0, 65535)
