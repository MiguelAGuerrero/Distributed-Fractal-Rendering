import threading
import socket
import sys
from ClientWorker import ClientWorker
from MandelZoom import mandelbrot_image
import numpy
from mltcanvas import MLTCanvas
from Worker import WorkerStatus

def distribute_mandelbrot_work(i, avail_workers, width, height, maxiter):
    vertical_partition = height // avail_workers
    params = [-2, 1,  # xmin, xmax
              -1, 1,  # ymin, ymax
    width, height, maxiter, i * vertical_partition,
              (i + 1) * vertical_partition]  # SPLIT WORK: xmin, xmax, ymin, ymax
    return (0, i * vertical_partition, width, (i + 1) * vertical_partition), params

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self._make_server_socket()
        self.manager = WorkManager(self)
        self.manager.start()
        self.img_width = 1000;
        self.img_height = 3 * self.img_width // 4;
        self.maxiter = 256
        self.canvas = MLTCanvas(self.img_width, self.img_height)
        self.params = self.img_width, self.img_height, self.maxiter

    def _make_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(16)


    def redistribute_work(self, failed_workers, avail, f, *args):
        failed_sections = len(failed_workers)
        avail_help = len(avail) + 1 #Plus one to consider the client as a worker

        for i, worker in enumerate(failed_workers):
            sect, params = worker.get_work_submission()
            worker.submit_work(*sect, params)

    def await_worker_status(self, workers):
        task_complete = False

        while not task_complete:
            failed = [worker for worker in workers if worker.get_status() is WorkerStatus.FAILED]
            working = [worker for worker in workers if worker.get_status() is WorkerStatus.WORKING]
            finished = [worker for worker in workers if worker.get_status() is WorkerStatus.WORK_READY]

            if failed:
                return WorkerStatus.FAILED

            elif finished and not working:
                task_complete = True

        return WorkerStatus.WORK_READY

    def run(self):
        avail = self.manager.get_available_workers()
        if avail:
            self.distribute_work(avail, distribute_mandelbrot_work, self.img_width, self.img_height, self.maxiter)
            status = self.await_worker_status(avail)
            if status is WorkerStatus.WORK_READY:
                if self.canvas.can_render():
                    print("Displaying")
                    self.canvas.render()
                else:
                    print("Insufficient work")
                    #Loop back and ask for more work to be done
            else:
                print()
        else:
            pass
            #render your damn self

class WorkManager(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.workers = {}
        self.ids = 0;
        self.socket = client.socket
        self.client = client

    def accept_connection(self):
        self.ids = self.ids + 1
        conn, addr = self.socket.accept()
        worker = ClientWorker(self.client, conn)
        print('Connected to Worker: ', worker)
        self._add_connection(self.ids,  worker)
        return worker

    def distribute_work(self, workers, f, *args):
        for i, worker in enumerate(workers):
            sect, params = f(i, len(workers), *args)
            worker.submit_work(*sect, params)
            print("Client REQ", worker, sect, params)

        return Task(workers, f, *args)

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

    def failed(self):
        for worker in self.workers:
            if worker.get_status() is WorkerStatus.FAILED:
                return True
        return False

    def in_progress(self):
        for worker in self.workers:
            if worker.get_status() is WorkerStatus.WORKING:
                return True

    def get_task_status(self):
        if self.failed():
            return WorkerStatus.FAILED

    def wait(self):
        while True:
            pass

if __name__ == "__main__":
    main(sys.argv[1:])