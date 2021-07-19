import socket
import select

HEADER = 256
HOST = 'localhost'
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#def send_message(msg):
#  send_message = msg.encode(FORMAT)  
#  msg_length = len(send_message)
#  send_length = str(msg_length).encode(FORMAT)
#  send_length += b' ' * (HEADER - len(send_length))
#  
#  client.send(send_length)
#  client.send(send_message)
#  
#  received_message = client.recv(1024).decode(FORMAT)
#  print(received_message)
  
def send_message(msg):

  readables, writeables, exceptions = select.select([client], [client], [client], 0.5)

  for s in writeables:
    s.send(msg.encode(FORMAT))

  for s in readables:
    print(s.recv(1024).decode(FORMAT))

  for s in exceptions:
    print(s)
      
send_message('Hello World')
send_message('Test')