from numba import guvectorize, complex128, int32, void, vectorize, float32, float64, uint8
import numpy as np
from math import *

# Worker xmin, xmax, ymin, ymax, height, width, maxiter
xmin, xmax = -2, 2
ymin, ymax = -1, 1
height, width = 100, 100
maxiter = 280


creal = -.25
cimag = .579

def create_function(eqn):
    lamb_str = 'lambda z, c : '
    return eval(lamb_str + eqn)

def gen_with_escape_cond(f, i):
    def with_escape_cond(z, maxiter):
        c = z
        for n in range(maxiter):
            if abs(z) > i:
                return n
            z = f(z, c)
        return maxiter
    return with_escape_cond

# def julia_numba_vect():
#     Z = r1 + r2[:,None]*1j
#     T = julia_vect(Z)
#     return T

def gen(f):
    def fu(r1, r2, maxitr, n3):
        height  = len(r1)
        width = len(r2)
        for i in range(width):
            for j in range(height):
                n3[j, i] = f(r1[j] + 1j * r2[i], maxiter)

    # Dynamically decoration of functioin
    return guvectorize(['float64[:], float64[:], int32, int64[:,:]'], '(n),(m), () -> (n,m)')(fu)

    # r1 = np.array(np.linspace(xmin, xmax, width)
    # r2 = np.array(np.linspace(ymin, ymax, height))
    # return [r1, r2]
    #return [mandelbrot(complex(r, i), maxiter) for r in r1 for i in r2]

if __name__ == '__main__':
    pass

    # start = time.time()
    # #mandelbrot_set(r1, r2, np.ndarray((len(r1), len(r2))))
    # end = time.time()
    # print(end - start)