from client import Client
import sys
import socket
from numpcanvas import NUMPCanvas
from msg import RSLTMessage
import struct
import numpy as np
import threading

'''
clientwrappergui provided a wrapped client for the Java GUI. By building ontop of the client, it is possible to 
configure it and submit fractal requests. The wrapped client listens for a connection from the Java GUI so that
it may receive configurations. As of now, there is no generalization for what configurations can be provided,
so it is hard-coded that the client accepts:
    Image Width
    Image Height
    X-Min
    X-Max
    Y-Min
    Y-Max
    Iterations
    Fractal type
'''

def main(args):
    if len(args) < 2:
        usage()

    #Accept the connection from the GUI
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gui_addr, gui_port = "127.0.0.1", 1000
    addr = gui_addr, gui_port
    sock.bind(addr)
    sock.listen(1)

    conn, acpt = sock.accept()

    #Create the client
    address = args[0]
    port = int(args[1])
    c = Client(address, port)
    done = False

    while not done:
        try:
            #Blocks until the GUI sends a configuration to this wrapper
            config = read_config(conn)

            #Print the config for debugging purposes
            print("Config:", config)

            #Create a new canvas with the new size, since there's no clean way to dynamically
            #change numpy arrays, which SocketCanvas uses
            c.set_canvas(SocketCanvas(conn, config["img_width"], config["img_height"]))
            for param in config:
                setattr(c, param, config[param])

            #Uses the current configuration of the client to determine the output fractal
            c.run()

        except Exception as e:
            print(e)
            done = True

def usage():
    pass

def read_config(sock):
    ''''
        As of now, this wrapped client module only expects one message to be sent to it: A CONFG (Configuration)
        message. Every call to read_config assumes that the incomming bytes can be interpreted such that:
            1 - 4   : CNFG (Str)
            5 - 8   : Data Length (int)
            9 - 12  : x-min (float)
            13 - 16 : x-max (float)
            17 - 20 : y-min (float)
            21 - 24 : y-max (float)
            25 - 28 : iterations (int)
            29+     : Fractal (String)
    '''
    type = sock.recv(4)
    data_len = int.from_bytes(sock.recv(4), sys.byteorder)
    done_reading = False
    bytes_read = 0
    data_buf = bytearray()
    packet_buf = bytearray(data_len)


    #Keep reading until the all the byes of the message
    #Have been read
    while not done_reading:
        read = sock.recv_into(packet_buf)
        bytes_read += read
        # print('     bytes read', bytes_read)
        data_buf.extend(packet_buf[:read])
        sys.stdout.flush()
        if bytes_read == data_len:
            done_reading = True

    #Lots and lots of parsing for the config file
    img_width = int.from_bytes(data_buf[:4], sys.byteorder)
    img_height = int.from_bytes(data_buf[4:8], sys.byteorder)
    x_min = bytes_to_float(data_buf, 8, 12)
    x_max = bytes_to_float(data_buf, 12, 16)
    y_min = bytes_to_float(data_buf, 16, 20)
    y_max = bytes_to_float(data_buf, 20, 24)
    itrs = int.from_bytes(data_buf[24:28], sys.byteorder)
    fractal = data_buf[28:].decode("ascii")

    #This config dict's keys MUST match up with the client's field attributes
    #The reason is because setattr() is used to automatically assign
    #the config values to the client
    config = {"img_width": img_width
            , "img_height": img_height
            , "xmin": x_min
            , "xmax": x_max
            , "ymin": y_min
            , "ymax": y_max
            , "maxitr": itrs
            , "fractal": fractal}

    return config


class SocketCanvas(NUMPCanvas):
    def __init__(self, sock, width, height):
        super().__init__(width, height)
        self.sock = sock

    def render(self):
        int_bytes = []
        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                int_bytes.append(self.data[i, j].item().to_bytes(4, sys.byteorder, signed=True))

        msg = b"".join([b"RSLT",
                       (4 * len(int_bytes) + 8).to_bytes(4, sys.byteorder, signed=True),
                       *int_bytes,
                       self.data.shape[0].to_bytes(4, sys.byteorder, signed=True),
                       self.data.shape[1].to_bytes(4, sys.byteorder, signed=True)])

        self.sock.sendall(msg)

def bytes_to_float(buf, start, end):
    return struct.unpack('f', buf[start:end])[0]

if __name__ == "__main__":
    main(sys.argv[1:])