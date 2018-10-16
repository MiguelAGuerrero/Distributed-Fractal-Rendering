import socket
import threading
from clientworker import ClientWorker
from worker import WorkerStatus


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
        print('Connected to Worker:', worker)
        self._add_connection(self.ids, worker)
        return worker

    def workers_available(self):
        count = 0
        for conn_id in self.workers:
            if self.workers[conn_id].get_status() is WorkerStatus.AVAILABLE:
                count += 1
        return count

    def distribute_work(self, distribution_func, expr, *args):
        avail = self.get_available_workers()
        client_args = [expr, *distribution_func(0, len(avail) + 1, *args)]
        for i, worker in enumerate(avail):
            # Plus 1 to include client
            distributed_args = [expr, *distribution_func(i + 1, len(avail) + 1, *args)]

            worker.submit_work(distributed_args)

            print("Client REQ:", worker, distributed_args)

        return Task(avail, distribution_func, distributed_args), client_args

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
            return WorkerStatus.DONE

    def wait_or_break_on_failure(self):
        '''Needed if the client needs to handle a failure
        during computation. Waiting for all workers
        to be done can waste time if there is a
        failure'''
        while self.in_progress() or not self.failed():
            continue

    def wait(self):
        while self.in_progress():
            continue