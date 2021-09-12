SELECT *
FROM room
INNER JOIN user_room
ON room.room_id = user_room.room_id
INNER JOIN users
ON users.user_id = user_room.user_id;