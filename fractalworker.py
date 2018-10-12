from worker import WorkerStatus, Worker
import time
from usrtofrac import create_function, gen_with_escape_cond, gen
from fractal import FractalType, mandelbrot_set
from MandelZoom import mandelbrot_set2
from msg import *
import pickle
import random
import sys

times = []

predefined_fractals = {
      FractalType.MANDELBROT.value  : mandelbrot_set2
    , FractalType.JULIA.value     : None
}

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print ('func %r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return timed

class FractalWorker(Worker):
    def __init__(self, address, port, conn_id=None):
        super().__init__(address, port, conn_id=conn_id)

    def validate_data(self, data):
        return data

    def run(self):
        try:
            self.connect()
        except:
            print("Could not connect to client at {}:{}".format(self.address, self.port))
            return

        while self.get_status() is not WorkerStatus.DONE:
            self.read()

        self.close()

    @timeit
    def compute(self, expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        r1 = np.linspace(ymin, ymax, end - start, dtype=np.float64)
        r2 = np.linspace(xmin, xmax, img_width, dtype=np.float64)
        n3 = np.ndarray((end - start, img_width), dtype=int)
        print(n3.shape)
        if expr in predefined_fractals: #Standard Hard Coded Fractals
            fractal_compute_function = predefined_fractals[expr]
        else:
            fractal_compute_function = gen(gen_with_escape_cond(create_function(expr), max_itr))

        if True:
            data = fractal_compute_function(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end, data=None)
            return data
        else:
            fractal_compute_function(r1, r2, max_itr, n3)

        return n3

        #return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

    def close(self, status: WorkerStatus, msg=""):
        print("Worker closed:", status, msg)
        self.sock.close()

    def on_read_clse(self):
        self.close(WorkerStatus.DONE, msg="Received closed message")

    def on_read_acpt(self):
        pass

    def on_read_rjct(self):
        pass

    def on_read_conn(self):
        pass

    def on_read_fail(self):
        pass

    def on_read_aval(self):
        if self.get_status() is WorkerStatus.AVAILABLE:
            self.write(StaticMessage(MessageType.ACPT).as_bytes())
        else:
            self.write(StaticMessage(MessageType.RJCT).as_bytes())

    def on_read_work(self, data):
            self.set_status(WorkerStatus.WORKING)
            args = pickle.loads(data)
            results = self.compute(*args)
            if results is None:
                self.write(StaticMessage(MessageType.FAIL).as_bytes())
            else:
                self.write(RSLTMessage(results, args[-2], args[-1]).as_bytes())
            self.set_status(WorkerStatus.AVAILABLE)

    def on_read_rslt(self, data):
        pass

class BadWorker(FractalWorker):
    def __init__(self, address, port, conn_id=None, force_terminate=False):
        super().__init__(address, port, conn_id=None)
        self.rand = random.Random()
        self.force_terminate = force_terminate

    def compute(self, expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        terminate = True if self.rand.randint(1, 5) == 1 else False
        if self.force_terminate or terminate:
            return None
        else:
            return super().compute(expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        num = int(sys.argv[3])
        for i in range(num):
            worker = BadWorker(address=sys.argv[1], port=int(sys.argv[2]))
            worker.start()
    else:
        bw = BadWorker(address=sys.argv[1], port=int(sys.argv[2]), force_terminate=True)
        bw.start()
        fw = FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
        fw.start()
