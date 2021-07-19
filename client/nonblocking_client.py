import socket
from datetime import datetime

class TCP_Nonblocking_Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.format = 'utf-8'

    def print_tstamp(self, msg):
      current_time = datetime.now().strftime("%Y-%M-%d %H:%M:%S")
      print(f'[{current_time}] [CLIENT] {msg}')
    
    def create_socket(self):
      self.print_tstamp('Creating socket...')
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.print_tstamp('Socket created')

      #self.sock.setblocking(False)
      
    def interact_with_server(self):

        try:
          # connect to server
            self.print_tstamp(f'Connecting to server [{self.host}] on port [{self.port}]...')
            self.sock.connect((self.host, self.port))
            msg = 'Hello this was sent from a client'
          
          #while True:
            # try sending the data to the server
            send_info = self.sock.send(msg.encode(self.format))

            # see how much data was actually sent
            self.print_tstamp(f'Sent {send_info} bytes to the server')
            
            response = self.sock.recv(1024)
            print(response)

        except OSError as err:
          self.print_tstamp(f'Encountered an error: {err}')
            
        except KeyboardInterrupt:
          # allows the while loop to be exited
          pass

        finally:
          self.print_tstamp('Closing socket...')
          self.sock.close()
          self.print_tstamp('Socket closed')

def main():
    tcp_client = TCP_Nonblocking_Client('localhost', 8080)
    tcp_client.create_socket()
    tcp_client.interact_with_server()

if __name__ == '__main__':
    main()
