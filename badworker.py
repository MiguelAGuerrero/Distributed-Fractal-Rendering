from client import Client
from fractalworker import FractalWorker
import random

'''
Bad Worker is used to test the how the system handles 
worker-related failures at different points in the system.
Using a random number (between 1 and 5) to provide a probability of the work
failing/closing in the middle of the computation.
'''
class BadWorker(FractalWorker):
    def __init__(self, address, port, conn_id=None, force_terminate=False):
        super().__init__(address, port, conn_id=None)
        self.rand = random.Random()
        self.force_terminate = force_terminate

    def compute(self, expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end):
        terminate = True if self.rand.randint(1, 5) == 1 else False
        if self.force_terminate or terminate:
            return None
        else:
            return super().compute(expr, xmin, xmax, ymin, ymax, img_width, img_height, max_itr, start, end)

if __name__ == "__main__":
    port = 80
    c = Client("127.0.0.1", port)
    for i in range(5):
        bw = BadWorker("127.0.0.1", port, conn_id=i)
        bw.start()

    input("press any key to continue")
    c.run()