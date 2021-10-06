### DATABASE EXCEPTIONS ###

class DataBaseError(Exception):
  """Base exception class used for errors to do with database
  
  Attributes:
    message -- explanation of error"""
    
  def __init__(self, message):
    self.message = message
    
    super().__init__(self.message)
    

class DuplicateRoomError(DataBaseError):
  """Exception raised when a room is attempted to be inserted into database but a duplicate room already exists
  
  Attributes:
    message -- explanation of error
    room_name -- name of room that was attempted to be inserted into database"""
    
  def __init__(self, message, room_name: str):
    self.message = message
    self.room_name = room_name
    
    super().__init__(self.message)
    
    
class DuplicateUserError(DataBaseError):
  """Exception raised when a user is attempted to be inserted into database but a duplicate user already exists
  
  Attributes:
    message -- explanation of error
    user_name -- name of user that was attempted to be inserted into database"""
    
  def __init__(self, message, user_name):
    self.message = message
    self.user_name = user_name
    
    super().__init__(self.message)
    

class DuplicateUserRoomError(DataBaseError):
  """Exception raised when a user is attempted to be added to a room, but that user is already in that room
  
  Attributes:
    message -- explanation of error
    user_id -- id of user that was was attempted to be added to room
    room_id -- id of room that user was attempted to be added to"""
    
  def __init__(self, message, user_id, room_id):
    self.message = message
    self.user_id = user_id
    self.room_id = room_id
    
    super().__init__(self.message)


class ClientLookupError(DataBaseError):
  """Exception raised when information no information is found for a given user that has been looked up in database
  
  Attributes:
    message -- explanation of error
    user_name -- name of user whose information was attempted to be looked up"""
    
  def __init__(self, message, user_name):
    self.message = message
    self.user_name = user_name
    
    super().__init__(self.message)


### MESSAGE EXCEPTIONS ###

class MessageError(Exception):
  """Base exception class used for errors to do with messages being sent to/from the server/client
  
  Attributes:
    message -- explanation of error"""
    
  def __init__(self, message):
    self.message = message
    
    super().__init__(self.message)
    
    
class InvalidMessageFormattingError(MessageError):
  """Exception raised when a message either 
  does not contain all required information for its message type or does not contain a message type
  
  Attributes:
    message -- explanation of error
    invalid_message -- message that was found to be incorrectly formatted and caused the exception"""
    
  def __init__(self, message, invalid_message):
    self.message = message
    self.invalid_message = invalid_message
    
    super().__init__(self.message)



### AUTHENTICATION EXCEPTIONS ###

class AuthenticationError(Exception):
  """Base exception class used for errors to do with clients authenticating
  
  Attributes:
    message -- explanation of error"""
    
  def __init__(self, message):
    self.message = message
    
    super().__init__(self.message)
  
  
class ClientLoginError(AuthenticationError):
  """Exception raised when a client could not be logged using supplied credentials
  
  Attributes:
    message -- explanation of error
    client_sock -- client socket that failed to login"""
  
  def __init__(self, message, client_sock):
    self.message = message
    self.client_sock = client_sock
    
    super().__init__(self.message)

class ClientSignupError(AuthenticationError):
  """Exception raised when a client could not be signed-up using supplied credentials
  
  Attributes:
    message -- explanation of error
    client_sock -- client socket that failed to signup"""
    
  def __init__(self, message, client_sock):
    self.message = message
    self.client_sock = client_sock
    
    super().__init__(self.message)
    


## CONNECTIONS EXCEPTIONS ##

# NOTE ConnectionError class may overwrite existing exceptions in standard python library

class ConnectionError(Exception):
  """High level exception raised for all connection errors
  
  Attributes:
    message -- explanation of error"""
  
  def __init__(self, message):
    self.message = message
    
    super().__init__(self.message)