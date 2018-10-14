from tkinter import *
from PIL import ImageTk,Image
from dfrapp import Client
from GUICanvas import GUICanvas
class GUI:
    def __init__(self):
        self.client = Client('127.0.0.1', 1000)
        self.root = Tk()
        self.parameters =[]
        self.fields = 'img_width', 'img_height', 'xmin', 'xmax','ymin','ymax','maxiter','fractal'
        ents = self.makeform(self.fields)
        # self.root.bind('<Return>', (lambda event, e=ents: self.fetch(e)))
        b1 = Button(self.root, text='Render', command=(lambda e=ents: self.run_client(e)))
        b1.pack()

        self.canvas = Canvas(self.root, width=650, height=650)
        self.fcanvas = GUICanvas(650, 650, self.canvas)
        self.canvas.pack(side=TOP, padx=5, pady=5)
        self.client.canvas = self.fcanvas
        self.root.mainloop()

    def run_client(self, entries):
        args = self.fetch(entries)
        for param in args:
            setattr(self.client, param, args[param])
        self.client.run()

    def fetch(self,entries):
        args = {}
        for entry in entries[:-1]:
            field = entry[0]
            text = entry[1].get()
            args[field] = int(text)
            print('%s: "%s"' % (field, text))
        args[entries[-1][0]] = entries[-1][1].get()
        return args
    def makeform(self, fields):
        entries = []
        for field in fields:
            row = Frame(self.root)
            lab = Label(row, width=15, text=field, anchor='w')
            ent = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))
        return entries

    def render(self):
        '''Image Code '''
        self.imag = ImageTk.PhotoImage(self.img,size=(1000,750))
        self.canvas = Canvas(self.root, width=2000, height=2000)
        self.canvas.imageList=[]
        self.canvas.grid(row=0, column=8,sticky=E)
        self.canvas.create_image(500,400,image=self.imag)
        self.canvas.imageList.append(self.imag)
        self.root.mainloop()

    def clicked1(self):
        input = self.entrytext.get()
        print(input)

    def clicked2(self):
        input = self.entrytext1.get()
        print("width is ", input)
    def updateScreen(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        print(w, h)

if __name__ == '__main__':
    GUI()