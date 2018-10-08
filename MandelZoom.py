from numba import jit, guvectorize, float64, complex64,int64, float32
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

@jit
def mandelbrot(c, maxiter):
    nreal = 0
    real = 0
    imag = 0
    for n in range(maxiter):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal;
        if real * real + imag * imag > 4.0:
            return n
    return 0


#@guvectorize([(complex64[:], int32[:], int32[:])], '(n),()->(n)', target='parallel')
# def mandelbrot_numpy(c, maxit, output):
#     maxiter = maxit[0]
#     for i in range(c.shape[0]):
#         output[i] = mandelbrot(c[i], maxiter)

def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter, begin, end, data=None):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float64)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float64)
    c = r1 + r2[:, None] * 1j

    offset = end - begin
    data = np.zeros((offset, width))
    for i in range(begin, end):
        for j in range(width):
            data[i - offset, j] = mandelbrot(c[i][j], maxiter)
    return data

def mandelbrot_image2(xmin, xmax, ymin, ymax, width=10, height=10, \
                     maxiter=256, cmap='jet', gamma=0.3):
    dpi = 72
    img_width = dpi * width
    img_height = dpi * height
    z = mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, maxiter)

    fig, ax = plt.subplots(figsize=(width, height), dpi=72)
    ticks = np.arange(0, img_width, 3 * dpi)
    x_ticks = xmin + (xmax - xmin) * ticks / img_width
    plt.xticks(ticks, x_ticks)
    y_ticks = ymin + (ymax - ymin) * ticks / img_width
    plt.yticks(ticks, y_ticks)
    ax.set_title(cmap)

    norm = colors.PowerNorm(gamma)
    ax.imshow(z.T, cmap=cmap, origin='lower', norm=norm)
    plt.show()

@jit
def mandelbrot_image(data, xmin, xmax, ymin, ymax, width=10, height=10, \
                     maxiter=256, cmap='jet', gamma=0.3):
    #dpi = 72
    # img_width = dpi * width
    # img_height = dpi * height
    # z = data

    fig, ax = plt.subplots(figsize=(width, height), dpi=72)
    # ticks = np.arange(0, img_width, 3 * dpi)
    # x_ticks = xmin + (xmax - xmin) * ticks / img_width
    # plt.xticks(ticks, x_ticks)
    # y_ticks = ymin + (ymax - ymin) * ticks / img_height
    # plt.yticks(ticks, y_ticks)
    # ax.set_title(cmap)

    norm = colors.PowerNorm(gamma)
    ax.imshow(data.T, cmap=cmap, origin='lower', norm=norm)
    plt.show()