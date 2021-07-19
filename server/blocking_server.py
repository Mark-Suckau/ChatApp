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
    print(f'[{current_date_time}] {msg}')
    
  def configure_server(self):
    self.print_tstamp('[SERVER] Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp('[SERVER] Creating socket created')
    
    self.print_tstamp('[SERVER] Binding socket...')
    self.sock.bind((self.host, self.port))
    self.print_tstamp(f'[SERVER] Socket bound to {self.host} on port {self.port}')
  
  def listen_for_connections(self):
    self.print_tstamp('[SERVER] Listening for new connections...')
    self.sock.listen(1)
  
    client_sock, client_addr = self.sock.accept()
    self.print_tstamp(f'[SERVER] Accepted new connection from address {client_addr}')
    self.handle_client(client_sock, client_addr)
    
  def handle_client(self, client_sock, client_addr):
    try:
      self.print_tstamp('[SERVER] Handling client connection...')
      data_encoded = client_sock.recv(1024)

      while data_encoded:
        data = data_encoded.decode(self.format)
        self.print_tstamp(f'[SERVER] Received [{data}] from {client_addr}')

        data_encoded = client_sock.recv(1024)

      self.print_tstamp('[SERVER] Client disconnected')
    except OSError as err:
      self.print_tstamp(f'[SERVER] Encountered error {err}')
    
    finally:
      self.print_tstamp(f'[SERVER] Closing client connection from {client_addr}...')
      client_sock.close()
      self.print_tstamp(f'[SERVER] Closed client connection from {client_addr}')
    
  def shutdown_server(self):
    self.print_tstamp('[SERVER] Shutting down...')
    self.sock.close()
    self.print_tstamp('[SERVER] Shut down')


def main():
  server = TCP_Blocking_Server('localhost', 8080)
  server.configure_server()
  server.listen_for_connections()
  server.shutdown_server()
  
if __name__ == '__main__':
  main()