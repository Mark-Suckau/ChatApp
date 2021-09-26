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

### Message creation parameters

_type_: used for all messages, allows receiver to properly process message
_username_: used by client for verification requests
_password_: used by client for verification requests
_verified_: used by server for verification responses
_status_code_: used by server for sending status code to clients
_error_msg_: used by server to describe error (describes status code if an error occured)

### Message Types

**SERVER**
_SERVER_TEXT_: Normal text message that is forwarded by the server to all clients (who should receive it), (server received a CLIENT*TEXT message), this variant requires the username of the client that sent it to the server
\_VERIFICATION_RESPONSE*: Response to a VERIFICATION_REQUEST made by a client

**CLIENT**
_CLIENT_TEXT_: Normal text message that is sent to the server from one client, this variant does not require a username
_VERIFICATION_REQUEST_: Request to the server to log in as a given user

#### Note on TEXT types

Both TEXT message type variants are meant to be used for clients sending messages to one another. The two different SERVER_TEXT and CLIENT_TEXT message types are required because the SERVER_TEXT needs to include from what client the message is, whereas it would be redundant for the client to send their username along with each message they send, since they verified at the beginning of their session and the server should have their username in memory or be able to grab it from a database. In addition to that, it would be very easy for the client to lie and send a fake username.

## Note on config files

There are three total config files, one in shared folder, one in server folder and one in client folder. The one in shared contains information that isn't sensitive and can be shared with anyone. Information in the client folder, likewise can be shared with anyone, it is only useful for the client and not the server though, which is why the information in the client config file isn't also in shared. The information from the server config file contains the ips and ports for the database server and in the future other things that should only be visible to the server.

## Executing Files

Files must be executed from terminal using python -m packagename.package.module instead of directly using python modulename. When doing this you must also be in the directory directly above the top level package. Also note that the actual top level package name is chatapp not ChatApp.

### EXAMPLES

_DIR_: Path/to/repository/ChatApp,
_CMD to start server_: python -m chatapp.server.server
_CMD to start client (terminal)_: python -m chatapp.client.client
_CMD to start client (gui)_: python -m chatapp.client.ui.run_ui

Execution of any file can be halted from the terminal using CTRL^C
