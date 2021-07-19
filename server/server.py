import socket
import threading
import select

HOST = 'localhost'
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
HEADER = 256

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

connections = []

def start():
  server.listen(5)
  running = True
  
  while running:
    conn, addr = server.accept()
    conn.setblocking(False)
    connections.append(conn)
    
    readables, writeables, exceptions = select.select(connections, connections, connections, 0.5)
    
    for s in readables:
      print(s.recv(1024).decode(FORMAT))
    
    for s in writeables:
      print(s.send('Test'.encode(FORMAT)))
    
    for s in exceptions:
      print(s)
    
    #thread = threading.Thread(target=handle_connection, args=(conn, addr))
    #thread.start()
    
  server.close()
    
    
def handle_connection(conn, addr):
  msg_length = conn.recv(256).decode(FORMAT)
  if msg_length:
    while True:
      msg_length = int(msg_length)
      msg = conn.recv(msg_length).decode(FORMAT)

      print(f'[{addr}] {msg}')
      conn.send('Message received'.encode(FORMAT))
      
print(f'[STARTING] Server listening on port {PORT}')
start()