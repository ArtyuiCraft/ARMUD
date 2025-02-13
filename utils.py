import db
import socket

db.init()

clients = []
parties = []

def is_socket_connected(sock):
    try:
        sock.send(b"", socket.MSG_DONTWAIT)
        return True
    except (BrokenPipeError, ConnectionResetError):
        return False

class Party:
    def __init__(self, creator, id):
        self.creator = creator
        self.joinedpeople = []
        self.partyid = id

    def addperson(self, name):
        self.joinedpeople.append(name)

    def removeperson(self, name):
        self.joinedpeople.remove(name)

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
            self.joinedparty = None


def send(client_socket,content="",lines=1):
    sending = ("\n"*lines)+content
    client_socket.send(sending.encode())

def sendall(content="", lines=1):
    sending = ("\n" * lines) + content
    disconnected_clients = []

    for client in clients:
        try:
            client.client_socket.sendall(sending.encode())
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

def get_client(username):
    return next((client for client in clients if client.username == username), None)

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
        case "createparty":
            if client.joinedparty == None:
                parties.append(Party(client.username,len(parties)))
                client.joinedparty = parties[-1]
                send(client_socket,f"Party {len(parties)-1} created")
            else:
                send(client_socket,f"Leave your current party first using leaveparty")
        case "partyrequest":
            if args[0] == "all":
                args.pop(0)
                message = " ".join(args)
                sendall(f"[PartyRequest] {client.username}: {message} Run 'joinparty {len(parties) - 1}' to join!" )
            else:
                checkclient = get_client(args[0])
                if checkclient != None:
                    send(checkclient.client_socket,f"{client.username} sent you a request to join his party run joinparty {client.joinedparty.partyid}")
                else:
                    send(client_socket,f"No user found with the username: {args[0]}")
        case "joinparty":
            if client.joinedparty == None:
                id = int(args[0])
                parties[id].addperson(client)
                client.joinedparty = parties[id]
                send(client_socket,f"Joined party {id}")
            else:
                send(client_socket,"Leave your current party first using leaveparty")
        case "leaveparty":
            if client.joinedparty == None:
                send(client_socket,"No party to leave")
            else:
                for i in client.joinedparty.joinedpeople:
                    send(i.client_socket,f"{client.username} left your party.")
                client.joinedparty.removeperson(client.username)
                client.joinedparty = None
        case "chat":
            if args[0] not in ("global","party"):
                send(client_socket,"Choose global or party")
            else:
                user.chat
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

