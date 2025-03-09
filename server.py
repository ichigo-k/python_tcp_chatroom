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
            message = client.recv(1024)
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
        nicknames.append(nickname)
        clients.append(client)

        broadcast(f"[INFO] {nickname} joined the chat".encode("ascii"))
        client.send(f"Welcome {nickname}".encode("ascii"))

        thread = threading.Thread(target = handle, args = (client,))
        thread.start()



receive()