import threading
from MandelZoom import mandelbrot
from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET,SO_REUSEADDR, timeout
import pickle


# Need Pickle to send object over stream/ connection
class Worker(threading.Thread):
    def __init__(self, IP, port):
        super().__init__()
        self.threadName = threading.Thread.name
        self.IP_Addr =IP
        self.port = port
        self.results = [x/2 for x in range(10)]
        self.start()

    def compute(self, complex_num, integer):
        # Make sure this is return an Array of Byte
        self.results.append(mandelbrot(complex_num, integer))

    def connect2client(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        addr = self.IP_Addr, self.port
        self.sock.settimeout(50)
        try:
            #Connection Request and Sending Data over Connection
            self.sock.connect(addr)
            arr = 'Worker'
            data_string = pickle.dumps(arr)
            self.sock.send(data_string)

            #Receiving Data and Sending Computed Data Values
            data = self.sock.recv(4096)
            data_arr = pickle.loads(data)
            print('Received from Server ', data_arr)

            # for elem in data_arr:
            #     print(type(elem), elem)
            if data_arr:
                for elem in data_arr:
                    self.compute(elem[0], elem[1])

            data_string = pickle.dumps(self.results)
            print(self.results)
            self.sock.send(data_string)

            #self.sock.close()
            #


            #Showing Data and Data Type to understand how pickle works

        except Exception as e:
            print(e)
    # def listen(self):
    #     HOST = 'localhost'
    #     PORT = 50007
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.bind((HOST, PORT))
    #     s.listen(1)
    #     conn, addr = s.accept()
    #     print('Connected by', addr)
    #     while 1:
    #         data = conn.recv(4096)
    #         if not data: break
    #         print(type(data))
    #         conn.send(data)
    #     conn.close()

    def start(self):
        self.connect2client()
        while(input() != "q"):
            continue

if __name__ == '__main__':
    w = Worker(IP='127.0.0.1', port=50006)