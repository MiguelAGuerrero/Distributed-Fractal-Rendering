from PIL import ImageTk

from fractalcanvas import FractalCanvas
import PIL


class GUICanvas(FractalCanvas):
    def __init__(self, width, height, canvas):
        super().__init__(width, height)
        self.img_width = width
        self.img_height = height
        self.canvas = canvas
        self.img = PIL.Image.new('RGB', (self.img_width, self.img_height))
        print(type(self.img))

    def can_render(self): pass
    def set_pixels(self, arr): pass
    def get_pixels(self): pass
    def put_pixels(self, arr, i, j):
        for row in range(i, arr.shape[0]):
            for column in range(j, arr.shape[1]):
                self.img.putpixel((column,row),(int(arr[row, column]) % 4 * 64, int(arr[row, column]) % 8 * 32, int(arr[row, column]) % 16 * 16))

    def put_pixel(self, pixel, i, j):
            self.img.putpixel((i, j), (250,255,200))
    def get_pixel(self, pixel, i, j): pass
    def render(self, *args, **kwargs):
        self.image = ImageTk.PhotoImage(image=self.img)
        self.canvas.create_image(self.img_width-400, self.img_height-400, image=self.image)
