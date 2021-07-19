import socket
from datetime import datetime

class TCP_Blocking_Client:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = None
    self.format = 'utf-8'
    
  def print_tstamp(self, msg):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
    print(f'[{current_time}] [CLIENT] {msg}')
  
  def configure_client(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp('Created socket')
    
  def interact_with_server(self):
    try:
      self.print_tstamp(f'Connecting to {self.host} on port {self.port}...')
      self.sock.connect((self.host, self.port))
      self.print_tstamp(f'Connected to {self.host} on port {self.port}')
      
      msg = 'Hello from client'
      self.print_tstamp(f'Sending message [{msg}] to {self.host} on port {self.port}...')
      self.sock.send(msg.encode(self.format))
      self.print_tstamp(f'Sent message [{msg}] to {self.host} on port {self.port}')
      
  
    except OSError as err:
      self.print_tstamp(f'Encountered error: {err}')

    finally:
      self.print_tstamp('closing socket...')
      self.sock.close()
      self.print_tstamp('closed socket')

      
def main():
  client = TCP_Blocking_Client('localhost', 8080)
  client.configure_client()
  client.interact_with_server()
  
if __name__ == '__main__':
  main()