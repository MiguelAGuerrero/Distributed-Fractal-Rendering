import threading
from MandelZoom import mandelbrot
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
from abc import ABC, abstractmethod
from enum import Enum
import sys

class WorkerState(Enum):
    FAILED = -1
    WORKING = 1
    AVAILABLE = 0
    READY = 2
    DONE = 3

class Worker(ABC, threading.Thread):
    def __init__(self, address, port):
        super().__init__()
        self.address = address
        self.port = port
        self.state = WorkerState.AVAILABLE

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr = self.address, self.port
        self.sock.settimeout(1)
        try:
            self.sock.connect(addr)
        except Exception as e:
            print(e)
    
    def read(self):
        data = []
        try:
            while True:
                packet = self.sock.recv(1024)
                if not packet:
                    break
                data.append(packet)
        except timeout as te:
            pass
        except Exception as e:
            self.close(WorkerState.FAILED, msg=e)

        if not data:
            return None

        data_arr = pickle.loads(b''.join(data))
        print(self.__class__.__name__, "Unloaded:", data_arr)

        return data_arr

    def write(self, data):
        try:
            data_string = pickle.dumps(data)
            self.sock.sendall(data_string)
        except:
            self.close(WorkerState.FAILED, "write error")

    @abstractmethod
    def validate_data(self, data):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def close(self, status: WorkerState, msg=None):
        pass

if __name__ == '__main__':
    w = Worker(IP='127.0.0.1', port=1000)