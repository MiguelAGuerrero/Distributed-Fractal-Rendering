import socket
import pickle

HOST = 'localhost'
PORT = 50006
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print( 'Connected by', addr)
args = [(x,x) for x in range(11)]
data_string = pickle.dumps(args)
while 1:
    data = conn.recv(4096)
    if not data: break
    conn.send(data_string)
    datas = pickle.loads(data)
    print(datas)
        #conn.send(data)
conn.close()
