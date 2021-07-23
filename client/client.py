import socket, threading, traceback, queue, json, os, sys
from datetime import datetime

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
  
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)
from universal import message


class TCP_Nonblocking_Client:
  def __init__(self, host, port, username, password):
    self.host = host
    self.port = port
    self.sock = None
    self.format = 'utf-8'
    
    self.username = username
    self.password = password
    
    self.received_messages = queue.Queue()
    self.stop_client = False
    
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

      self.print_tstamp('Verifying username and password with server...')
      
      verified = self.send_verification(self.username, self.password)
      if verified:
        self.print_tstamp('Username and password verified with server')
        return True
      else:
        self.print_tstamp('Username and/or password could not be verified by server')
        self.shutdown_socket()
        
        return False # halts execution of top level function calling this function
      
    except socket.error:
      self.stop_client = True
      
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
      return False # halts execution of top level function calling this function
      
    except OSError as err:
      self.stop_client = True
      
      self.print_tstamp('Encountered an error:')
      traceback.print_exc()
      
      return False # halts execution of top level function calling this function
      
  def send_verification(self, username, password):
    msg = message.Verification_Request_Message(username, password)
    msg = json.dumps(msg.contents)
    msg = msg.encode(self.format)
    
    self.sock.send(msg)
    response = self.sock.recv(64)
    response = response.decode(self.format)
    response = json.loads(response)
    
    if message.Verification_Response_Message.is_verification_response_message(response):
      return response["verified"] # returns true or false based on if the server could verify the request or not
    
    return False
    
  def send_message(self, msg):
    try:
      if msg:
        msg = message.Normal_Message(msg, self.username)
        msg = json.dumps(msg.contents)  # convert python dict to json string
        msg = msg.encode(self.format)   # convert json string to utf-8 bytes
        send_info = self.sock.send(msg) # send json string encoded with utf-8
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
    if not self.connect_to_server():
      return
    
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
    
def run_socket():
  try:
    print('Username: ')
    username = input()
    print('Password: ')
    password = input()
    
    tcp_client = TCP_Nonblocking_Client('localhost', 8080, username, password)
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
