# used to unify format of messages sent between server and client so that a single file can be changed to change formatting
import json

import os
from chatapp import path_util

# loading config using dynamically generated absolute path
shared_config_file_path = os.path.join(path_util.get_dir_path('shared'), 'shared_config.json')
with open(shared_config_file_path, 'r') as config_json:
  shared_config = json.load(config_json)
  
config_msg_types_client = shared_config['messages']['client']['message_types']
config_msg_types_server = shared_config['messages']['server']['message_types']

# list of all possible message types
message_types = [config_msg_types_client['CLIENT_TEXT'], config_msg_types_server['SERVER_TEXT'],
                 config_msg_types_client['VERIFICATION_REQUEST'], config_msg_types_server['VERIFICATION_RESPONSE']]

# required variables in a message for a given message type
types_required_fields = {
  config_msg_types_client['CLIENT_TEXT']: ['msg_body'], # text that is sent to server as text from client which will be broadcast to clients from server
  config_msg_types_server['SERVER_TEXT']: ['msg_body', 'username'], # text that is sent broadcast to all clients from server (received from a client to server as client_text)
  config_msg_types_client['VERIFICATION_REQUEST']: ['username', 'password'],
  config_msg_types_server['VERIFICATION_RESPONSE']: ['verified', 'error_msg', 'status_code']
}


def create_message(type, msg_body=None, username=None, password=None, verified=None, status_code=None, error_msg=None):
  # type used for all messages, allows receiver to properly process message
  # msg_body used by client for sending texts
  # username used by client for verification requests
  # password used by client for verification requests
  # verified used by server for verification responses
  # status_code used by server for sending status code to clients
  # error_msg used by server to describe error (describes status code if an error occured)
  
  # first adds all params, then removes params that where None (not supplied)
  msg = {'type': type, 'msg_body': msg_body, 'username': username, 'password': password, 
         'verified': verified, 'status_code': status_code, 'error_msg': error_msg}
  
  msg = remove_null_keys(msg)
  
  if valid_message(msg):
    return msg
  raise Exception('Invalid message formatting')
  
def remove_null_keys(msg):
  new_msg = {}
  for key in msg:
    if msg[key] != None:
      new_msg[key] = msg[key]
  return new_msg

def valid_message(msg):
  # checks if all required fields for the given message type are present
  try:
    for message_type in message_types:
      if msg['type'] == message_type:
        for field in types_required_fields[message_type]:
          if msg[field] != None:
            pass # checks if key exists in msg, if it doesn't, it will raise a KeyError exception
          else:
            # return false if for whatever reason the key exists, but is None
            return False 
        return True
    
  except KeyError:
    return False
  
def is_type(msg, type):
  # checks if msg is correctly formatted, then checks if message is of given type
  if valid_message(msg):
    if msg['type'] == type:
      return True
  return False