from MandelZoom import mandelbrot_set2
import sys
import Worker
import time
import fractal

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
                self.write(results)
                done = True

    def compute(self, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        return fractal.generate_rows("julia", start, end, -1.037 + 0.17j, size=(img_width, img_height))
        #return mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

if __name__ == '__main__':
    FractalWorker(address=sys.argv[1], port=int(sys.argv[2]))
