from tkinter import *
from PIL import ImageTk, Image
import threading

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
import client



class Window1:
    def __init__(self, master):
        self.roman = ("Times New Roman", 19)
        assert isinstance(master, object)
        self.master = master
        self.my = Image.open("images/bluephoto.png")
        self.my = self.my.resize((620, 695))

        self.blue_img = ImageTk.PhotoImage(self.my)
        self.blue_screen = Label(self.master, image=self.blue_img)
        self.blue_screen.place(x=0, y=1)

        self.username_entry = Entry(self.master, width=45, font=self.roman, borderwidth=4)
        self.username_label = Label(self.master, text="            Enter Username", font=("Helvetica", 30))
        self.username_label.place(x=640, y=45)
        self.username_entry.place(x=640, y=100)
        
        self.password_entry = Entry(self.master, width=45, font=self.roman, borderwidth=4)
        self.password_label = Label(self.master, text="            Enter Password", font=("Helvetica", 30))
        self.password_label.place(x=640, y=160)
        self.password_entry.place(x=640, y=245)

        self.image_btn = PhotoImage(file="images/Join-Button.png")
        self.btn_label = Label(self.master, image=self.image_btn)
        self.join_btn = Button(self.master, image=self.image_btn, borderwidth=0, command=lambda: self.open_chat())
        self.join_btn.place(x=50, y=420)
        
        self.save = PhotoImage(file="images/save.png")
        self.save_label = Label(self.master, image=self.save)
        self.save_button = Button(self.master, image=self.save, borderwidth=0)
        self.save_button.place(x=180, y=150)

        self.master.resizable(False, False)
        self.master.geometry("1230x703")
        self.master.mainloop()
        
    def connect(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        self.tcp_client = client.TCP_Nonblocking_Client('139.162.172.141', 8080, self.username, self.password)
        self.tcp_client.create_socket()
        self.tcp_client.connect_to_server()
        
        # will be true when something goes wrong (in this case if connection fails)
        if self.tcp_client.stop_client:
            return False

        reading_thread = threading.Thread(target=self.tcp_client.read_message_loop)
        reading_thread.daemon = True
        reading_thread.start()
        
        displaying_thread = threading.Thread(target=self.display_messages)
        displaying_thread.daemon = True
        displaying_thread.start()
        return True

    def open_chat(self):
        if not self.connect():
            self.display_login_error('Incorrect username or password')
            return
        
        self.f = Toplevel()
        self.main_text_box = Text(self.f, padx=18, pady=70, font=("Times New Roman", 11))
        self.main_text_box.place(x=1, y=0)

        self.send_img = PhotoImage(file='images/send4.png')
        self.send_button = Button(self.f, image=self.send_img, borderwidth=0, command=lambda:self.send_message())

        self.send_button.place(x=150, y=600)

        self.send_message_entry = Entry(self.f, width=28, font=("Times New Roman", 30))
        self.send_message_entry.place(x=26, y=550)

        self.f.title('Chat App')
        self.f.geometry("600x700")

    def display_login_error(self, error_msg):
        pass # display error when logging in

    def send_message(self):
        message = self.send_message_entry.get()
        self.tcp_client.send_message(message)
        
    def display_messages(self):
        while True:
            if self.tcp_client.stop_client:
                break
            
            message = self.tcp_client.received_messages.get()
            
            assert isinstance(message, object)
            self.main_text_box.insert(END, f'{str(message["username"])}: {str(message["content"])}' + "\n")
    