from worker import WorkerStatus, Worker
import time
from usrtofrac import create_function, gen_with_escape_cond, gen
from fractal import FractalType, mandelbrot_set2
from msg import *
import pickle
import random
import sys
import numpy as np
times = []

predefined_fractals = {
      FractalType.MANDELBROT.value  : mandelbrot_set2} #Expand this as needed when
                                                       #more fractals are introduced
                                                       #into DFR

'''
    Decorator function that wrapper around other functions 
    and returns a time. Mostly used to easily see
     bottlenecks that exist in the fractal computation code
'''
def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print ('func %r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return timed

'''
Fractal worker receives the IP address and port of the client,
It begins to read in the work provided by the Client. It will
run the respective computation based on fractal type passed in
'''
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

        try:
            self.sock.close()
        except:
            pass #Maybe the socket got closed already due to an
                 #Invocation to close()

    ''' Compute will using the parameters provided to it from the Client to compute the respective
        Fractal based on the expression (expr) that was passed in. If the expr is in the 
        predefined_fractals dictionary it will pass the input to it's respective computation method
        otherwise it assumes it a custom equation
    '''
    @timeit
    def compute(self, expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        if expr in predefined_fractals: #Standard Hard Coded Fractals
            fractal_compute_function = predefined_fractals[expr]
            data = fractal_compute_function(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end, data=None)
            return data
        else:
            r1 = np.linspace(ymin, ymax, end - start, dtype=np.float64)
            r2 = np.linspace(xmin, xmax, img_width, dtype=np.float64)
            n3 = np.ndarray((end - start, img_width))
            fractal_compute_function = gen(gen_with_escape_cond(create_function(expr), max_itr))
            fractal_compute_function(r1, r2, max_itr, n3)
            return n3

    def close(self, status: WorkerStatus, msg=""):
        print("{} closed with status {}:".format(self.__str__(), status.value),  msg)
        self.sock.close()

        #Set to done to get out of while loop
        self.set_status(WorkerStatus.DONE)

    ## Due to the Worker abtract methods, there are a lot
    ## of methods that fractalworker does not need
    ## There may be a cleaner way to do this, but it
    ## works so far

    def on_read_clse(self):
        self.close(WorkerStatus.DONE, msg="Received closed message")

    def on_read_conn(self):
        self.set_status(WorkerStatus.AVAILABLE)

    def on_read_fail(self):
        pass

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

if __name__ == '__main__':

    #Creates a number of workers from one computer if provided a
    #third cmd arg
    if len(sys.argv) == 4:
        num = int(sys.argv[3])
        for i in range(num):
            worker = FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
            worker.start()

    #Otherwise just create one
    else:
        fw = FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
        fw.start()
