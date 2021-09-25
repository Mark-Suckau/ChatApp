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

## Messages

All configurations for messages are located in the shared folder to allow the server and client to identify the kind of message they received. Each time a message is sent, a key called type is attached with the value of one the message_types from the configuration file. (ex. "type": VERIFICATION_REQUEST) the type of message it can be is dependant on whether it's the server or the client sending the message. Before any message is sent, it is first checked if it has all required information attached. This is done by a method within the Message class from message.py. (ex. if type is VERIFICATION_REQUEST, then the message instance must include self.username and self.password). Because the message.py file is the one actually checking if the required information is present for any given message type, shared/message.py must be updated along with shared/config.json each time a type is to be added.

### Note on config files

There are three total config files, one in shared folder, one in server folder and one in client folder. The one in shared contains information that isn't sensitive and can be shared with anyone. Information in the client folder, likewise can be shared with anyone, it is only useful for the client and not the server though, which is why the information in the client config file isn't also in shared. The information from the server config file contains the ips and ports for the database server and in the future other things that should only be visible to the server.
