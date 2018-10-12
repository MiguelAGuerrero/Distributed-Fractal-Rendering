
from numba import jit, guvectorize, int32, complex128, complex64, uint8
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt

@guvectorize([(complex128[:], uint8[:])], '(n)->(n)', target='parallel')
def mandelbrot_vect(Z, T):
    creal = 0
    cimag = 0
    for i in range(Z.shape[0]):
        zimag = Z[i].imag
        zreal = Z[i].real
        T[i] = 0
        zreal2 = zreal * zreal
        zimag2 = zimag * zimag
        while zimag2 + zreal2 <= 4:
            zimag = 2 * zreal * zimag + cimag
            zreal = zreal2 - zimag2 + creal
            zreal2 = zreal * zreal
            zimag2 = zimag * zimag
            T[i] += 1

@guvectorize([(complex128[:], uint8[:])], '(n)->(n)', target='parallel')
def julia_vect(Z,T):
    creal = -2
    cimag = -0.5
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

def julia_numba_vect(N ,xmi,xma,ymi,yma):
    r1 = np.linspace(xmi, xma, 2*N)
    r2 = np.linspace(ymi, yma, N, dtype=np.float32)
    Z = r1 + r2[:,None]*1j
    T = julia_vect(Z)
    return T

@jit
def mandelbrot_numba_vect(N, xmi, xma, ymi,yma):
    x, y = np.ogrid[xmi:xma:5000j, ymi:yma:5000j]
    c = x + 1j * y
    z = 0
    for g in range(N):
        z = z ** 2 + c

    threshold = 2
    mask = np.abs(z) < threshold
    plt.imshow(mask.T, extent=[-2, 1, -1.5, 1.5])
    plt.show()

def mandelbrot_image(data, xmin=0, xmax=0, ymin=0, ymax=0, width=10, height=10, \
                     maxiter=256, cmap='jet', gamma=0.3):
    #dpi = 72
    # img_width = dpi * width
    # img_height = dpi * height
    # z = data

    fig, ax = plt.subplots(figsize=(width, height), dpi=72)
    # ticks = np.arange(0, img_width, 3 * dpi)
    # x_ticks = xmin + (xmax
    #  - xmin) * ticks / img_width
    # plt.xticks(ticks, x_ticks)
    # y_ticks = ymin + (ymax - ymin) * ticks / img_height
    # plt.yticks(ticks, y_ticks)
    # ax.set_title(cmap)

    norm = colors.PowerNorm(gamma)
    ax.imshow(data.T, cmap=cmap, origin='lower', norm=norm)
    plt.show()

if __name__ == '__main__':
    # data = julia_numba_vect(2000,-2,0,-1,0)
    # data2 = julia_numba_vect(2000,0,2, 0,1 )
    #data31 = julia_numba_vect(2000, 2,-2, -1, 1)
    # data4 = julia_numba_vect(2000, 0,2, -1,1)

    # mandelbrot_image(data)
    # mandelbrot_image(data2)
    # mandelbrot_image(data+data2)
    #mandelbrot_image(data31)
    # mandelbrot_image((data3)/(data+data2+data4))

    mandelbrot_numba_vect(480, -2, 1, -1, 1)
