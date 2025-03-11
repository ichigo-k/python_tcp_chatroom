import threading
import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 50505

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((HOST, PORT))

def start():
    server.listen()
    print(f"[LISTENING] server listening on port http://{HOST}:{PORT}")

start()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode("ascii").startswith("KICK"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_kick  = msg.decode("ascii")[5:]
                    print(name_to_kick)
                    kick_user(name_to_kick)
                else:
                    client.send("[UNAUTHORIZED] command was refused".encode("ascii"))
            elif msg.decode("ascii").startswith("BAN"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_ban = msg.decode("ascii")[4:]
                    kick_user(name_to_ban)
                    with open("bans.txt", "a") as f :
                        f.write(f"{name_to_ban}\n")
                    broadcast(f"[INFO] {name_to_ban} was banned".encode("ascii"))
                else:
                    client.send("[UNAUTHORIZED] command was refused".encode("ascii"))
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()

            nickname = nicknames[index]
            broadcast(f"[INFO] {nickname} left the chat!".encode("ascii"))
            nicknames.remove(nickname)

            break

def receive():
    while True:
        client, address = server.accept()
        print(f"[NEW CONNECTION] {str(address)} connected!")

        client.send("NICK".encode("ascii"))
        nickname = client.recv(1024).decode("ascii")
        with open("bans.txt", "r") as f:
            bans = f.readlines()
        if nickname+"\n" in bans:
            client.send("BAN".encode("ascii"))
            client.close()
            continue

        if nickname == "admin":
            client.send("PASS".encode("ascii"))
            password = client.recv(1024).decode("ascii")

            if password != "password":
                client.send("REFUSE".encode("ascii"))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        broadcast(f"[INFO] {nickname} joined the chat".encode("ascii"))
        client.send(f"Welcome {nickname}".encode("ascii"))

        thread = threading.Thread(target = handle, args = (client,))
        thread.start()


def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked out by admin!'.encode("ascii"))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f"[INFO] {name} was kicked out by admin".encode("ascii"))


receive()