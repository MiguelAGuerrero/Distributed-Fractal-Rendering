from worker import Worker, WorkerStatus
import socket
import numpy as np
from msg import *


'''
ClientWorker is responsible for listening to FractalWorkers. Everytime a FractalWorker connects to the 
client's WorkManager, a ClientWorker is created and ran in its own thread. ClientWorkers will take results
and put them onto the canvas that the client is configured to. This is so that the client does not
block it's own thread to put results onto the canvas. 
'''
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

        print("{} closed with status {}:".format(self.__str__(), state.value),  msg)

        #Set self to done to escape while loop in
        #run()
        self.set_status(WorkerStatus.DONE)

    def on_read_clse(self):
        self.close(WorkerStatus.DONE, msg="Worker closed connection")

    def on_read_conn(self):
        self.set_status(WorkerStatus.AVAILABLE)

    def on_read_work(self, data):
        pass

    def on_read_fail(self):
        self.set_status(WorkerStatus.FAILED)

    def on_read_rslt(self, data):
        results = np.fromstring(data[:-16])
        rows = int.from_bytes(data[-16:-12], sys.byteorder)
        columns = int.from_bytes(data[-12:-8], sys.byteorder)
        section_start = int.from_bytes(data[-8:-4], sys.byteorder)

        # Used for potential vertical partitioning of work
        section_end = int.from_bytes(data[-4:], sys.byteorder)
        results = results.reshape((rows, columns))
        self.client.canvas.put_pixels(results, section_start, 0)
        self.set_status(WorkerStatus.AVAILABLE)

    def run(self):
        while not self.get_status() is WorkerStatus.DONE:
            self.read()
            if self.get_status() is WorkerStatus.FAILED:
                    pass #Wait until a manager checks for the failure

