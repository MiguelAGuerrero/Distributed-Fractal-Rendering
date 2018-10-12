import threading
import socket
import sys
from clientworker import ClientWorker
from mltcanvas import MLTCanvas
from worker import WorkerStatus
from fractal import FractalType
from fractalworker import FractalWorker

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

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.manager = WorkManager(self)
        self.img_width = 1000;
        self.img_height = 3 * self.img_width // 4;
        self.maxiter = 256
        self.canvas = MLTCanvas(self.img_width, self.img_height)
        self.params = self.img_width, self.img_height, self.maxiter
        self.fractal = FractalType.MANDELBROT
        self.personal_worker = FractalWorker(self.address, self.port)
        self.xmin = -2
        self.xmax = 1
        self.ymin = -1.1
        self.ymax = 1.5
        self.maxiter = 256


    def naive_task_manage(self):
        work_done = False
        # Naive approach: Just compute the fractal over and over again until a complete image is formed
        # A better approach would be to subdivided the missing sections among available workers
        # instead of computing the same results over again
        while not work_done:
            task = self.manager.distribute_work(partition_horizontally, self.get_fractal_expr(),
                                                *[self.xmin, self.xmax, self.ymin, self.ymax,
                                                  self.img_width, self.img_height, self.maxiter, 0, self.img_height])
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

    def run(self):
        if self.manager.workers_available():
            self.naive_task_manage()
        else:
            print("No workers available: client rendering...")
            self.self_compute_fractal()

        print("Displaying")
        self.canvas.render()

    def self_compute_fractal(self, expr):
        results = self.personal_worker.compute(self.get_fractal_expr(), *[self.xmin, self.xmax, self.ymin, self.ymax,
                                                       self.img_width, self.img_height,
                                                       self.maxiter, 0, self.img_height])
        self.canvas.put_pixels(results, 0, 0)

    def get_fractal_expr(self):
        expr = self.fractal
        if type(self.fractal) is FractalType:
            expr = self.fractal.value
        return expr

class WorkManager(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.workers = {}
        self.ids = 0;
        self.client = client
        self._make_server_socket()
        self.start()

    def _make_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.client.address, self.client.port))
        self.socket.listen(16)

    def accept_connection(self):
        self.ids = self.ids + 1
        conn, addr = self.socket.accept()
        worker = ClientWorker(self.client, conn, conn_id=self.ids)
        print('Connected to Worker: ', worker)
        self._add_connection(self.ids,  worker)
        return worker

    def workers_available(self):
        for conn_id in self.workers:
            if self.workers[conn_id].get_status() is WorkerStatus.AVAILABLE:
                return True
        return False

    def distribute_work(self, distribution_func, expr, *args):
        avail = self.get_available_workers()
        for i, worker in enumerate(avail):
            distributed_args = [expr, *distribution_func(i, len(avail), *args)]

            worker.submit_work(distributed_args)

            print("Client REQ:", worker, distributed_args)

        return Task(avail, distribution_func, distributed_args)

    def get_available_workers(self):
        return [worker for worker in self.get_workers() if worker.get_status() == WorkerStatus.AVAILABLE]

    def _add_connection(self, conn_id, worker):
        self.workers[conn_id] = worker
        
    def _remove_connection(self, conn_id):
        del self.workers[conn_id]

    def run(self):
        done = False
        while not done:
            worker = self.accept_connection()

    def purge(self):
        for id in self.workers:
            worker = self.workers[id]
            worker.close(WorkerStatus.DONE, "Client forced disconnection")
            del self.workers[id]

    def get_workers(self):
        print(self.workers.values())
        return self.workers.values()

    def redistribute_work(self, task):
        pass

def main(args):
    port = int(args[1])
    c = Client(args[0], port)
    input("press any key to continue")
    c.run()

class Task:
    def __init__(self, workers, function, args):
        self.workers = workers
        self.function = function
        self.args = args

    def _get_workers_of_status(self, status):
        return [worker for worker in self.workers if worker.get_status() is status]

    def _worker_of_status_exists(self, status):
        return any((worker for worker in self.workers if worker.get_status() is status))

    def failed(self):
        return self._worker_of_status_exists(WorkerStatus.FAILED)

    def in_progress(self):
        return self._worker_of_status_exists(WorkerStatus.WORKING)

    def get_failed_workers(self):
        return self._get_workers_of_status(WorkerStatus.FAILED)

    def get_workers_in_progress(self):
        return self._get_workers_of_status(WorkerStatus.WORKING)

    def get_task_status(self):
        if self.get_failed_workers():
            return WorkerStatus.FAILED
        elif self.get_workers_in_progress():
            return WorkerStatus.WORKING
        else:
            return WorkerStatus.WORK_READY

    def wait(self):
        while self.in_progress():
            continue


if __name__ == "__main__":
    main(sys.argv[1:])