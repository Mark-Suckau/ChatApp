import socket
from datetime import datetime
import queue
import select

class TCP_Nonblocking_Server:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = None
    
    self.format = 'utf-8'
    
    self.input_list = []      # read sockets
    self.output_list = []     # write sockets
    self.client_requests = {} # used for mapping request queues to client sockets
  
  def print_tstamp(self, msg):
    current_time = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
    print(f'[{current_time}] [SERVER] {msg}')
    
  def configure_server(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp('Socket created')
    
    self.sock.setblocking(False)
    
    self.print_tstamp(f'Binding socket to {self.host} on port {self.port}')
    self.sock.bind((self.host, self.port))
    self.print_tstamp(f'Bound socket to {self.host} on port {self.port}')
    
    self.input_list.append(self.sock)
    
  def accept_client_socket(self):
    client_sock, client_addr = self.sock.accept()
    self.print_tstamp(f'Accepted new connection from {client_addr}')
    
    client_sock.setblocking(False)
    
    self.client_requests[client_sock] = (client_addr, queue.Queue())
    self.input_list.append(client_sock)
    
  def close_client_socket(self, client_sock):
    client_addr = self.client_requests[client_sock][0]
    self.print_tstamp(f'Closing socket from address {client_addr}...')
    
    for s in self.input_list:
      if s == client_sock:
        self.input_list.remove(s)
    
    for s in self.output_list:
      if s == client_sock:
        self.output_list.remove(s)
    
    del self.client_requests[client_sock]
    client_sock.close()    
    
    self.print_tstamp(f'Socket closed from address {client_addr}')
    
  def receive_client_message(self, client_sock):
    try:    
      data_encoded = client_sock.recv(1024)

      if not data_encoded:
        # no data sent from client thus client must have disconnected
        self.close_client_socket(client_sock)
        return
      
      data = data_encoded.decode(self.format)
      
      self.client_requests[client_sock][1].put(data)
      
      if client_sock not in self.output_list:
        self.output_list.append(client_sock)
      
    except OSError as err:
      self.print_tstamp(f'Encountered error {err}')
      client_addr = self.client_requests[client_sock][0]

      self.close_client_socket(client_sock)
  
  def handle_client(self, client_sock):
    # respond to client with a request from client_requests
    
    try:
      client_addr = self.client_requests[client_sock][0]
      
      response = 'This is a response from the server'
      client_sock.send(response.encode(self.format))
      
      self.print_tstamp(f'Sent [{response}] to {client_addr}')
      
    except KeyError:
      # handles a condition where client socket is in the writable list
      # even though it's been removed from the dictionary
      pass
      
    except queue.Empty:
      self.output_list.remove(client_sock)
    
    except OSError as err:
      self.print_tstamp(f'Encountered error {err}')
    
    
  def handle_exception_socket(self, client_sock):
    client_addr = self.client_requests[client_sock][0]
    self.close_client_socket(client_sock)
    self.print_tstamp(f'Closed exception socket from address {client_addr}')

  def listen_for_connections(self):
    self.print_tstamp('Listening for connections...')
    self.sock.listen(10)
    try:
      while True:
        readable_socks, writable_socks, error_socks = select.select(self.input_list, self.output_list, self.input_list, 5)
        # read from readable sockets
        for sock in readable_socks:
          # if the socket is server socket, accept the connection
          if sock is self.sock:
            self.accept_client_socket()
          # otherwise receive the client request
          else:
            self.receive_client_message(sock)
            
        for sock in writable_socks:
          self.handle_client(sock)
        
        for sock in error_socks:
          self.handle_exception_socket(sock)
        
    except KeyboardInterrupt:
      self.print_tstamp('Shutting down server...')
      self.shutdown_server()
      self.print_tstamp('Server shut down')
        
  def shutdown_server(self):
    for s in self.input_list:
      s.close()
    
    for s in self.output_list:
      s.close()
      
    del self.input_list
    del self.output_list
    del self.client_requests
    
    self.sock.close()
    

def main():
  server = TCP_Nonblocking_Server('localhost', 8080)
  server.configure_server()
  server.listen_for_connections()
  
if __name__ == '__main__':
  main()