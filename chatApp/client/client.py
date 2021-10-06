import socket, threading, traceback, queue, json
from datetime import datetime
from chatapp.shared import message
from chatapp.shared import exception


class TCP_Nonblocking_Client:
  def __init__(self, host, port, username, password, verbose_output=True):
    self.host = host
    self.port = port
    self.sock = None
    self.format = 'utf-8'
    
    self.verbose_output = verbose_output
    
    self.username = username
    self.password = password
    
    self.received_messages = queue.Queue()
    
  def print_tstamp(self, msg):
    if self.verbose_output:
      current_time = datetime.now().strftime("%Y-%M-%d %H:%M:%S")
      print(f'[{current_time}] [CLIENT] {msg}')
  
  def send_message(self, msg: str):
    msg = json.dumps(msg) # convert python dict to json string
    msg = msg.encode(self.format) # convert json string to utf-8 bytes
    send_info = self.sock.send(msg) # send json string encoded with utf-8
    
    return send_info
  
  def receive_message(self, receive_bytes: int):
    # blocks code execution until a message is received from socket connection
    try:
      msg = self.sock.recv(receive_bytes)
      msg = msg.decode(self.format)
      msg = json.loads(msg)
      
      return msg
    except json.JSONDecodeError:
      # NOTE will raise this exception when msg is empty string (could be handled by 
      # doing msg = '' however this may cause other more serious times this exception 
      # is raised to be ignored, such as when the message is too long and 
      # causes an unterminated string)
      raise exception.MessageError('Message could not be decoded by json decoder (message possibly empty)')
  
  def send_text_message(self, msg_body: str):
    try:
      if msg_body:
        msg = message.create_message(message.config_msg_types['CLIENT_TEXT'], msg_body=msg_body)
        
        send_info = self.send_message(msg)
        
        self.print_tstamp(f'Sent {send_info} bytes to the server')
    
    except OSError as err:
      raise exception.ConnectionError(f'Encountered OSError: {err}')
    
  def create_socket(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp(f'Socket created')

  def establish_connection(self):
    """Merely establishes connection with server (does not verify, thus no interactions
    other than verifying or signing up can be done with server)"""
    
    try:
      self.print_tstamp(f'Connecting to server [{self.host}] on port [{self.port}]...')
      self.sock.connect((self.host, self.port))
      self.print_tstamp(f'Connected to server [{self.host}] on port [{self.port}]')
        
    #except socket.error as err:
    #  raise exception.ClientConnectionError(err)
    
    except ConnectionRefusedError as err:
      raise exception.ConnectionError('Connection was refused by server (server may not be running)')
      
    except OSError as err:
      raise exception.ConnectionError(f'Encountered OSError: {err}')

  def attempt_verification(self, username: str, password: str):
    """Attempts to verify username, password with server; returns response 
    from server or raises InvalidMessageFormattingError if response from server was incorrectly formatted"""
    
    # TODO add output to terminal if verification was successful or not
    
    self.print_tstamp('Attempting verification with server...')
    
    msg = message.create_message(message.config_msg_types['VERIFICATION_REQUEST'], username=username, password=password)
    self.send_message(msg)
    response = self.receive_message(128)

    if message.is_type(response, message.config_msg_types['VERIFICATION_RESPONSE']):
      return response
    else:
      raise exception.InvalidMessageFormattingError('Response message received from server was incorrectly formatted', response)
    
  def attempt_signup(self, username: str, password: str):
    """attempts to signup new user with username, password"""
    
    # TODO add output to terminal if signup was successful or not
    
    self.print_tstamp('Attempting signup with server...')
    
    msg = message.create_message(message.config_msg_types['SIGNUP_REQUEST'], username=username, password=password)
    self.send_message(msg)
    
    response = self.receive_message(128)
    
    if message.is_type(response, message.config_msg_types['SIGNUP_RESPONSE']):
      return response
    else:
      raise exception.InvalidMessageFormattingError('Response message received from server was incorrectly formatted', response)
    
  def shutdown_socket(self):
    self.print_tstamp('Closing socket...')
    self.sock.close()
    self.print_tstamp('Socket closed')
    
  def read_message_loop(self):
    # TODO Add checking if message from server is correctly formatted, 
    # and only display if it's a server_text message
    while True:
      try:
        # not using receive_message() method in order to allow partial receiving of the method in case of exceptions
        
        #msg = self.receive_message(1024)
        msg = self.sock.recv(1024)    # receive json string encoded with utf-8 from server
        msg = msg.decode(self.format) # decode msg from utf-8 bytes to json string
        msg = json.loads(msg)         # decode json string to python dict
          
      except socket.timeout:
        self.print_tstamp('Socket timed out, retrying receive')
        continue

      except json.JSONDecodeError:
        pass
      
      #except:
      #  self.print_tstamp('Encountered socket error:')
      #  traceback.print_exc()
      #  break
        
      if msg == '':
        # connection closed by peer, exit loop
        self.print_tstamp('Connection closed by server')
        break
      
      
      self.print_tstamp(f'Received from [SERVER]: {msg}')
      self.received_messages.put(msg)

    self.shutdown_socket()
        
        

def convert_string_bool(input_string: str, true_string: str, false_string: str, case_sensitive: bool = False) -> bool:
  if not case_sensitive:
    input_string.lower()
  
  if input_string == true_string:
    return True
  elif input_string == false_string:
    return False

def check_valid_input(input_string: str, valid_inputs: list, case_sensitive: bool = False) -> bool:
  if not case_sensitive:
    input_string.lower()
    
  for input in valid_inputs:
    if input_string == input:
      return True
  
  return False

def run_client():
  try:
    # getting inputs
    valid_inputs = ['y', 'n']
    
    while True:
      print('Give verbose output? [y/n]')
      is_verbose_output = input()
      if not check_valid_input(is_verbose_output, valid_inputs, case_sensitive=False):
        print('Invalid answer, please use either "y" for yes or "n" for no')
      else:
        break;
    is_verbose_output = convert_string_bool(is_verbose_output, valid_inputs[0], valid_inputs[1])
          
    while True:
      print('Signup before logging in? [y/n]')
      is_signup = input()
      if not check_valid_input(is_signup, valid_inputs, case_sensitive=False):
        print('Invalid answer, please use either "y" for yes or "n" for no')
      else:
        break;
    is_signup = convert_string_bool(is_signup, valid_inputs[0], valid_inputs[1])
    
    print('Username: ')
    username = input()
    print('Password: ')
    password = input()
    # /getting inputs
    
    tcp_client = TCP_Nonblocking_Client('localhost', 8080, username, password, is_verbose_output)
    tcp_client.create_socket()
    tcp_client.establish_connection()
    
    if is_signup:
      tcp_client.attempt_signup(username, password)
      
    tcp_client.attempt_verification(username, password)

    thread = threading.Thread(target=tcp_client.read_message_loop)
    thread.daemon = True
    thread.start()
    
    while True:
      message = input()
      tcp_client.send_text_message(message)
      
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  run_client()
