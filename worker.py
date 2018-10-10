import threading
from MandelZoom import mandelbrot
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
from abc import ABC, abstractmethod
from enum import Enum
import sys
from msg import StaticMessage, MessageType, static_msgs


class WorkerStatus(Enum):
    FAILED = -1
    WORKING = 1
    AVAILABLE = 0
    WORK_READY = 2
    DONE = 3
    UNAVAILABLE = 4

class Worker(ABC, threading.Thread):
    def __init__(self, address, port, id=None):
        super().__init__()
        self.address = address
        self.port = port
        self.status = WorkerStatus.AVAILABLE
        self.read_switch = {
            MessageType.CONN: self.on_read_conn
        ,   MessageType.CLSE: self.on_read_clse
        ,   MessageType.RSLT: self.on_read_rslt
        ,   MessageType.RJCT: self.on_read_rjct
        ,   MessageType.WORK: self.on_read_work
        ,   MessageType.AVAL: self.on_read_aval}

        if id:
            self.id = id

    def __str__(self):
        return self.__class__.__name__ + str(id)

    def set_status(self, status: WorkerStatus):
        self.status = status

    def get_status(self):
        return self.status

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr = self.address, self.port
        self.sock.settimeout(1)
        self.sock.connect(addr)
        self.sock.sendall(StaticMessage(MessageType.CONN).as_bytes())

    def read(self):
        data = []
        try:
            type = (self.sock.recv(4)).decode("ascii")
            if type in static_msgs:
                return self.read_switch[type]()
            else: #These are dynamic messages
                data_len = self.sock.recv(4)
                data = self.sock.recv(data_len)
                return self.read_switch[type](data)
        except timeout as te:
            pass
        except WindowsError as we:
            self.close(WorkerStatus.FAILED, msg=we)
        except Exception as e:
            self.close(WorkerStatus.FAILED, msg=e)

        if not data:
            return None

    def write(self, data):
        try:
            self.sock.sendall(data)
        except:
            self.close(WorkerStatus.FAILED, "write error")

    @abstractmethod
    def on_read_clse(self):
        pass

    @abstractmethod
    def on_read_acpt(self):
        pass

    @abstractmethod
    def on_read_rjct(self):
        pass

    @abstractmethod
    def on_read_conn(self):
        pass

    @abstractmethod
    def on_read_aval(self):
        pass

    @abstractmethod
    def on_read_work(self, data):
        pass

    @abstractmethod
    def on_read_rslt(self, data):
        pass

    @abstractmethod
    def validate_data(self, data):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def close(self, status: WorkerStatus, msg=None):
        pass

if __name__ == '__main__':
    w = Worker(IP='127.0.0.1', port=1000)