import threading
from MandelZoom import mandelbrot
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
from abc import ABC, abstractmethod


class Worker(ABC, threading.Thread):
    def __init__(self, address, port):
        super().__init__()
        self.address = address
        self.port = port

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
        except Exception as e:
            pass

        if not data:
            return []

        data_arr = pickle.loads(b''.join(data))
        print(self.__class__.__name__, "Unloaded:", data_arr)

        return data_arr

    def write(self, data):
        data_string = pickle.dumps(data)
        self.sock.send(data_string)

    @abstractmethod
    def validate_data(self, data):
        pass

    @abstractmethod
    def run(self):
        pass

    def close(self):
        self.sock.close()
        
if __name__ == '__main__':
    w = Worker(IP='127.0.0.1', port=1000)