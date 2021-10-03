import psycopg2

# NOTE: psycopg2 requires variables be passed into queries in tuples when using cursor.execute(),
# with just one variable it is required to add a comma at the end to convert to tuple instead of keeping it as a string
# ex. cursor.execute('SELECT * FROM users WHERE user_name = %s;', (user_name,))

class DB_Connector:
  def __init__(self, host, port, dbname, username, password):
    self.conn = psycopg2.connect(host=host,
                                 port=port, 
                                 dbname=dbname, 
                                 user=username,
                                 password=password)
    
    self.cursor = self.conn.cursor()
  
  def create_tables_if_needed(self):
    # creates tables if they dont already exists using schema from sql/create_tables
    self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                          user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                          user_name VARCHAR(255) NOT NULL,
                          user_password_hash VARCHAR(255) NOT NULL
                        );

                        CREATE TABLE IF NOT EXISTS room(
                          room_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                          room_name VARCHAR(255) NOT NULL
                        );

                        CREATE TABLE IF NOT EXISTS user_room(
                          user_room_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                          
                          room_id INT,
                          CONSTRAINT fk_room
                            FOREIGN KEY(room_id)
                            REFERENCES room(room_id)
                          ON DELETE CASCADE,
                          
                          user_id INT,
                          CONSTRAINT fk_users
                            FOREIGN KEY(user_id) 
                            REFERENCES users(user_id)
                            ON DELETE CASCADE
                        );

                        CREATE TABLE IF NOT EXISTS message(
                          message_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                          create_date DATE,
                          message_body TEXT,
                          
                          creator_id INT,
                          CONSTRAINT fk_users
                            FOREIGN KEY(creator_id)
                            REFERENCES users(user_id)
                            ON DELETE CASCADE,
                          
                          room_id INT,
                          CONSTRAINT fk_room
                            FOREIGN KEY(room_id)
                            REFERENCES room(room_id)
                            ON DELETE CASCADE
                        );
                        ''')
    self.conn.commit()
    
  def insert_user(self, user_name, user_password_hash):
    self.cursor.execute('''SELECT * FROM users WHERE user_name = %s;''', (user_name,))
    duplicates = self.cursor.fetchall()

    if duplicates:
      raise Exception('User with supplied user_name already exists')
      
    output = self.cursor.execute('''INSERT INTO users (user_name, user_password_hash)
                        VALUES (%s, %s);''', (user_name, user_password_hash))
    self.conn.commit()
    return output
    
  def insert_room(self, room_name):
    self.cursor.execute('''SELECT * FROM room WHERE room_name = %s;''', (room_name,))
    duplicates = self.cursor.fetchall()
    
    if duplicates:
      raise Exception('Room with supplied room_name already exists')
    
    output = self.cursor.execute('''INSERT INTO room (room_name)
                        VALUES (%s);''', (room_name,))
    self.conn.commit()
    return output
      
  def insert_message(self, create_date, message_body, creator_id, room_id):
    # inserts a message into "message" table
    # doesn't need to check for duplicates since clients could technically send two identical messages without it being a bug
    output = self.cursor.execute('''INSERT INTO message (create_date, message_body, creator_id, room_id) 
                        VALUES (%d, %-s, %s, %s);''', 
                        create_date, message_body, creator_id, room_id)
    self.conn.commit()
    return output
    
  def add_user_to_room(self, user_id, room_id):
    # adds a given user to a given room
    # checks for duplicates since a client cant be apart of a room twice
    self.cursor.execute('''SELECT * FROM user_room WHERE user_id = %s AND room_id = %s;''', (user_id, room_id))
    duplicates = self.cursor.fetchall()
    
    if duplicates:
      raise Exception('User is already appart of supplied room')
    
    output = self.cursor.execute('''INSERT INTO user_room (user_id, room_id)
                        VALUES (%s, %s);''', (user_id, room_id))
    self.conn.commit()
    return output
    
  def remove_user_from_room(self, user_id, room_id):
    # removes a given user from a given room
    output = self.cursor.execute('''DELETE FROM user_room
                        WHERE user_id = %s
                        AND room_id = %s;''', (user_id, room_id))
    self.conn.commit()
    return output
    
  def get_user_rooms(self, user_id):
    # returns all rooms a given user is apart of (used to determine: if a user is allowed to read/write messages to this room; gives client data on what rooms to display on gui when user logs on)
    user_rooms = self.cursor.execute('''SELECT *
                                    FROM user_room
                                    INNER JOIN room
                                    ON user_room.room_id = room.room_id
                                    WHERE user_room.user_id = %s;''', (user_id,))
    return user_rooms
  
  def get_room_users(self, room_id):
    # returns all users in a given room
    room_users = self.cursor.execute('''SELECT *
                                    FROM room
                                    WHERE room_id = %s;''', (room_id,))
    return room_users
  
  def get_room_messages(self, room_id, start_date, end_date):
    # returns all messages in a room in a specified range of dates
    room_messages = self.cursor.execute('''SELECT *
                                       FROM room
                                       INNER JOIN message
                                       ON room.room_id = message.room_id
                                       WHERE NOT (create_date < %d OR
                                       create_date > %d) AND
                                       message.room_id = %s;''', 
                                       (start_date, end_date, room_id))
    return room_messages
  
  def get_user_messages(self, user_id, start_date, end_date):
    # returns all messages a given user has received in a specified date range from all rooms the user is apart of
    user_messages = self.cursor.execute('''SELECT room.*, message.*
                                  FROM users
                                  INNER JOIN user_room
                                  ON users.user_id = user_room.user_id
                                  INNER JOIN room
                                  ON room.room_id = user_room.room_id
                                  INNER JOIN message
                                  ON message.room_id = room.room_id
                                  WHERE NOT (message.create_date < %d 
                                  OR message.create_date > %d) 
                                  AND users.user_id = 1;''', (start_date, end_date, user_id))
    return user_messages
  
  def get_user_room_messages(self, user_id, room_id, start_date, end_date):
    # returns messages in a specified date range of a specific user in a specific room
    # date range, 1 user, 1 room
    messages = self.cursor.execute('''SELECT room.*, message.*
                                  FROM users
                                  INNER JOIN user_room
                                  ON users.user_id = user_room.user_id
                                  INNER JOIN room
                                  ON room.room_id = user_room.room_id
                                  INNER JOIN message
                                  ON message.room_id = room.room_id
                                  WHERE NOT (message.create_date < %d 
                                  OR message.create_date > %d) 
                                  AND message.room_id = %s
                                  AND users.user_id = 1;''', (start_date, end_date, room_id, user_id))
    return messages
    
  def shutdown(self):
    self.cursor.close()
    self.conn.close()