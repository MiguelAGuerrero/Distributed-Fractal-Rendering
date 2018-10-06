import threading
from MandelZoom import mandelbrot_set2
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
import sys
    
class FractalWorker(Worker):
    def __init__(self, address, port):
        super().__init__(address, port)
    
    def validate_data(self, data):
        return data
    
    def start(self):
        self.connect()
        done = False;
        
        while not done:
            data = self.read()
            if data:
                results = self.compute(*data)
                self.write(results)
            
    def compute(self, xmin, xmax, ymin, ymax, img_width, img_height, max_itr):
        return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr)
        
def main(args):
    w = FractalWorker(address='127.0.0.1', port=1000)

if __name__ == '__main__':
    main(sys.argv[1:])