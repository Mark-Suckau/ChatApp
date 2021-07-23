import socket
from datetime import datetime
import queue
import select


class TCP_Nonblocking_Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.timeout = 1  # timeout for select.select() in listen_for_connections()

        self.format = 'utf-8'

        self.client_list = []  # used for storing sockets
        self.client_info = {}  # used for storing info about sockets (ex. address, etc.)
        self.client_messages = queue.Queue()  # used for saving messages from clients before sending them to all other clients

    def print_tstamp(self, msg):
        current_time = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
        print(f'[{current_time}] [SERVER] {msg}')

    def configure_server(self):
        self.print_tstamp('Creating socket...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.print_tstamp('Socket created')

        self.sock.setblocking(False)

        self.print_tstamp(f'Binding socket to {self.host} on port {self.port}')
        self.sock.bind((self.host, self.port))
        self.print_tstamp(f'Bound socket to {self.host} on port {self.port}')

        self.client_list.append(self.sock)

    def accept_client_socket(self):
        client_sock, client_addr = self.sock.accept()
        self.print_tstamp(f'Accepted new connection from {client_addr}')

        client_sock.setblocking(False)

        self.client_info[client_sock] = (client_addr)
        self.client_list.append(client_sock)

    def close_client_socket(self, client_sock):
        client_addr = self.client_info[client_sock][0]
        self.print_tstamp(f'Closing socket from address {client_addr}...')

        for s in self.client_list:
            if s == client_sock:
                self.client_list.remove(s)

        del self.client_info[client_sock]
        client_sock.close()

        self.print_tstamp(f'Socket closed from address {client_addr}')

    def receive_message(self, client_sock):
        try:
            data_encoded = client_sock.recv(1024)
            client_addr = self.client_info[client_sock][0]

            if not data_encoded:
                # no data sent from client thus client must have disconnected
                self.close_client_socket(client_sock)
                self.print_tstamp(f'{client_addr} disconnected')
                return

            data = data_encoded.decode(self.format)
            self.print_tstamp(f'{client_addr} client says: [{data}]')

            self.client_messages.put(data)

        except OSError as err:
            self.print_tstamp(f'Encountered error: {err}')
            client_addr = self.client_info[client_sock][0]

            self.close_client_socket(client_sock)

    def broadcast_message(self, client_socks):
        # takes a list of client sockets to broadcast message to
        try:
            msg = self.client_messages.get_nowait()
            msg = msg.encode(self.format)

            self.print_tstamp(f'Broadcasting message to {len(client_socks)} clients...')
            for s in client_socks:
                s.send(msg)
            self.print_tstamp(f'Broadcasted message to {len(client_socks)} clients')

        except queue.Empty:
            pass

    def send_message(self, client_sock):
        # respond to client with a request from client_info

        try:
            client_addr = self.client_info[client_sock][0]

            msg = 'This is a message from the server'
            client_sock.send(msg.encode(self.format))

            self.print_tstamp(f'Sent [{msg}] to {client_addr}')

        except KeyError:
            # handles a condition where client socket is in the writable list
            # even though it's been removed from the dictionary
            pass

        except OSError as err:
            self.print_tstamp(f'Encountered error: {err}')

    def handle_exception_socket(self, client_sock):
        client_addr = self.client_info[client_sock][0]
        self.close_client_socket(client_sock)
        self.print_tstamp(f'Closed exception socket from address {client_addr}')

    def listen_for_connections(self):
        self.print_tstamp('Listening for connections...')
        self.sock.listen(10)
        try:
            while True:
                readable_socks, writable_socks, error_socks = select.select(self.client_list, self.client_list,
                                                                            self.client_list, self.timeout)
                # read from readable sockets
                for sock in readable_socks:
                    # if the socket is server socket, accept the connection
                    if sock is self.sock:
                        self.accept_client_socket()
                    # otherwise receive the client request
                    else:
                        self.receive_message(sock)

                if writable_socks:
                    self.broadcast_message(writable_socks)

                for sock in error_socks:
                    self.handle_exception_socket(sock)

        except KeyboardInterrupt:
            self.print_tstamp('Shutting down server...')
            self.shutdown_server()
            self.print_tstamp('Server shut down')

    def shutdown_server(self):
        for s in self.client_list:
            s.close()

        del self.client_list
        del self.client_info

        self.sock.close()


def run_server():
    server = TCP_Nonblocking_Server('139.162.172.141', 8080)
    server.configure_server()
    server.listen_for_connections()


if __name__ == '__main__':
    run_server()