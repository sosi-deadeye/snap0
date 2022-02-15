from struct import Struct

from snap7.client import Client
from snap7.types import Areas


class G:
    def __init__(self, plc: Client, area, fmt, get_bit=False):
        self.plc = plc
        self.area = area
        self.get_bit = get_bit
        self.fmt = Struct(fmt)

    def __getitem__(self, addr):
        if self.get_bit and isinstance(addr, tuple):
            return bool(
                self.plc.read_area(self.area, 0, addr[0], self.fmt.size)[0]
                & (1 << addr[1])
            )

        elif isinstance(addr, int):
            return self.fmt.unpack(
                self.plc.read_area(self.area, 0, addr, self.fmt.size)
            )[0]

    def __setitem__(self, addr, value):
        if isinstance(addr, int):
            self.plc.write_area(self.area, 0, addr, self.fmt.pack(value))

    def __call__(self, addr, value=None):
        if value is not None:
            self[addr] = value
        else:
            return self[addr]


class Delegator:
    def __init__(self, plc, area):
        self.plc = plc
        self.area = area

    @property
    def bit(self):
        return G(self.plc, self.area, ">b", get_bit=True)

    @property
    def byte(self):
        return G(self.plc, self.area, ">b")

    @property
    def ubyte(self):
        return G(self.plc, self.area, ">B")

    @property
    def int16(self):
        return G(self.plc, self.area, ">h")

    @property
    def int32(self):
        return G(self.plc, self.area, ">i")

    @property
    def float32(self):
        return G(self.plc, self.area, ">f")

    @property
    def float64(self):
        return G(self.plc, self.area, ">d")


class Area:
    def __init__(self, name):
        self.area = Areas[name]

    def __get__(self, obj, obj_type):
        return Delegator(obj, self.area)


class PLC(Client):
    PE = Area(Areas.PE.name)
    PA = Area(Areas.PA.name)
    MK = Area(Areas.MK.name)

    def __init__(self, ip):
        super().__init__()
        self.connect(ip, 0, 0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_obj, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    with PLC("192.168.0.1") as plc:
        print(plc.PE.byte(0))
        print(plc.PA.int16(0, 0))
        print(plc.PA.int16(0))
        print(plc.PA.int16(0, 16000))
        print(plc.PA.int16(0))
        print(plc.PE.bit[10, 1])
        print(plc.MK.float64[10])
