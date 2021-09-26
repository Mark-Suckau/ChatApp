import socket, queue, select, json, traceback
from datetime import datetime
from chatapp.shared import message
class TCP_Nonblocking_Server:
  def __init__(self, host, port, verbose_output=True):
    self.host = host
    self.port = port
    self.sock = None
    self.timeout = 1 # timeout for select.select() in listen_for_connections()
    
    self.format = 'utf-8'
    self.verbose_output = verbose_output # determines if anything is logged to terminal
    
    self.client_list = [] # used for storing sockets
    self.client_info = {} # used for storing info about sockets (ex. address, etc.)
    self.client_messages = queue.Queue() # used for saving messages from clients before sending them to all other clients
    
    self.configure_server()
  
  def print_tstamp(self, msg):
    if self.verbose_output:
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
    
    self.client_list.append(self.sock)
    
  def accept_client_socket(self):
    client_sock, client_addr = self.sock.accept()
    self.print_tstamp(f'Accepted new connection from {client_addr}')
    
    client_sock.setblocking(False)
    
    self.client_info[client_sock] = {'address': client_addr, 'verified': False}
    self.client_list.append(client_sock)
    
  def close_client_socket(self, client_sock):
    client_addr = self.client_info[client_sock]['address']
    self.print_tstamp(f'Closing socket from address {client_addr}...')
    
    for s in self.client_list:
      if s == client_sock:
        self.client_list.remove(s)
    
    del self.client_info[client_sock]
    client_sock.close()    
    
    self.print_tstamp(f'Socket closed from address {client_addr}')
    
  def receive_message(self, client_sock):
    try:    
      data_encoded = client_sock.recv(1024)
      client_addr = self.client_info[client_sock]['address']
      client_verified = self.client_info[client_sock]['verified']
      
      if not data_encoded:
        # no data sent from client thus client must have disconnected
        self.close_client_socket(client_sock)
        self.print_tstamp(f'{client_addr} disconnected')
        return
      
      data = data_encoded.decode(self.format) # decoding from utf-8 bytes to string
      data = json.loads(data)                 # converting from json string to python dict
      
      # check if client is verified
      if not client_verified:
        # check if client is sending a valid verification request
        if message.is_type(data, message.config_msg_types_client['VERIFICATION_REQUEST']):
          
          # attempt to verify client
          could_verify = self.verify_client(client_sock, data['username'], data['password'])

          msg = message.create_message(type=message.config_msg_types_server['VERIFICATION_RESPONSE'], verified=could_verify, error_msg='a', status_code='a')
          msg = json.dumps(msg)
          msg = msg.encode(self.format)
          
          client_sock.send(msg)
          
          # close connection if couldnt verify username and/or password
          if not could_verify:
            self.close_client_socket(client_sock)
            
        else:
          # closes connection if verification message is not in correct format
          self.close_client_socket(client_sock)
          
      else:
        # if client is verified, then check if message is correctly formatted and accept message, not correctly formatted messages will be ignored
        if message.is_type(data, 'CLIENT_TEXT'):
          self.print_tstamp(f'{client_addr} client says: [{data}]')

          self.client_messages.put(data)
      
    except json.JSONDecodeError:
      self.print_tstamp('Encountered error: Could not decode JSON')
      traceback.print_exc()
      
      self.close_client_socket(client_sock)
      
      
    except OSError as err:
      self.print_tstamp(f'Encountered error: ')
      traceback.print_exc()
            
      self.close_client_socket(client_sock)
  
  def verify_client(self, client_sock, username, password):
    #return True or False depending on if client could be verified
    if username == 'testUsername' and password == 'testPassword':
      self.client_info[client_sock]['verified'] = True
      return True

    return False
  
  def broadcast_message(self, client_socks):
    # broadcasts messages sent from other clients to other clients
    # takes a list of client sockets to broadcast message to
    try:
      msg = self.client_messages.get_nowait() # get message sent from a client
      msg = json.dumps(msg)          # convert from python dict to json string
      msg = msg.encode(self.format)  # encode from json string to utf-8 bytes

      self.print_tstamp(f'Broadcasting message to {len(client_socks)} clients...')
      for s in client_socks:
        s.send(msg)
      self.print_tstamp(f'Broadcasted message to {len(client_socks)} clients')
    
    except queue.Empty:
      pass
  
  def send_message(self, client_sock, msg_content):
    # respond to client with a predefined message from the server
    
    try:
      client_addr = self.client_info[client_sock]['address']
      client_username = self.client_info[client_sock]['username']
      
      msg = message.create_message(type=message.config_msg_types_server['SERVER_TEXT'], msg_body=msg_content, username=client_username)
      
      msg = json.dumps(msg)            # convert msg from python dict to json string
      msg = msg.encode(self.format)             # encoding msg from json string to utf-8 bytes
      send_info = client_sock.send(msg)         # sending msg
      
      self.print_tstamp(f'Sent {send_info} bytes to {client_addr}')
      
    except KeyError:
      # handles a condition where client socket is in the writable list
      # even though it's been removed from the dictionary
      pass
    
    except OSError as err:
      self.print_tstamp(f'Encountered error: {err}')
    
    
  def handle_exception_socket(self, client_sock):
    client_addr = self.client_info[client_sock]['address']
    self.close_client_socket(client_sock)
    self.print_tstamp(f'Closed exception socket from address {client_addr}')

  def listen_for_connections(self):
    # main function which handles connections and dispatches them to appropriate functions to be accepted, responded to, received from, etc.
    self.print_tstamp('Listening for connections...')
    self.sock.listen(10)
    try:
      while True:
        readable_socks, writable_socks, error_socks = select.select(self.client_list, self.client_list, self.client_list, self.timeout)
        # read from readable sockets
        for sock in readable_socks:
          # if the socket is server socket, accept the connection
          if sock is self.sock:
            self.accept_client_socket()
          # otherwise receive the client request
          else:
            self.receive_message(sock)
            
        if writable_socks:
          self.broadcast_message(writable_socks)
        
        for sock in error_socks:
          self.handle_exception_socket(sock)
        
    except KeyboardInterrupt:
      self.print_tstamp('Shutting down server...')
      self.shutdown_server()
      self.print_tstamp('Server shut down')
        
  def shutdown_server(self):
    for s in self.client_list:
      s.close()
      
    del self.client_list
    del self.client_info
    
    self.sock.close()
    

def run_server():  
  server = TCP_Nonblocking_Server('localhost', 8080)
  server.listen_for_connections()
  
if __name__ == '__main__':
  run_server()