import MandelZoom
from tkinter import *

args=[]

def show_entry_fields():
    print("Xmin: {}\nXmax: {}\nYmin: {}\n Ymax: {}".format(e1.get(), e2.get(), e3.get(), e4.get()))
    args.append([float(e1.get()), float(e2.get()), float(e3.get()), float(e4.get())])
    print(args)

def Mandelbrot():
    print('Start Mandelbrot')
    MandelZoom.mandelbrot_image(args[0][0],args[0][1],args[0][2],args[0][3])
    print('Finished Mandelbrot')
    args.pop(0)
    print(args)

def scale_info():
    args.append([float(w1.get())/100, float(w2.get())/100, float(w3.get())/100, float(w4.get())/100])
    print(args)

master = Tk()
master.title('DFR Application')
Label(master, text = "Xmin ").grid(row = 0)
master.grid_columnconfigure(1,weight=1)

Label(master, text = "Xmax ").grid(row = 1)
master.grid_columnconfigure(1,weight=1)

Label(master, text = "Ymin ").grid(row = 2)
master.grid_columnconfigure(1,weight=1)

Label(master, text = "Ymax ").grid(row = 3)
master.grid_columnconfigure(1,weight=1)


e1 = Entry(master)
e2 = Entry(master)
e3 = Entry(master)
e4 = Entry(master)

print(e1, e2, e3, e4)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
e4.grid(row=3, column=1)

Button(master, text='Quit', command=master.quit).grid(row=4, column=3, sticky=W, pady=2)
Button(master, text='Store Entry', command=show_entry_fields).grid(row=4, column=0, sticky=W, pady=2)
Button(master, text='Store Scale', command = scale_info).grid(row=4, column=1, sticky = W, pady=2)
Button(master, text='Draw', command = Mandelbrot).grid(row=4,column=2, sticky = W, pady=2)

w1 = Scale(master, from_=-210, to=100,length=950,tickinterval=1, orient=HORIZONTAL)
w2 = Scale(master, from_=-210, to=100,length=950 ,tickinterval=1, orient=HORIZONTAL)
w3 = Scale(master, from_=-100, to=100,length=950 ,tickinterval=1, orient=HORIZONTAL)
w4 = Scale(master, from_=-100, to=100,length=950 ,tickinterval=1, orient=HORIZONTAL)
w1.grid(row = 0, column= 2)
w2.grid(row = 1, column =2)
w3.grid(row = 2, column= 2)
w4.grid(row = 3, column =2)
# def hi():
#     print("Hi!")
#
# root = tk.Tk()
# root.title("DFR System GUI")
# frame = tk.Frame(root)
# frame.pack()
#
# # button = tk.Button().button.pack()
# createFractal  = tk.Button(frame, text="Create Image", command=hi).pack(side='top')
#
# logo = tk.PhotoImage(file="Mandelbrot_Animation0.gif")
# w1 = tk.Label(root, image=logo ).pack(side="right")

# explaination = """At Present, the Application only supports jpeg and png formats, but we're working on it"""
# w2 = tk.Label(root, justify=tk.LEFT, padx=5, text=explaination).pack(side='left')



mainloop()
