from tkinter import *
from PIL import ImageTk,Image

class GUI:
    def __init__(self, image):
        self.root = Tk()
        self.img = ImageTk.PhotoImage(image,size=(1000,750))
        self.canvas = Canvas(self.root, width=1000, height=1000)
        self.canvas.imageList=[]
        self.canvas.pack()
        self.canvas.create_image(500,400,image=self.img)
        self.img.
        self.canvas.imageList.append(self.img)
        self.root.mainloop()

