from Worker import Worker, WorkerStatus
import socket
import numpy as np

class ClientWorker(Worker):

    def __init__(self, client, sock, id=None):
        super().__init__(None, None, id=id)
        self.client = client
        self.sock = sock
        self.start()

    def validate_data(self, data):
        return data

    def get_work_submission(self):
        return self.work_section, self.work_params

    def submit_work(self, x0, y0, x1, y1, params):
        self.set_status(WorkerStatus.WORKING)
        self.work_section = (x0, y0, x1, y1)
        self.work_params = params
        self.write(params)

    def close(self, state: WorkerStatus, msg=""):
        #Socket may be already closed
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

        self.set_status(state)

    def run(self):
        while not (self.get_status() is WorkerStatus.DONE) or (not self.get_status() is WorkerStatus.FAILED):
            if self.get_status() is WorkerStatus.WORKING:
                print("Reading:", self.get_status())
                data = self.read()
                print("Read:", self.get_status())
                if self.get_status() is not WorkerStatus.FAILED:
                    if type(data) is np.ndarray:
                        print('Client Worker got data:', data)
                        self.client.canvas.put_pixels(data, self.work_section[1], self.work_section[0])
                        self.set_status(WorkerStatus.AVAILABLE)
                    elif type(data) is list and not data:
                        pass
                else:
                    print("Worker({}) failed".format(self.id))