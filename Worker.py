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
        self.start()

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr = self.address, self.port
        self.sock.settimeout(50)
        try:
            self.sock.connect(addr)
        except Exception as e:
            print(e)
    
    def read(self):
        try:
            data = self.sock.recv(4096)
            if not validate_data(data):
                return None
            data_arr = pickle.loads(data)
            return data_arr
        except Exception as e:
            print(e)
        
    def write(self, data):
        data_string = pickle.dumps(data)
        self.sock.send(data)
    
    @abstractmethod
    def validate_data(self, data):
        pass
    
    @abstractmethod        
    def start(self):
        pass
            
    def close(self):
        self.sock.close()
        
if __name__ == '__main__':
    w = Worker(IP='127.0.0.1', port=1000)