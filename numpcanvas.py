import fractalcanvas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

""" In the event that no workers are available,
    the end-user will use the NUMPCanvas.
    The NUMPCanvas uses Matplotlib for the rendering 
    which is compatible with Numpy Arrays that are
    passed into the Canvas.
"""
class NUMPCanvas(fractalcanvas.FractalCanvas):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.data = np.full((height, width), np.nan)
        self.data.dtype = np.int64

    def can_render(self):
        return not np.isnan(self.data).any()

    def set_pixels(self, arr):
        self.data = arr

    def get_pixels(self):
        return self.data

    def put_pixels(self, arr, i, j):
        self.data[i:(i + arr.shape[0]), j:(j + arr.shape[1])] = arr

    def put_pixel(self, pixel, i, j):
        self.data[i][j] = pixel

    def get_pixel(self, pixel, i ,j):
        return self.data[i][j]

    def render(self, *args, **kwargs):
        width = 10
        height = 10
        cmap = 'jet'
        gamma = 0.3
        fig, ax = plt.subplots(figsize=(width, height), dpi=72)
        norm = colors.PowerNorm(gamma)
        ax.imshow(self.data.T, cmap=cmap, origin='lower', norm=norm)
        self.data = np.full((self.height, self.width), -1)
        plt.show()