# used to unify format of messages sent between server and client so that a single file can be changed to change formatting
import json

with open('shared_config.json', 'r') as config_json:
  shared_config = json.load(config_json)
  
config_msg_types_client = shared_config["messages"]["client"]["message_types"]
config_msg_types_server = shared_config["messages"]["server"]["message_types"]

# list of all possible message types
message_types = [config_msg_types_client["TEXT"], config_msg_types_client["VERIFICATION_REQUEST"],
                 config_msg_types_server["VERIFICATION_RESPONSE"]]

# required variables in a message for a given message type
types_required_fields = {
  config_msg_types_client["TEXT"]: ["msg_body"],
  config_msg_types_client["VERIFICATION_REQUEST"]: ["username", "password"],
  config_msg_types_server["VERIFICATION_RESPONSE"]: ["verified", "error_msg", "status_code"]
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
  msg = {"type": type, "msg_body": msg_body, "username": username, "password": password, 
         "verified": verified, "status_code": status_code, "error_msg": error_msg}
  
  msg = remove_null_keys(msg)
  
  if type_valid(msg):
    return msg
  
def remove_null_keys(msg):
  for key, value in msg:
    if value == None:
      del msg[key]

def type_valid(msg):
  # checks if all required fields for the given message type are present
  try:
    for message_type in message_types:
      if msg.type == message_type:
        for field in types_required_fields[message_type]:
          if msg[field] != None:
            pass # checks if key exists in msg, if it doesn't, it will raise a KeyError exception
          else:
            # return false if for whatever reason the key exists, but is None
            return False 
        return True
    
  except KeyError:
    return False