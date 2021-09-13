# ChatApp

## Client

Once logged into server with account, the client sends a request for all rooms the user is apart to the server of and stores their ids until logged out.

### Client Online vs. Offline message receiving mode

When client is online and has the program actively running, server sends live messages from rooms via TCP connection.
When client is offline and has the program closed, it will periodically send http requests to a secondary http api running on server to receive message notifications.

## Server

1. Service for TCP connections which will be used in Online mode of clients (see above)
2. Service for HTTP requests which will be used in Offline mode of clients (see above)

### Database Connector

Used by server to manipulate Database and properly verify clients.
Server checks what rooms a client is apart of using DB Connector to:

1. Allow gui on client side to properly display rooms when a client logs on
2. Check if a client is permitted to receive/send messages from/to a given room whenever a client tries to receive/send a message
