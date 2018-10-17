from __future__ import division, print_function
import numpy as np
from numba import complex128, int32, vectorize
from enum import Enum, auto


'''
    Module that fractal workers use to access computational predefined fractals
    this design choice was made when we realized that function pointers are 
    tricky and to avoid security issue that arise from using eval
    (eval is evil)
'''

'''
    Create FractalType Enumerations to use the respective computations 
    based on the Enumeration given by the Client.
'''
class FractalType(Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self

    MANDELBROT = auto()
    JULIA = auto()

'''
    Delegation of Work:
        Using the begin and end parameters, workers are able 
        to successfully compute a portion of the fractal, 
        this delegation of work is dependent upon the 
        number of available workers.
        
    Real and Imaginary Number Generation:
        Using boundaries for the image
        i.e.(xmin,xmax,ymin, ymax, Width, Height)
        We generate a set of real points and 
        a set of imaginary points(r2 * 1j) and
        store them in c. 
        
    Populating data array:
        We pass in single points of c, a max iteration # and 
        generate different points to fill out the data numpy array. 
'''
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

'''
    Basic Mandelbrot Function that enforce types via Numba
    @Vectorize it requires that this function return a 
    single-precision integer and it takes a 
    double-precison complex number and 
    a single-precision integer as its parameters.
    
    It allows our computers to use our GPUs to make
    this slow, naive computation really fast!!!
'''
@vectorize([int32(complex128, int32)])
def mandelbrot(z, maxiter):
    c = z
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
    return maxiter
#
