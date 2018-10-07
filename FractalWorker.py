import threading
from MandelZoom import mandelbrot_set2
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle
import sys
import Worker


class FractalWorker(Worker.Worker):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.start()

    def validate_data(self, data):
        return data
    
    def run(self):
        self.connect()
        done = False;
        
        while not done:
            params = self.read()
            if params:
                results = self.compute(*params)
                print("Got results:", type(results))
                self.write(results)
                done = True


    def compute(self, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)
        
def main(args):
    w = FractalWorker(address='127.0.0.1', port=1000)

if __name__ == '__main__':
    main(sys.argv[1:])