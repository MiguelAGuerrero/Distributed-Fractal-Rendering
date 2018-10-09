from numba import guvectorize, complex128, int32, void, vectorize, float32, float64, uint8
import numpy as np

# WWorker xmin, xmax, ymin, ymax, height, width, maxiter
xmin, xmax = -2, 2
ymin, ymax = -1, 1
height, width = 100, 100
maxiter = 280

r1 = np.linspace(xmin, xmax, width)
r2 = np.linspace(ymin, ymax, height)


creal = -.25
cimag = .579

def create_function(eqn):
    lamb_str = 'lambda z, c : '
    return eval(lamb_str + eqn)

@vectorize([int32(complex128, int32)])
def mandelbrot(z, maxiter):
        c = z
        for n in range(maxiter):
            if abs(z) > 2:
                return n
            z = z * z + c
            #z = create_function(input('Enter equation in terms of z and c'))
        return maxiter

def gen_with_escape_cond(f, i):
    def with_escape_cond(z, maxiter):
        c = z
        for n in range(maxiter):
            if abs(z) > i:
                return n
            z = f(z, c)
        return maxiter
    return with_escape_cond

@guvectorize(['float64[:], float64[:], int64[:,:]'], '(n),(m) -> (n,m)')
def mandelbrot_set(r1, r2, n3):
    n3 = np.empty((height, width))
    for i in range(width):
        for j in range(height):
            n3[j,i] = mandelbrot(r1[i] + 1j * r2[j], maxiter)

@guvectorize([(complex128[:], uint8[:])], '(n)->(n)', target='parallel')
def julia_vect(Z,T):
    c_real = creal
    c_imag = cimag
    for i in range(Z.shape[0]):
        zimag = Z[i].imag
        zreal = Z[i].real
        T[i] = 0
        zreal2 = zreal*zreal
        zimag2 = zimag*zimag
        while zimag2 + zreal2 <= 4:
            zimag = 2* zreal*zimag + cimag
            zreal = zreal2 - zimag2 + creal
            zreal2 = zreal*zreal
            zimag2 = zimag*zimag
            T[i] += 1
def julia_numba_vect():
    Z = r1 + r2[:,None]*1j
    T = julia_vect(Z)
    return T

def gen(f):
    def fu(r1, r2, n3=[]):
        n3 = np.empty((height, width))
        for i in range(width):
            for j in range(height):
                n3[j, i] = f(r1[i] + 1j * r2[j], maxiter)
    # Dynamically decoration of functioin
    return guvectorize(['float64[:], float64[:], int64[:,:]'], '(n),(m) -> (n,m)')(fu)

    # r1 = np.array(np.linspace(xmin, xmax, width)
    # r2 = np.array(np.linspace(ymin, ymax, height))
    # return [r1, r2]
    #return [mandelbrot(complex(r, i), maxiter) for r in r1 for i in r2]

if __name__ == '__main__':
    import time

    my = gen_with_escape_cond(create_function(input('Enter Equation in terms of z and c')), 2)
    start = time.time()
    #mandelbrot_set(r1, r2, np.ndarray((len(r1),len(r2))))
    f = gen(my)
    f(r1, r2, np.ndarray((len(r1), len(r2))))
    end = time.time()
    print(end - start)

    # start = time.time()
    # #mandelbrot_set(r1, r2, np.ndarray((len(r1), len(r2))))
    # end = time.time()
    # print(end - start)