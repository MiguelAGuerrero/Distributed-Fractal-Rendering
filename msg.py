from abc import ABC, abstractmethod
import sys
from enum import Enum, auto
import pickle

class MessageType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.encode("ascii")

    WORK = auto()
    CONN = auto()
    CLSE = auto()
    AVAL = auto()
    ACPT = auto()
    RJCT = auto()
    RSLT = auto()

static_msgs = set([MessageType.CONN, MessageType.CLSE, MessageType.AVAL, MessageType.ACPT, MessageType.RJCT])
dynamic_msgs = set([MessageType.WORK, MessageType.RSLT])

def msg(type, data=None):
    if type in static_msgs:
        return type.value
    elif type in dynamic_msgs:
        return
    else:
        return b""

def interp(bytes):
    type = print(bytes[4:])

print(msg(MessageType.CONN, [1, 2, 3]))