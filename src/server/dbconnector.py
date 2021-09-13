import psycopg2

class DB_Connector:
  def __init__(self, host, port, dbname, username, password):
    self.conn = psycopg2.connect(host=host,
                                 port=port, 
                                 dbname=dbname, 
                                 username=username, 
                                 password=password)
    
    self.cursor = self.conn.cursor()
  
  def insert_message(self, create_date, message_body, creator_id, room_id):
    # inserts a message into "message" table
    self.cursor.execute('''INSERT INTO message (create_date, message_body, creator_id, room_id) 
                        VALUES (%d, %-s, %s, %s)''', 
                        create_date, message_body, creator_id, room_id)
    self.conn.commit()
    
  def get_user_rooms(self, user_id):
    # returns all rooms a given user is apart of (used to determine: if a user is allowed to read/write messages to this room; gives client data on what rooms to display on gui when user logs on)
    user_rooms = self.cursor.execute('''SELECT room_id
                        FROM user_room
                        INNER JOIN room
                        ON user_room.room_id = room.room_id
                        WHERE user_room.user_id = %s;''', 
                        user_id)
    return user_rooms
  
  def get_messages_room(self, room_id, start_date, end_date):
    # returns all messages in a room in a specified range of dates
    
  def shutdown(self):
    self.cursor.close()
    self.conn.close()