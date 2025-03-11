import socket
import threading


HOST = socket.gethostbyname(socket.gethostname())
PORT = 50505

nickname = input("[PROMPT] Choose a nickname: ")
if nickname == "admin":
    password = input("Enter admin password: ")

stop_thread = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode("ascii")
            if message == "NICK":
                client.send(nickname.encode("ascii"))
                next_message = client.recv(1024).decode("ascii")
                if next_message =="PASS":
                    client.send(password.encode("ascii"))

                    if client.recv(1024).decode("ascii") == "REFUSE":
                        print("Connection was refused -- Wrong Password!")
                        stop_thread = True
                elif message == "BAN":
                    print("[BANNED USER] connection refused!")
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("[ERROR] An error occurred!")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        msg = input("")
        if len(msg) <= 0:
            print("[ERROR] Message cannot be empty")
            continue
        message = f"{nickname}: {msg}"
        if message[len(nickname)+2].startswith("/"):
            if nickname == "admin":
                if message[len(nickname)+2:].startswith("/kick"):
                    client.send(f"KICK {message[len(nickname)+8:]}".encode("ascii"))
                elif message[len(nickname) + 2:].startswith("/ban"):
                        client.send(f"BAN {message[len(nickname) + 7:]}".encode("ascii"))
                else:
                    print(f"[ERROR] Command {message[len(nickname)+2:]} not recognized ")
            else:
                print("[ERROR] Commands can only be executed but the admin")
        else:
            client.send(message.encode("ascii"))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
