from abc import ABC, abstractmethod

class Canvas(ABC):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @abstractmethod
    def putPixels(self, arr):
        pass

    @abstractmethod
    def getPixels(self):
        pass

    @abstractmethod
    def render(self):
        pass