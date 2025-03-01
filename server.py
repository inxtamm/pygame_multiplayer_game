import socket
from _thread import *

import pickle

server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")
players = {}


def threaded_client(conn, player_index):
    conn.send(pickle.dumps(players))
    reply = ""
    players[player_index] = pickle.loads(conn.recv(3072))
    #conn.send(pickle.dumps(players))
    while True:
        try:
            data = pickle.loads(conn.recv(3072))
            players[player_index] = data

            if not data:
                print("Disconnected")
                break
            else:
                
                reply = players.copy()
                reply.pop(player_index)
                #print("Received: ", data)
                #print("Sending : ", reply)
            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    players.pop(player_index)
    print(players)
    conn.close()

_id = 1

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    
    start_new_thread(threaded_client, (conn, _id))
    _id += 1

