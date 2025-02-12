import socket
import threading
import db
import menus

bind_ip = "0.0.0.0"
bind_port = 2323

db.init()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((bind_ip, bind_port))
server.listen(5)

clients = []

print(f"[+] Listening on port {bind_ip} : {bind_port}")

def is_socket_connected(sock):
    try:
        sock.send(b"", socket.MSG_DONTWAIT)
        return True
    except (BrokenPipeError, ConnectionResetError):
        return False

class user:
    def __init__(self,client_socket, addr):
        login = login_sequence(client_socket, addr,False)
        if login == True:
            self.error = True
            self.client_socket = client_socket
            self.username = ""
            self.address = addr[0]
            self.port = addr[1]
        else:
            self.client_socket = client_socket
            self.username = login
            self.address = addr[0]
            self.port = addr[1]
            self.error = False


def send(client_socket,content="",lines=1):
    sending = ("\n"*lines)+content
    client_socket.send(sending.encode())

def sendall(content="", lines=1):
    sending = ("\n" * lines) + content
    disconnected_clients = []

    for client in clients:
        try:
            client.sendall(sending.encode())
        except (BrokenPipeError, ConnectionResetError):
            print("A client disconnected.")
            disconnected_clients.append(client)
    for client in disconnected_clients:
        clients.remove(client)

def cinput(client_socket, question="",code=True,nosend=False):
    if not nosend: send(client_socket,question)
    if code:
        return client_socket.recv(1024).decode().lower().strip()
    else:
        return client_socket.recv(1024)

def command(client):
    client_socket = client.client_socket
    data = cinput(client_socket,nosend=True).split(" ")
    command = data[0].lower()
    data.pop(0)
    args = data
    match command:
        case "say":
            sendall(f"[Chat] {client.username}: {" ".join(args)}")
        case "help":
            send(client_socket,"commands: \n - help: shows this \n - say <message>: send a chat message!!")
        case _:
            send(client_socket,"Not a valid command.")

def yn(client_socket,question,default="y"):
    while True:
        recv = cinput(client_socket, f"{question} {default.upper()}/{"n" if default == "y" else "y"}: ")
        if recv in ('y', 'n', ''):
            break
        else:
            send(client_socket,"Not a valid answer.")
    if recv == '':
        return True if default.lower() == "y" else False
    else:
        return True if recv == "y" else False

def header_sequence(client_socket):
    send(client_socket,open("header.txt").read())
    send(client_socket,"Welcome to ARMUD!!", 3)


def login_sequence(client_socket, addr, ipcheck=True):
    if ipcheck:
        user = db.get_user_by_id(db.get_user_by_ip(addr[0]))
        if user != False:
            send(client_socket, "Ok logged in.")
            return user
    username = cinput(client_socket, "\nUsername:")
    if db.check_user(username):
        password = cinput(client_socket, "Password: ", False).decode()
        if db.check_password(username,password):
            if db.get_user_by_ip(addr[0]) == False:
                send(client_socket, "Adding ip connection...")
                db.add_ip_for_user(addr[0],db.get_user_id(username))
            send(client_socket, "Ok logged in.")
            return username
        else:
            send(client_socket, "Wrong password.")
            client_socket.close()
            return True
    else:
        if yn(client_socket,"New user? "):
            password = cinput(client_socket, "Password: ", False).decode()
            send(client_socket,"Creating user...")
            send(client_socket, db.create_user(username,password))
            send(client_socket, "Adding ip connection...")
            db.add_ip_for_user(addr[0],db.get_user_id(username))
            send(client_socket,"Done!")
            return username
        else:
            client_socket.close()
            return True

def handle_client(client_socket, addr):
    header_sequence(client_socket)
    client = user(client_socket, addr)
    if client.error == True:
        print(f"[+] Client {addr[0]}:{addr[1]} has an error")
        return
    clients.append(client.client_socket)
    while True:
        command(client)

def main():
    while True:
        client, addr = server.accept()
        print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,addr))
        client_handler.start()

if __name__ == "__main__":
    main()
