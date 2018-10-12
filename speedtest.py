from fractal import *
from time import time
from multiprocessing import freeze_support
def gen(model, y0, y1, c, size):
     generate_rows(model, y0, y1, c, size=size)

for i in range(749, 750):
    try:
        t1 = time()
        gen("julia", 0, i, 1.037 + 0.17j, size=(i, i))
        t2 = time()
        print("time took:", t2 - t1)
    except:
        pass