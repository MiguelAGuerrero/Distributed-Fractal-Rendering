import Worker
import numpy
class ClientWorker(Worker.Worker):

    def __init__(self, client, socket):
        super().__init__(None, None)
        self.client = client
        self.sock = socket
        self.work_status = False
        self.start()

    def validate_data(self, data):
        return data

    def get_status(self):
        return self.work_status

    def submit_work(self, params):
        self.write(params)
        self.work_status = True

    #Implement this
    def run(self):
        done = False
        while not done:
            if self.work_status:
                data = self.read()
                if type(data) is numpy.ndarray and data.any():
                    print('Client Worker got data')
                    self.client.receive(data)
                    self.work_status = False
                elif type(data) is list and not data:
                    pass