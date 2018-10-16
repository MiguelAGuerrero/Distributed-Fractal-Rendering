from __future__ import division, print_function
import numpy as np
from numba import complex128, int32, vectorize
from enum import Enum, auto

class FractalType(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self

    MANDELBROT = auto()
    JULIA = auto()


def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter, begin, end, data=None):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float64)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float64)
    c = r1 + r2[:, None] * 1j

    offset = end - begin
    data = np.zeros((offset, width))
    for i in range(begin, end):
        for j in range(width):
            data[i - begin, j] = mandelbrot(c[i][j], maxiter)

    return data



@vectorize([int32(complex128, int32)])
def mandelbrot(z, maxiter):
    c = z
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
    return maxiter
#
