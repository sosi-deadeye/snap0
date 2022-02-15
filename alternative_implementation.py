import time
from struct import Struct

from snap7.client import Client
from snap7.types import Areas


class S7Base:
    def __init__(self, cpu, area):
        self.cpu = cpu
        self.area = area

    def __getitem__(self, key):
        return self.st.unpack(self.cpu.read_area(self.area, 0, key, self.st.size))[0]


class Area:
    def __init__(self, cpu):
        self.byte = Byte(cpu, self.area)
        self.int16 = Int16(cpu, self.area)
        self.int32 = Int32(cpu, self.area)


class Byte(S7Base):
    st = Struct(">B")


class Int16(S7Base):
    st = Struct(">h")


class Int32(S7Base):
    st = Struct(">i")


class PE(Area):
    area = Areas.PE


class PA(Area):
    area = Areas.PA


class MK(Area):
    area = Areas.MK


class CPU(Client):
    def __init__(self, ip, rack, slot):
        super().__init__()
        self.connect(ip, rack, slot)
        self.PE = PE(self)
        self.PA = PA(self)
        self.MK = MK(self)


class Event:
    def __init__(self, cpu):
        self.cpu = cpu
        self.readers = {}

    def add(self, target, address):
        self.readers[(target, address)] = None

    def loop(self):
        while True:
            time.sleep(0.1)

            for target, addr in self.readers:
                area, dtype = target.split(".")
                value_old = self.readers[(target, addr)]
                value = getattr(getattr(self.cpu, area), dtype)[addr]

                if value_old is not None and value != self.readers[(target, addr)]:
                    print(value)

                self.readers[(target, addr)] = value


cpu = CPU("192.168.0.1", 0, 0)
ev = Event(cpu)
ev.add("PE.int16", 0)
ev.loop()
