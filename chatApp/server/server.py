import socket, queue, select, json, traceback
from datetime import datetime
from hashlib import sha256

from chatapp.shared import exception, message
from chatapp.server import db_connector as db_conn
from chatapp.server import load_server_config

server_config = load_server_config.load_config()
server_config_python_server = server_config['python_server']
server_config_postgres_server = server_config['postgres_server']

class TCP_Nonblocking_Server:
  def __init__(self, host, port, verbose_output=True, debug_mode=False):
    self.host = host
    self.port = port
    self.sock = None
    self.timeout = 1 # timeout for select.select() in listen_for_connections()
    
    self.format = 'utf-8'
    self.verbose_output = verbose_output # determines if anything is logged to terminal
    self.debug_mode = debug_mode # determines if information like messages being sent to server are also logged to terminal
    
    self.client_list = [] # used for storing sockets
    self.client_info = {} # used for storing info about sockets (ex. address, etc.)
    self.client_messages = queue.Queue() # used for saving messages from clients before sending them to all other clients

    self.db_connector = db_conn.DB_Connector(server_config_postgres_server['ip'],
                                                  server_config_postgres_server['port'],
                                                  server_config_postgres_server['dbname'],
                                                  server_config_postgres_server['user'],
                                                  server_config_postgres_server['password'])
    
    self.configure_server()
  
  def print_tstamp(self, msg):
    if self.verbose_output:
      current_time = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
      formatted_msg = f'[{current_time}] [SERVER] {msg}'
      print(formatted_msg)

      return formatted_msg
  
  def print_tstamp_debug(self, msg):
    if self.debug_mode:
      current_time = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
      formatted_msg = f'[{current_time}] [SERVER] {msg}'
      print(formatted_msg)
      
      return formatted_msg
    
  def send_message(self, msg, client_sock):
    msg = json.dumps(msg) # convert msg from python dict to json string
    
    self.print_tstamp_debug(f'Sent message: {msg}, to client: {client_sock}')
    
    msg = msg.encode(self.format) # encoding msg from json string to utf-8 bytes
    client_sock.send(msg) # sending msg
    
  
  def receive_message(self, receive_bytes):
    msg = self.sock.recv(receive_bytes)
    msg = msg.decode(self.format)
    msg = json.loads(msg)
  
  def configure_server(self):
    self.print_tstamp('Initializing database...')
    self.db_connector.create_tables_if_needed()
    
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    self.sock.setblocking(False)
    
    self.print_tstamp(f'Binding socket to [{self.host}] on port [{self.port}]...')
    self.sock.bind((self.host, self.port))
    
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
      try:
        # not using receive_message() method so that incase of errors, the message will still be partially captured
        data_encoded = client_sock.recv(1024)
        data = data_encoded.decode(self.format)
        data = json.loads(data)


      except json.JSONDecodeError:
        # disconnect sent from client thus client must have disconnected
        self.close_client_socket(client_sock)
        return
        
      client_addr = self.client_info[client_sock]['address']
      client_verified = self.client_info[client_sock]['verified']
      
      self.print_tstamp_debug(f'received message: {data}, from: {client_addr}, client verified: {client_verified}')
      
      if not client_verified:
        if message.is_type(data, message.config_msg_types['VERIFICATION_REQUEST']):
          could_verify = self.verify_client(client_sock, data['username'], data['password'])
          
          if not could_verify:
            self.close_client_socket(client_sock)
          return
        
        elif message.is_type(data, message.config_msg_types['SIGNUP_REQUEST']):
          could_signup = self.sign_up_client(data['username'], data['password'], client_sock)
          return
          
        else:
          # closes connection if verification message is not in correct format
          self.close_client_socket(client_sock)
          return
        
      # only if client is verified:
      
      if message.is_type(data, message.config_msg_types['CLIENT_TEXT']):
        self.client_messages.put(data)
        
    except json.JSONDecodeError:
      self.print_tstamp('Encountered error: Could not decode JSON')
      self.print_tstamp_debug(traceback.format_exc())
      
      self.close_client_socket(client_sock)
      
    except OSError as err:
      self.print_tstamp(f'Encountered error: {err}')
      self.print_tstamp_debug(traceback.format_exc())
      
      self.close_client_socket(client_sock)
      
  def verify_client(self, client_sock, username, password):
    #return True or False depending on if client could be verified
    self.print_tstamp('Attempting to verify client...')
    try:
      user_info = self.db_connector.get_user_info(username)
      
    except exception.ClientLookupError:
      return False
    
    password_hash = sha256(password.encode('utf-8')).hexdigest()

    if username == user_info[1] and password_hash == user_info[2]:
      self.client_info[client_sock]['verified'] = True
      self.client_info[client_sock]['user_id'] = user_info[0]
      self.client_info[client_sock]['username'] = user_info[1]
      
      msg = message.create_message(type=message.config_msg_types['VERIFICATION_RESPONSE'], success=True, error_msg='a', status_code='a')
      self.send_message(msg, client_sock)
    
      self.print_tstamp('Successfully verified client')
      return True

    msg = message.create_message(type=message.config_msg_types['VERIFICATION_RESPONSE'], success=False, error_msg='a', status_code='a')
    self.send_message(msg, client_sock)
    
    self.print_tstamp('Failed to verify client (invalid credentials)')
    return False
  
  def sign_up_client(self, username, password, client_sock):
    # signs up new clients, client must then seperately verify to be able to use server
    # TODO send response back to clients
    
    self.print_tstamp('Attempting to sign up new user...')
    password_hash = sha256(password.encode('utf-8')).hexdigest()
    
    try:
      self.db_connector.insert_user(username, password_hash)
      
      msg = message.create_message(type=message.config_msg_types['SIGNUP_RESPONSE'],
                                   success=True, error_msg='', status_code='')
      self.send_message(msg, client_sock)
          
      self.print_tstamp('Successfully signed up new user')
      return True
    
    except exception.DuplicateUserError as err:
      msg = message.create_message(type=message.config_msg_types['SIGNUP_RESPONSE'], 
                                   success=False, error_msg='', status_code='')
      self.send_message(msg, client_sock)
          
      self.print_tstamp('Failed to sign up new user')
      self.print_tstamp(err)
      self.print_tstamp_debug(traceback.format_exc())
      return False
  
  def broadcast_message(self, client_socks):
    # broadcasts messages sent from other clients to other clients
    # takes a list of client sockets to broadcast message to
    
    # NOTE BUG (not really a bug, just a potential one) 
    # queue.Empty exception will be raised if the client_messages 
    # queue is empty since get_nowait() is being used (in theory this should never happen, 
    # since messages are only broadcast when they are received)
    try:
      msg = self.client_messages.get_nowait() # get message sent from a client
      self.print_tstamp_debug(f'Broadcasting {msg} to {len(client_socks)} clients')
      msg = json.dumps(msg)          # convert from python dict to json string
      msg = msg.encode(self.format)  # encode from json string to utf-8 bytes

      for s in client_socks:
        s.send(msg)
    
    except queue.Empty:
      pass
    
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
          else:
            # otherwise receive the client request
            self.receive_message(sock)
            
        if writable_socks:
          # BUG server is attempting to broadcast messages even when none are saved in client_messages queue
          # (meaning server isnt properly saving client_text messages from clients)
          self.broadcast_message(writable_socks)
        
        for sock in error_socks:
          self.handle_exception_socket(sock)
        
    except KeyboardInterrupt:
      self.print_tstamp('Shutting down server...')
      self.shutdown_server()
      self.print_tstamp('Server shut down')
      self.print_tstamp_debug(traceback.format_exc(),)
        
  def shutdown_server(self):
    for s in self.client_list:
      s.close()
      
    del self.client_list
    del self.client_info
    
    self.sock.close()
    

def run_server():
  server = TCP_Nonblocking_Server('localhost', 8080, True, False)
  server.listen_for_connections()
  
if __name__ == '__main__':
  run_server()