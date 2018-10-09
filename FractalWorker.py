from MandelZoom import mandelbrot_set2
import sys
from Worker import WorkerStatus, Worker
import time
import fractal
import socket
import threading


times = []
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

        done = False
        while not done:
            params = self.read()
            if self.get_status() is not WorkerStatus.FAILED:
                if params:
                    results = self.compute(*params)
                    self.write(results)
                    done = True
            else:
                pass

    def compute(self, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        return fractal.generate_rows("julia", start, end, -1.037 + 0.17j, size=(img_width, img_height))
        #return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

    def close(self, status: WorkerStatus, msg=""):
        print("Worker closed:", status, msg)
        self.sock.close()
        sys.exit(0)

if __name__ == '__main__':
    FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
