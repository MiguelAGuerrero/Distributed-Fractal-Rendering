from abc import ABC, abstractmethod

class Canvas(ABC):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @abstractmethod
    def can_render(self):
        pass

    @abstractmethod
    def set_pixels(self, arr):
        pass

    @abstractmethod
    def get_pixels(self):
        pass

    @abstractmethod
    def put_pixels(self, arr, i, j):
        pass

    @abstractmethod
    def put_pixel(self, pixel, i, j):
        pass

    @abstractmethod
    def get_pixel(self, pixel, i ,j):
        pass

    @abstractmethod
    def render(self, *args, **kwargs):
        pass
