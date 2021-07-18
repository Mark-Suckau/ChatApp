from tkinter import *
import socket
import threading


class Window1:
    def __init__(self, master):
        self.master = master

        self.home_label = Label(master,text="hello world",font=("Helvetica",20))
        self.home_label.pack()
        self.test_button = Button(master,text="test button",padx=50, pady=60,command=lambda:self.clicker(),font = ("Times New Roman",39))
        self.test_button.pack()


        self.master.geometry("500x600")
        self.master.mainloop()

    def clicker(self):
        self.home_label.config(text="changed")


