import socket
import pickle

class Network:
    def __init__(self, player):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.player = player
        self.player_index = 0
        self.addr = (self.server, self.port)
        self.connect()


    def connect(self):
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps(self.player))
            return pickle.loads(self.client.recv(3072))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            players = pickle.loads(self.client.recv(3072))
            players[self.player_index] = self.player
            return players
        except socket.error as e:
            print(e)
