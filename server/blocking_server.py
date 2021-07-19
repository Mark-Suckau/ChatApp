import socket
from datetime import datetime

class TCP_Blocking_Server:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.format = 'utf-8'
    self.sock = None
    
  def print_tstamp(self, msg):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] [SERVER] {msg}')
    
  def configure_server(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp('Creating socket created')
    
    self.print_tstamp('Binding socket...')
    self.sock.bind((self.host, self.port))
    self.print_tstamp(f'Socket bound to {self.host} on port {self.port}')
  
  def listen_for_connections(self):
    self.print_tstamp('Listening for new connections...')
    self.sock.listen(1)
  
    client_sock, client_addr = self.sock.accept()
    self.print_tstamp(f'Accepted new connection from address {client_addr}')
    self.handle_client(client_sock, client_addr)
    
  def handle_client(self, client_sock, client_addr):
    try:
      self.print_tstamp('Handling client connection...')
      data_encoded = client_sock.recv(1024)

      while data_encoded:
        data = data_encoded.decode(self.format)
        self.print_tstamp(f'Received [{data}] from {client_addr}')

        data_encoded = client_sock.recv(1024)

      self.print_tstamp('Client disconnected')
    except OSError as err:
      self.print_tstamp(f'Encountered error {err}')
    
    finally:
      self.print_tstamp(f'Closing client connection from {client_addr}...')
      client_sock.close()
      self.print_tstamp(f'Closed client connection from {client_addr}')
    
  def shutdown_server(self):
    self.print_tstamp('Shutting down...')
    self.sock.close()
    self.print_tstamp('Shut down')


def main():
  server = TCP_Blocking_Server('localhost', 8080)
  server.configure_server()
  server.listen_for_connections()
  server.shutdown_server()
  
if __name__ == '__main__':
  main()