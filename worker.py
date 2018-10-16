import threading
from MandelZoom import mandelbrot
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
from abc import ABC, abstractmethod
from enum import Enum
import sys
from msg import StaticMessage, MessageType, static_msgs
import struct


class WorkerStatus(Enum):
    FAILED = -1
    WORKING = 1
    AVAILABLE = 0
    WORK_READY = 2
    DONE = 3
    UNAVAILABLE = 4

class Worker(ABC, threading.Thread):
    def __init__(self, address, port, conn_id=None):
        super().__init__()
        self.address = address
        self.port = port
        self.status = WorkerStatus.AVAILABLE
        self.read_switch = {
            MessageType.CONN.value: self.on_read_conn
        ,   MessageType.CLSE.value: self.on_read_clse
        ,   MessageType.RSLT.value: self.on_read_rslt
        ,   MessageType.RJCT.value: self.on_read_rjct
        ,   MessageType.WORK.value: self.on_read_work
        ,   MessageType.AVAL.value: self.on_read_aval
        ,   MessageType.FAIL.value: self.on_read_fail}
        self.conn_id = conn_id

    def __str__(self):
        return self.__class__.__name__ + str(self.conn_id)

    def set_status(self, status: WorkerStatus):
        self.status = status

    def get_status(self):
        return self.status

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr = self.address, self.port
        self.sock.settimeout(1)
        self.sock.connect(addr)
        #self.sock.sendall(StaticMessage(MessageType.CONN).as_bytes())


    #TODO: Deal with ConnectionResetError
    def read(self):
        data = []
        try:
            type = (self.sock.recv(4)).decode("ascii")
            if not type:
                pass
            elif type in static_msgs:
                return self.read_switch[type]()
            else: #These are dynamic messages
                data_len = int.from_bytes(self.sock.recv(4), sys.byteorder)
                #3print("Data length on read:", data_len)
                done_reading = False

                bytes_read = 0
                data_buf = bytearray()
                packet_buf = bytearray(data_len)
                while not done_reading:
                    read = self.sock.recv_into(packet_buf)
                    bytes_read += read
                    #print('     bytes read', bytes_read)
                    data_buf.extend(packet_buf[:read])
                    if bytes_read == data_len:
                        done_reading = True

                return self.read_switch[type](bytes(data_buf))

        except timeout as te:
            pass
        except ConnectionResetError as cre:
            if self.get_status() is WorkerStatus.WORKING:
                self.close(WorkerStatus.FAILED, "connection closed while working")
            elif self.get_status() is WorkerStatus.AVAILABLE:
                self.close(WorkerStatus.DONE, "connection closed")
        except:
            self.close(WorkerStatus.DONE, "unexpected connection error occured")
        if not data:
            return None

    #TODO: deal with ConnectionResetError
    def write(self, data):
        try:
            self.sock.sendall(data)
        except ConnectionResetError as cre:
            self.close(WorkerStatus.FAILED, "connection closed")
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

    def on_read_fail(self):
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