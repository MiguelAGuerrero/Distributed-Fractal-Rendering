class ClientWorker(Worker):
    def __init__(self, client, socket):
        super.__init__(None, None)
        self.client = client
        self.sock = socket
    
    def validate_data(self, data):
        return data
       
    #Implement this
    def start(self):
        done = False
        while not done:
            data = self.read()
            client.send(data)
        