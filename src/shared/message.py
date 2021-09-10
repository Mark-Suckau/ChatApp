# used to unify format of messages sent between server and client so that a single class can be changed to change formatting

class Normal_Message:
  def __init__(self, msg_content, username):
    self.contents = {"content": msg_content, "username": username}
  
  @staticmethod
  def is_normal_message(msg):
    try:
      if msg["content"] and msg["username"]:
        return True
    
    except KeyError:
      return False
      
    return False
  
  @staticmethod
  def keep_necessary_keys(msg):
    # removes possibly excess keys added by client
    new_msg = {"content": msg["content"], "username": msg["username"]}
    
    return new_msg
  
    
class Verification_Request_Message:
  def __init__(self, username, password):
    self.contents = {"username": username, "password": password}
  
  @staticmethod
  def is_verification_request_message(msg):
    try:
      if msg["username"] and msg["password"]:
        return True
      
    except KeyError:
      return False
    
    return False
  
  @staticmethod
  def keep_necessary_keys(msg):
    # removes possibly excess keys added by client
    new_msg = {"username": msg["username"], "password": msg["password"]}
    
    return new_msg


class Verification_Response_Message:
  def __init__(self, is_verified):
    self.contents = {"verified": is_verified}
  
  @staticmethod
  def is_verification_response_message(msg):
    try:
      if msg["verified"]:
        return True
    
    except KeyError:
      return False
    
    return False
  
  @staticmethod
  def keep_necessary_keys(msg):
    # removes possibly excess keys added by client
    new_msg = {"valid": msg["valid"]}
    
    return new_msg