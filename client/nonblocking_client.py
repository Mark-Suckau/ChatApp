import socket
import threading
from datetime import datetime
import traceback
import sys
import queue

class TCP_Nonblocking_Client:
  def __init__(self, host, port, name):
    self.host = host
    self.port = port
    self.sock = None
    self.format = 'utf-8'
    
    self.received_messages = queue.Queue()
    self.stop_client = False
    self.name = name
    
  def print_tstamp(self, msg):
    current_time = datetime.now().strftime("%Y-%M-%d %H:%M:%S")
    print(f'[{current_time}] [CLIENT] {msg}')
  
  def create_socket(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp(f'Socket created')

  def connect_to_server(self):
    try:
      self.print_tstamp(f'Connecting to server [{self.host}] on port [{self.port}]...')
        
      self.sock.connect((self.host, self.port))

      self.print_tstamp(f'Connected to server [{self.host}] on port [{self.port}]')
   
    except socket.error:
      self.stop_client = True
      
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
    except OSError as err:
      self.stop_client = True
      
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
  def send_message(self, msg):
    try:
      if msg:
        send_info = self.sock.send(msg.encode(self.format))
        self.print_tstamp(f'Sent {send_info} bytes to the server')

    except OSError as err:
      self.stop_client = True
      
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
  
  def shutdown_socket(self):
    self.print_tstamp('Closing socket...')
    self.sock.close()
    self.print_tstamp('Socket closed')
    
  def read_message_loop(self):
    # if function returns value then error has occured and interaction should be halted
    if self.connect_to_server():
      return
    
    while True:
      try:   
        msg = self.sock.recv(1024).decode(self.format)
          
      except socket.timeout:
        self.print_tstamp('Socket timed out, retrying receive')
        continue
      
      except:
        self.print_tstamp('Encountered socket error:')
        traceback.print_exc()
        break
        
      if msg == '':
        # connection closed by peer, exit loop
        self.print_tstamp('Connection closed by server')
        break
        
      self.print_tstamp(f'Received from [SERVER]: {msg}')
      self.received_messages.put(msg)

    self.shutdown_socket()
    self.stop_client = True
    
def run_socket():
  try:
    tcp_client = TCP_Nonblocking_Client('139.162.172.141', 8080, 'Jeff')
    tcp_client.create_socket()

    thread = threading.Thread(target=tcp_client.read_message_loop)
    thread.daemon = True
    thread.start()
    
    while True:
      message = input()
      if tcp_client.stop_client:
        tcp_client.print_tstamp('Socket already closed, message not sent')
        break
      tcp_client.send_message(message)
      
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  run_socket()
