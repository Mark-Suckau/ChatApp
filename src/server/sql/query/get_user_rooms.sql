SELECT *
FROM users
INNER JOIN user_room
ON users.user_id = user_room.user_id
INNER JOIN room
ON room.room_id = user_room.room_id;