from worker import Worker, WorkerStatus
import socket
import numpy as np
from msg import *

class ClientWorker(Worker):

    def __init__(self, client, sock, conn_id=None):
        super().__init__(None, None, conn_id=conn_id)
        self.client = client
        self.sock = sock
        self.start()

    def validate_data(self, data):
        return data

    def get_work_submission(self):
        return self.work_section, self.work_args

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
        results = np.fromstring(data[:-16])
        print("Shape as client worker sees it:", results.shape)

        print(data[-16:-12], data[-12:-8], data[-8:-4],data[-4:])
        rows = int.from_bytes(data[-16:-12], sys.byteorder)
        columns = int.from_bytes(data[-12:-8], sys.byteorder)
        section_start = int.from_bytes(data[-8:-4], sys.byteorder)
        section_end = int.from_bytes(data[-4:], sys.byteorder)

        print("Rows: {}, Columns: {}, Section Start: {}, Section End: {}".format(rows, columns, section_start, section_end))
        results = results.reshape((rows, columns))
        print(self.client.canvas.get_pixels().shape)
        self.client.canvas.put_pixels(results, section_start, 0)
        self.set_status(WorkerStatus.AVAILABLE)

    def run(self):
        while not self.get_status() is WorkerStatus.DONE:
            self.read()
            if self.get_status() is WorkerStatus.FAILED:
                    print("Worker({}) failed".format(self.id))
