CREATE TABLE IF NOT EXISTS users(
  user_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_name VARCHAR(255) NOT NULL
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
