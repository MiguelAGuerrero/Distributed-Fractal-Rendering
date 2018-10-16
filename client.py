import sys
from numpcanvas import NUMPCanvas

from worker import WorkerStatus
from fractal import FractalType
from fractalworker import FractalWorker
from fractalcanvas import FractalCanvas
from workmanager import WorkManager
import threading

#expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end
def partition_horizontally(i, avail_workers, xmin, xmax, ymin, ymax, width, height, maxiter, start, end):
    space_interval = height / avail_workers

    #avail_workers may not evenly divide into the height of the image
    #round the values for discrete values
    args = [xmin, xmax,  # xmin, xmax
              ymin, ymax,  # ymin, ymax
              width, height,
              maxiter, round(start + i * space_interval), round(start + (i+1) * space_interval)]  # SPLIT WORK: xmin, xmax, ymin, ymax

    return args

class Client(threading.Thread):
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.manager = WorkManager(self)
        self.img_width = 100;
        self.img_height = 3 * self.img_width // 4;
        self.maxiter = 256
        self.canvas = NUMPCanvas(self.img_width, self.img_height)
        self.fractal = FractalType.MANDELBROT
        self.personal_worker = FractalWorker(self.address, self.port)
        self.xmin = -2
        self.xmax = 1
        self.ymin = -1
        self.ymax = 1

    def set_canvas(self, canvas: FractalCanvas):
        self.canvas = canvas

    def smarter_task_handling(self):
        work_done = False
        # Naive approach: Just compute the fractal over and over again until a complete image is formed
        # A better approach would be to subdivided the missing sections among available workers
        # instead of computing the same results over again
        while not work_done:
            args = [self.xmin, self.xmax, self.ymin, self.ymax, self.img_width, self.img_height, self.maxiter, 0, self.img_height]
            task = self.manager.distribute_work(partition_horizontally, self.get_fractal_expr(), *args)
            task.wait()
            print("Done waiting for task")
            status = task.get_task_status()
            if status is WorkerStatus.FAILED:
                if self.manager.workers_available():
                    print("Tasked failed: redistibuting work")
                else:
                    print("Task failed: no more workers. Client now rendering...")
                    self.self_compute_fractal()
                    work_done = True
            else:
                work_done = True

    def naive_task_handling(self):
        work_done = False
        # Naive approach: Just compute the fractal over and over again until a complete image is formed
        # A better approach would be to subdivided the missing sections among available workers
        # instead of computing the same results over again
        while not work_done:
            args = [self.xmin, self.xmax, self.ymin, self.ymax, self.img_width, self.img_height, self.maxiter, 0, self.img_height]
            task, client_args = self.manager.distribute_work(partition_horizontally, self.get_fractal_expr(), *args)
            results = self.personal_worker.compute(*client_args)
            self.canvas.put_pixels(results, 0, 0)
            task.wait()
            status = task.get_task_status()
            if status is WorkerStatus.FAILED:
                if self.manager.workers_available():
                    print("Tasked failed: redistibuting work")
                else:
                    print("Task failed: no more workers. Client now rendering...")
                    self.self_compute_fractal()
                    work_done = True
            else:
                work_done = True

    def run(self):
        if self.manager.workers_available():
            self.naive_task_handling()
        else:
            print("No workers available: client rendering...")
            self.self_compute_fractal()

        print("Computation done. Now rendering...")
        self.canvas.render()

    def self_compute_fractal(self):
        start_row, start_col = 0, 0
        results = self.personal_worker.compute(self.get_fractal_expr(), *[self.xmin, self.xmax, self.ymin, self.ymax,
                                                       self.img_width, self.img_height,
                                                       self.maxiter, 0, self.img_height])

        self.canvas.put_pixels(results, start_row, start_col)

    def get_fractal_expr(self):
        expr = self.fractal
        if type(self.fractal) is FractalType:
            expr = self.fractal.value
        return expr

def main(args):
    port = int(args[1])
    c = Client(args[0], port)
    input("press any key to continue")
    c.run()

if __name__ == "__main__":
    main(sys.argv[1:])