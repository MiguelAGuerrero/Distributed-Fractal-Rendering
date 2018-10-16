from client import Client
from fractalworker import BadWorker

if __name__ == "__main__":
    port = 80
    c = Client("127.0.0.1", port)
    for i in range(5):
        bw = BadWorker("127.0.0.1", port, conn_id=i)
        bw.start()

    input("press any key to continue")
    c.run()