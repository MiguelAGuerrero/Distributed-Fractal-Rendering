import threading
import socket
import sys
from ClientWorker import ClientWorker
from MandelZoom import mandelbrot_image
import numpy

def distribute_mandelbrot_work(i, avail_workers, width, height, maxiter):
    vertical_partition = height // avail_workers
    params = [-2, 1,  # xmin, xmax
              -1, 1,  # ymin, ymax
    width, height, maxiter, i * vertical_partition,
              (i + 1) * vertical_partition]  # SPLIT WORK: xmin, xmax, ymin, ymax
    return params

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self._make_server_socket()
        self.manager = ConnectionManager(self)
        self.manager.start()
        self.data = None
        self.img_width = 1000;
        self.img_height = 3 * self.img_width // 4;
        self.maxiter = 256

    def _make_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(16)

    #Implement
    def receive(self, data):
        print()
        if self.data is None:
            self.data = data
        else:
            self.data = numpy.concatenate((self.data, data), axis=0)

    def can_render_fractal_img(self):
        print("Dimensions: ", len(self.data), len(self.data[0]))
        if self.data is None:
            return False
        return (len(self.data) * len(self.data[0]) == self.img_width * self.img_height) or len(self.data) == self.img_width


    def display(self):
        mandelbrot_image(self.data, xmin=-2, xmax=1, ymin=-1, ymax=1)


    def get_AvailableWorkers(self):
        return self.manager.get_workers()



    def distribute_work(self,workers, f,*args):
        for i, conn_id in enumerate(self.manager.get_workers()):
            params = f(i, len(workers), *args)
            conn, worker = workers[conn_id]
            print(params)
            worker.submit_work(params)

    def wait_for_results(self):
        workers = self.manager.get_workers()

        def workers_are_done():
            for conn_id in workers:
                conn, worker = workers[conn_id]
                if worker.get_status():
                    return False
            return True

        while not workers_are_done():
            pass



    def render(self):
        avail = self.get_AvailableWorkers()
        if avail:
            self.distribute_work(avail, distribute_mandelbrot_work, self.img_width, self.img_height, self.maxiter)
            self.wait_for_results()
            if self.can_render_fractal_img():
                print("DiSPLAYINg")
                self.display()
            else:
                print("DID NOT MAKE IT")
        else:
            pass #render your damn self

class ConnectionManager(threading.Thread):
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
        self._add_connection(self.ids, (conn, worker))
        return conn, worker

    def _add_connection(self, conn_id, val):
        self.workers[conn_id] = val
        
    def _remove_connection(self, conn_id):
        return self.workers.pop(conn_id)

    def run(self):
        done = False
        while not done:
            conn_id, worker = self.accept_connection()

    def get_workers(self):
        return self.workers

def main(args):
    port = int(args[1])
    c = Client(args[0], port)
    input("press any key to continue")
    c.render()


if __name__ == "__main__":
    main(sys.argv[1:])