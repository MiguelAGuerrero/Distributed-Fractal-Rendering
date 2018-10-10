from worker import Worker, WorkerStatus
import socket
import numpy as np
from msg import *

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

    def submit_work(self, args):
        self.set_status(WorkerStatus.WORKING)
        self.write(WORKMessage(args).as_bytes()) #Work message

    def close(self, state: WorkerStatus, msg=""):
        #Socket may be already closed
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

        self.set_status(state)

    def on_read_clse(self):
        self.close(WorkerStatus.DONE, msg="Worker closed connection")

    def on_read_acpt(self):
        print(self, "available")
        self.set_status(WorkerStatus.AVAILABLE)

    def on_read_rjct(self):
        print(self, "not available")
        self.set_status(WorkerStatus.UNAVAILABLE)

    def on_read_conn(self):
        pass

    def on_read_aval(self):
        pass

    def on_read_work(self, data):
        pass

    def on_read_rslt(self, data):
        #Last 8 bytes are the dimensions of the ndarray
        results = np.fromstring(data[:-16], dtype=int)
        rows = data[-16:-12]
        columns = data[-12:-8]
        section_start = data[-8:-4]
        section_end = data[-4:]
        results = results.reshape((rows, columns))
        self.client.canvas.put_pixels(data, section_start, 0)
        self.write(StaticMessage(MessageType.AVAL).as_bytes()) #Check is worker is available for next round

    def run(self):
        while not self.get_status() is WorkerStatus.DONE:
            self.read()
            if self.get_status() is WorkerStatus.FAILED:
                    print("Worker({}) failed".format(self.id))