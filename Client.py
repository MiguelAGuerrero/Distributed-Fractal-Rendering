import threading
import socket
import sys
from ClientWorker import ClientWorker
from MandelZoom import mandelbrot_image
import numpy

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
        self.time_log = []
    def _make_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(16)

    #Implement
    def receive(self, data):
        if self.data is None:
            self.data = data
        else:
            self.data = numpy.concatenate((self.data, data), axis=0)

    def can_render_fractal_img(self):
        if self.data is None:
            return False
        return len(self.data) == self.img_width * self.img_height or len(self.data) == self.img_width


    def display(self):
        mandelbrot_image(self.data, xmin=-2, xmax=1, ymin=-1, ymax=1)

    def render(self):
        workers = self.manager.get_workers()
        avail_workers = len(workers)
        print(avail_workers)
        if avail_workers:
            for i, conn_id in enumerate(workers):
                vertical_partition = self.img_height // avail_workers
                params = [-2, 1, #xmin, xmax
                          -1, 1, #ymin, ymax
                          self.img_width, self.img_height, self.maxiter, i * vertical_partition, (i + 1) * vertical_partition] #SPLIT WORK: xmin, xmax, ymin, ymax
                conn, worker = workers[conn_id]
                worker.submit_work(params)

            while not self.can_render_fractal_img():
                continue

            self.display()

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