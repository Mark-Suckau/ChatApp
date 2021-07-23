from tkinter import *
import socket
import threading

class mainClass:
    Roman = ("Times New Roman", 20)
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.join_screen = Toplevel()
        self.screen_size = "1000x700"
        self.geometry = self.master.geometry(self.screen_size)
        self.home_label = Label(self.master, padx=40, pady=20, text="Hello world")
        self.home_label.pack()

        self.send_entry = Entry(self.master, width=45, font=Roman)
        self.master.mainloop()

    def main_screen(self):
        pass

