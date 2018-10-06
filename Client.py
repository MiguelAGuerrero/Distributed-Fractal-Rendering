import threading
import socket
import pickle
from sys import argv

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.manager = ConnectionManager(self, address, port)
        
        _make_server_socket()
        
    def _maker_server_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(16)
        
    def connect(self):
        pass
    
class ConnectionManager(threading.Thread):
    def __init__(self, client, address, port):
        self.client = client
        self.connections = []
        
    def accept_connection(self):
        conn, addr = self.socket.accept()
        self.accept_connection(conn)
        
    def add_connection(self, conn):
        self.connections.append(conn)
        
    def remove_connection(self, conn):
        self.connections.remove(conn)
        
def main(args):
    port = int(args[1])
    c = Client(args[0], port)
    
if __name__ == "__main__":
    main(argv[1:])