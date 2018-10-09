from Worker import Worker, WorkerState
import socket

class ClientWorker(Worker):

    def __init__(self, client, sock):
        super().__init__(None, None)
        self.client = client
        self.sock = sock
        self.start()

    def validate_data(self, data):
        return data

    def set_status(self, status: WorkerState):
        self.status = status

    def get_status(self):
        return self.state

    def get_work_submission(self):
        return self.work_section, self.work_params

    def submit_work(self, x0, y0, x1, y1, params):
        self.work_section = (x0, y0, x1, y1)
        self.work_params = params
        self.write(params)

    def close(self, state: WorkerState, msg=""):
        #Socket may be already closed
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

        self.set_status(state)

    def run(self):
        while not self.get_status() == WorkerState.DONE and not self.get_status() == WorkerState.FAILED:
            if self.get_status() == WorkerState.AVAILABLE:
                self.set_status(WorkerState.WORKING)
                data = self.read()
                if self.get_status() != WorkerState.FAILED:
                    if data and hasattr(data, "__getitem__"):
                        print('Client Worker got data:', data)
                        self.client.canvas.put_pixels(data, self.work_section[1], self.work_section[0])
                        self.set_status(WorkerState.AVAILABLE)
                    elif type(data) is list and not data:
                        pass
            else:
                print("WORKER FAILED")