import tkinter as tk
from tkinter import *

window = tk.Tk()
window.title()
window.title('批量识别地图')
window.geometry('600x400')
l1=Label(window,text='路径名：')
l1.pack()
path_text=tk.Entry(bd=5,width=80)
path_text.pack()
def getPath():
    global path
    path=path_text.get()
    window.destroy()

def returnPath():
    path
    return path

btn=tk.Button(window,text='OK',command=getPath).pack()
window.mainloop()


