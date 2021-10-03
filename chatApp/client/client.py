import socket, threading, traceback, queue, json
from datetime import datetime
from chatapp.shared import message


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
  
  def create_socket(self):
    self.print_tstamp('Creating socket...')
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.print_tstamp(f'Socket created')

  def connect_to_server(self):
    # returns True/False if successfully connected, along with message to be displayed by ui incase something goes wrong
    try:
      self.print_tstamp(f'Connecting to server [{self.host}] on port [{self.port}]...')
      self.sock.connect((self.host, self.port))
      self.print_tstamp(f'Connected to server [{self.host}] on port [{self.port}]')

      self.print_tstamp('Verifying username and password with server...')
      
      verification_response = self.send_verification(self.username, self.password)
      if verification_response['verified']:
        self.print_tstamp('Username and password verified with server')
        
        return True, ''
        
      else:
        self.print_tstamp('Username and/or password could not be verified by server')
        self.shutdown_socket()
        
        return False, 'Username and/or password could not be verified by server'  

    except socket.error:
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
      return False, 'Encountered a socket error'
      
    except OSError as err:
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
      return False, 'Encountered an OSError'
      
  def send_verification(self, username, password):
    # attempts to verify username, password with server; returns response from server or false if response from server was incorrectly formatted
    msg = message.create_message(message.config_msg_types['VERIFICATION_REQUEST'], username=username, password=password)
    msg = json.dumps(msg)
    msg = msg.encode(self.format)
    
    self.sock.send(msg)
    response = self.sock.recv(128)
    response = response.decode(self.format)
    response = json.loads(response)
    
    if message.is_type(response, message.config_msg_types['VERIFICATION_RESPONSE']):
      return response
    
    return False
    
  def send_message(self, msg):
    try:
      if msg:
        msg = message.create_message(message.config_msg_types['CLIENT_TEXT'], msg_body=msg)
        msg = json.dumps(msg)  # convert python dict to json string
        msg = msg.encode(self.format)   # convert json string to utf-8 bytes
        send_info = self.sock.send(msg) # send json string encoded with utf-8
        self.print_tstamp(f'Sent {send_info} bytes to the server')
        return True, ''

    except OSError as err:
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      return False, 'Encountered an OSError'
  
  def shutdown_socket(self):
    self.print_tstamp('Closing socket...')
    self.sock.close()
    self.print_tstamp('Socket closed')
    
  def read_message_loop(self):
    # if function returns value then error has occured and interaction should be halted
    while True:
      try:
        msg = self.sock.recv(1024)    # receive json string encoded with utf-8 from server
        msg = msg.decode(self.format) # decode msg from utf-8 bytes to json string
        msg = json.loads(msg)         # decode json string to python dict
          
      except socket.timeout:
        self.print_tstamp('Socket timed out, retrying receive')
        continue

      except json.JSONDecodeError:
        self.print_tstamp('Encountered error: ')
        traceback.print_exc()
      
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
    
def run_client():
  try:
    print('Username: ')
    username = input()
    print('Password: ')
    password = input()
    
    tcp_client = TCP_Nonblocking_Client('localhost', 8080, username, password, True)
    tcp_client.create_socket()
    tcp_client.connect_to_server()

    thread = threading.Thread(target=tcp_client.read_message_loop)
    thread.daemon = True
    thread.start()
    
    while True:
      message = input()
      tcp_client.send_message(message)
      
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  run_client()
