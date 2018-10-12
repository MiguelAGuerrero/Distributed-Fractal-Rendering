import Canvas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

class MLTCanvas(Canvas.Canvas):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.data = np.full((height, width), np.nan)

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
        ax.imshow(self.data.T, cmap=cmap, origin='lower', norm=norm)
        self.data = np.full((self.height, self.width), -1)
        plt.show()