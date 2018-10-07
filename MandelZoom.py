from numba import jit,guvectorize
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np




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

@jit
def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter, begin, end):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
    c = r1 + r2[:, None] * 1j
    data = np.zeros((height, width))
    for i in range(begin, end):
        for j in range(width):
            data[i, j] = mandelbrot(c[i][j], maxiter)

    return data.T


def mandelbrot_image2(xmin, xmax, ymin, ymax, width=10, height=10, \
                     maxiter=256, cmap='jet', gamma=0.3):
    dpi = 72
    img_width = dpi * width
    img_height = dpi * height
    z = mandelbrot_set2(xmin, xmax, ymin, ymax, img_width, img_height, maxiter)

    fig, ax = plt.subplots(figsize=(width, height), dpi=72)
    # ticks = np.arange(0, img_width, 3 * dpi)
    # x_ticks = xmin + (xmax - xmin) * ticks / img_width
    # plt.xticks(ticks, x_ticks)
    # y_ticks = ymin + (ymax - ymin) * ticks / img_width
    # plt.yticks(ticks, y_ticks)
    # ax.set_title(cmap)

    norm = colors.PowerNorm(gamma)
    ax.imshow(z.T, cmap=cmap, origin='lower', norm=norm)
    plt.show()
@jit
def mandelbrot_image(data, xmin, xmax, ymin, ymax, width=10, height=10, \
                     maxiter=256, cmap='jet', gamma=0.3):
    # dpi = 72
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