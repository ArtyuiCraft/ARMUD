import socket
import threading
from utils import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import importlib
import utils

class CodeReloader(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 Reloading {event.src_path}...")
            importlib.reload(utils)

def handle_client(client_socket, addr):
    header_sequence(client_socket)
    client = user(client_socket, addr)
    if client.error == True:
        print(f"[+] Client {addr[0]}:{addr[1]} has an error")
        return
    clients.append(client)
    while True:
        command(client)

def main():
    while True:
        client, addr = server.accept()
        print(f"[+] Accepted connection from: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,addr))
        client_handler.start()

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(CodeReloader(), path=".", recursive=True)
    observer.start()
    bind_ip = "0.0.0.0"
    bind_port = 2323
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    print(f"[+] Listening on port {bind_ip} : {bind_port}")
    try:
        main()
    except KeyboardInterrupt:
        print("keybioar")
