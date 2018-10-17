import socket
import threading
from clientworker import ClientWorker
from worker import WorkerStatus


'''
workmanager contains the WorkManager class, which is responsible for listening to any potential FractalWorkers
from other computers. WorkManager, as it is, aggregates connections and is able to know the statuses
of the workers. In addition, WorkManagers are able to distribute works to connected workers, as well as provide
arguments for the client so that it may render itself.

Each client instance should have a WorkerManager, as it how the distributed system can be developed for the 
DFR application   
'''
class WorkManager(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.workers = {}
        self.ids = 0;
        self.client = client
        self._make_server_socket()
        self.start()

    def _make_server_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.client.address, self.client.port))
        self.sock.listen(16)
        self.sock.settimeout(1)

    def accept_connection(self):
        self.ids = self.ids + 1
        conn, addr = self.sock.accept()
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

    '''
        Determines how to split a fractal computation by adjusting the arguments for a fractal 
         function's paraemeters. The split is even, so all workers have an equal amount of work to perform.
         The Manager adjusts for one worker more than the amount of available workers because the client
         should be able to perform work.
    '''
    def distribute_work(self, distribution_func, expr, *args):
        avail = self.get_available_workers()
        client_args = [expr, *distribution_func(0, len(avail) + 1, *args)]
        for i, worker in enumerate(avail):
            # Plus 1 to include client
            distributed_args = [expr, *distribution_func(i + 1, len(avail) + 1, *args)]

            worker.submit_work(distributed_args)

            print("Distribution:", worker, distributed_args)

        return Task(avail, distribution_func, distributed_args), client_args


    def get_available_workers(self):
        #Client workers that have failed are considered available. It is assumed that
        #that the failure has been recognized because of the control flow of the program
        for worker in self.get_workers():
            if worker.get_status() is WorkerStatus.FAILED:
                worker.set_status(WorkerStatus.AVAILABLE)
        return [worker for worker in self.get_workers() if worker.get_status() is WorkerStatus.AVAILABLE]

    def _add_connection(self, conn_id, worker):
        self.workers[conn_id] = worker

    def _remove_connection(self, conn_id):
        del self.workers[conn_id]

    def run(self):
        done = False
        while not done:
            try:
                worker = self.accept_connection()
            except:
                pass
            self.purge_dead_workers()

    def purge_dead_workers(self):
        for id in list(self.workers.keys()):
            worker = self.workers[id]
            if worker and worker.get_status() is WorkerStatus.DONE:
                self._remove_connection(id)

    def get_workers(self):
        return self.workers.values()

    def redistribute_work(self, task):
        pass

'''
    A class that represents the status of workers overall
    so the Client would not have to know how to check 
    the status of workers and it provide useful methods 
    like waiting for the task to finish or breaking 
    upon a failure in the task.
    
    The main difference between Task and WorkManager is that
    Task refers to only a subset of workers that WorkManager has, and
    only performs checks and waits on those workers only.
'''
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