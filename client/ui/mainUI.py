from tkinter import *
from rooms import mainClass
from PIL import ImageTk, Image

import os, sys
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
  
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)
import nonblocking_client



class Window1:
    def __init__(self, master):

        self.roman = ("Times New Roman", 19)
        assert isinstance(master, object)
        self.master = master
        self.my = Image.open("bluephoto.png")
        self.my = self.my.resize((620, 695))

        self.blue_img = ImageTk.PhotoImage(self.my)
        self.blue_screen = Label(self.master, image=self.blue_img)

        self.join_entry = Entry(self.master, width=45, font=self.roman, borderwidth=4)
        self.main_label = Label(self.master, text="            Enter Username", font=("Helvetica", 30))

        self.image_btn = PhotoImage(file="mainfolders/Join-Button.png")
        self.btn_label = Label(self.master, image=self.image_btn)
        self.join_btn = Button(self.master, image=self.image_btn, borderwidth=0, command=lambda: self.main_level())

        self.save = PhotoImage(file="mainfolders/save.png")
        self.save_label = Label(self.master, image=self.save)
        self.save_button = Button(self.master, image=self.save, borderwidth=0)

        self.join_btn.place(x=670, y=420)
        self.blue_screen.place(x=0, y=1)
        self.main_label.place(x=640, y=45)
        self.join_entry.place(x=640, y=100)

        self.username = self.join_entry.get()

        self.save_button.place(x=800, y=150)

        self.master.resizable(False, False)
        self.master.geometry("1230x703")
        self.master.mainloop()

    def main_level(self):
        self.f = Toplevel()
        self.main_text_box = Text(self.f, padx=18, pady=70, font=("Times New Roman", 11))
        self.main_text_box.place(x=1, y=0)

        self.send_img = PhotoImage(file='mainfolders/send4.png')
        self.send_button = Button(self.f, image=self.send_img, borderwidth=0,command=lambda:self.message())

        self.send_button.place(x=150, y=600)

        self.main_entry = Entry(self.f, width=28, font=("Times New Roman", 30))
        self.main_entry.place(x=26, y=550)

        self.f.title('Chat App')
        self.f.geometry("600x700")


    def message(self):

        message = self.main_entry.get()

        assert isinstance(message, object)
        self.main_text_box.insert(END, str(message) + "\n")