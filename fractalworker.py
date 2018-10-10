from MandelZoom import mandelbrot_set2
import sys
from worker import WorkerStatus, Worker
import time
import fractal
import usrtofrac
import socket
import threading
import numpy as np
from usrtofrac import create_function, gen_with_escape_cond, gen
from fractal import FractalType, mandelbrot_set
from msg import *
import pickle

times = []

predefined_fractals = {
      FractalType.MANDELBROT  : fractal.mandelbrot_set
    , FractalType.JULIA     : None
}

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print ('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return times.append(timed)

class FractalWorker(Worker):
    def __init__(self, address, port, id=None):
        super().__init__(address, port, id=id)
        self.start()

    def validate_data(self, data):
        return data

    def run(self):
        try:
            self.connect()
        except:
            print("Could not connect to client at {}:{}".format(self.address, self.port))
            return

        while not self.get_status() is WorkerStatus.DONE:
            self.read()

    def compute(self, expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        r1 = np.linspace(xmin, xmax, img_width)
        r2 = np.linspace(ymin, ymax, img_height)
        n3 = np.ndarray((img_height, img_width))
        if expr in predefined_fractals: #Standard Hard Coded Fractals
            fractal_compute_function = predefined_fractals[expr]
        else:
            fractal_compute_function = gen(gen_with_escape_cond(create_function(expr), max_itr))

        try:
            fractal_compute_function(r1, r2, max_itr, n3)
            return n3
        except:
            pass #Send failure message

        #return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

    def close(self, status: WorkerStatus, msg=""):
        print("Worker closed:", status, msg)
        self.sock.close()
        sys.exit(0)

    def on_read_clse(self):
        self.close(WorkerStatus.DONE, msg="Received closed message")

    def on_read_acpt(self):
        pass

    def on_read_rjct(self):
        pass

    def on_read_conn(self):
        pass

    def on_read_aval(self):
        if self.get_status() is WorkerStatus.AVAILABLE:
            self.write(StaticMessage(MessageType.ACPT).as_bytes())
        else:
            self.write(StaticMessage(MessageType.RJCT).as_bytes())

    def on_read_work(self, data):
        try:
            self.set_status(WorkerStatus.WORKING)
            args = pickle.loads(data)
            results = self.compute(*args)
            self.write(RSLTMessage(data).as_bytes())
            self.set_status(WorkerStatus.AVAILABLE)
        except:
            self.set_status(WorkerStatus.FAILED)
            print(self, "failed in computation")

    def on_read_rslt(self, data):
        pass

if __name__ == '__main__':
    FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
