import db
import socket
import re
import json
import pickle

db.init()

clients = []
parties = []

# TELNET
IAC  = bytes([255])
SB   = bytes([250])
GMCP = bytes([201])
SE   = bytes([240])
WILL = bytes([251])

class Array3D:
    def __init__(self, x, y, z, c=""):
        self.lst = [[[ c for _ in range(x)] for _ in range(y)] for _ in range(z)]

    def list(self):
        return self.lst

    def str(self,z):
        tmp = ""
        for y in self.lst[z]:
            for x in y:
                tmp += str(x)
            tmp += "\n"
        return tmp

    def set(self,x,y,z,c=" "):
        self.lst[z][y][x] = c

    def __repr__(self):
        return self.str(0)

class Array2D:
    def __init__(self, x, y, c=""):
        self.lst = [[ c for _ in range(x)] for _ in range(y)]

    def list(self):
        return self.lst

    def str(self):
        tmp = ""
        for y in self.lst:
            for x in y:
                tmp += str(x)
            tmp += "\n"
        return tmp

    def set(self,x,y,c=" "):
        self.lst[y][x] = c

    def __repr__(self):
        return self.str()

class Room:
    def __init__(self,x,y):
        self.array = Array2D(self,x,y)
        self.exits = {}

    def str(self):
        return self.array.str()

    def set(self,x,y,c=" "):
        self.array.lst[y][x] = c

    def __repr__(self):
        return self.str()

class World:
    def __init__(self):
        self.world: Array3D = Array3D(100,100,10)

    def save(self, filename="world.pkl"):
        with open(filename, "wb") as file:
            pickle.dump(self, file)
        print(f"World saved to {filename}")

    @staticmethod
    def load(filename="world.pkl"):
        with open(filename, "rb") as file:
            world = pickle.load(file)
        print(f"World loaded from {filename}")
        return world

def is_socket_connected(sock):
    try:
        sock.send(b"", socket.MSG_DONTWAIT)
        return True
    except (BrokenPipeError, ConnectionResetError):
        return False

def parse_telnet_data(data: str):
    clean_data = re.sub(r'\xff[\xfd\xfa\xf0]', '', data)

    entries = re.findall(r'([\w.]+)\s*(\{.*?\}|\[.*?\]|$)', clean_data)

    parsed_data = {}
    for key, value in entries:
        try:
            parsed_data[key] = json.loads(value)
        except json.JSONDecodeError:
            parsed_data[key] = value.strip()

    return parsed_data

class Party:
    def __init__(self, creator, id):
        self.creator = creator
        self.joinedpeople = []
        self.partyid = id

    def addperson(self, name):
        self.joinedpeople.append(name)

    def removeperson(self, name):
        print(self.joinedpeople)
        print(name)
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
            self.chat = "global"
            bsend(client_socket,IAC + SB + GMCP + SE)
            bsend(client_socket,IAC + WILL + GMCP)
            self.data = parse_telnet_data(str(client_socket.recv(1024)))
            self.mudlet = True if self.data["xc9Core.Hello"]["client"] == "Mudlet" else False
            if self.mudlet:
                gmcpsend(client_socket,'Client.GUI { "version": "1", "url": "https://github.com/ArtyuiCraft/ARMUDlet/raw/refs/heads/main/ARMUDlet.mpackage" } ')

def bsend(client_socket,content):
    client_socket.send(content)

def gmcpsend(client_socket,content):
    client_socket.send(IAC + SB + GMCP + content.encode() + IAC + SE, socket.MSG_OOB)

def send(client_socket,content="",lines=0):
    sending = ("\n"*lines)+content+"\n"
    client_socket.send(sending.encode())

def sendall(content="", lines=0):
    sending = ("\n" * lines) + content + "\n"
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

def send_room(client):
    send(client.client_socket,"")
    map = '''#############
#           #
#           #
#           #
#           #
#############'''
    if client.mudlet:
        tmp = ''
        tmp += '[STARTMAP]\n'
        for i in map.split("\n"):
            tmp += "[MAP] "+i+"\n"
        for i in tmp.split("\n"):
            send(client.client_socket, i)
    else:
        for i in map.split("\n"):
            send(client.client_socket, i)

def command(client):
    send_room(client)
    client_socket = client.client_socket
    data = cinput(client_socket,nosend=True).split(" ")
    command = data[0].lower()
    data.pop(0)
    args = data
    match command:
        case ("say" | "s"):
            if client.chat.lower() == "global":
                sendall(f"[Chat] {client.username}: {" ".join(args)}")
            elif client.chat.lower() == "party":
                if client.joinedparty == None:
                    send(client_socket,"You sent that to no one")
                else:
                    send(client_socket,f"[PartyChat] {client.username}: {" ".join(args)}")
                    for i in client.joinedparty.joinedpeople:
                        send(i.client_socket,f"[PartyChat] {client.username}: {" ".join(args)}")
        case ("help" | "?"):
            send(client_socket,"commands: \n - help: shows this \n - say <message>: send a chat message!!")
        case ("createparty" | "cp"):
            if client.joinedparty == None:
                parties.append(Party(client.username,len(parties)))
                parties[-1].addperson(client.username)
                client.joinedparty = parties[-1]
                send(client_socket,f"Party {len(parties)-1} created")
            else:
                send(client_socket,f"Leave your current party first using leaveparty")
        case ("partyrequest" | "pr"):
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
        case ("joinparty"| "jp"):
            if client.joinedparty == None:
                id = int(args[0])
                parties[id].addperson(client)
                client.joinedparty = parties[id]
                send(client_socket,f"Joined party {id}")
            else:
                send(client_socket,"Leave your current party first using leaveparty")
        case ("leaveparty" | "lp"):
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
                client.chat = args[0]
        case ("up"|"u"):
            pass
        case ("down"|"d"):
            pass
        case ("left"|"l"):
            pass
        case ("right"|"r"):
            pass
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
            send(client_socket, "Ok logged in.\n")
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

