from abc import abstractmethod
from enum import Enum, auto
import pickle
import sys

from abc import ABC

class MessageType(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self

    WORK = auto()
    CONN = auto()
    CLSE = auto()
    AVAL = auto()
    ACPT = auto()
    RJCT = auto()
    RSLT = auto()
    FAIL = auto()


static_msgs = [msg.value for msg in [MessageType.CONN, MessageType.CLSE, MessageType.AVAL, MessageType.ACPT, MessageType.RJCT, MessageType.FAIL]]
dynamic_msgs = [msg.value for msg in {MessageType.WORK, MessageType.RSLT}]

def msg(type, data=None):
    if type in static_msgs:
        return type.value
    elif type is MessageType.WORK:
        return
    elif type is MessageType.RSLT:
        return
    else:
        return b""


class Message(ABC):
    def __init__(self, type, data):
        self.type = type
        self.data = data

    @abstractmethod
    def as_bytes(self):
        pass

class StaticMessage(Message):
    def __init__(self, type):
        self.type = type;

    def as_bytes(self):
        return self.type.value.encode("ascii")

class WORKMessage(Message):
    def __init__(self, data):
        super().__init__(MessageType.WORK, data)

    def as_bytes(self):
        payload = pickle.dumps(self.data)
        return b"".join([self.type.value.encode("ascii"), len(payload).to_bytes(4, sys.byteorder), payload])

class RSLTMessage(Message):
    def __init__(self, data, section_start, section_end):
        super().__init__(MessageType.RSLT, data)
        self.section_start = section_start
        self.section_end = section_end

    def as_bytes(self):
        payload = self.data.tostring()
        rows = self.data.shape[0]
        columns = self.data.shape[1]

        return b"".join([self.type.value.encode("ascii"),
                         (len(payload) + 16).to_bytes(4, sys.byteorder),
                         payload,
                         rows.to_bytes(4, sys.byteorder),
                         columns.to_bytes(4, sys.byteorder),
                         self.section_start.to_bytes(4, sys.byteorder),
                         self.section_end.to_bytes(4, sys.byteorder)])