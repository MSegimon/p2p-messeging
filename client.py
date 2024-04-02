import socket
import threading
import sqlite3
import sys

class P2PClient:
    def __init__(self, server_host, server_port, local_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_host = 'localhost'
        self.local_port = local_port  # Use the port number passed as an argument
        self.sock.bind((self.local_host, int(self.local_port)))
        self.sock.listen(1)
        print(f'Listening for incoming messages on {self.local_host}:{self.local_port}')
        threading.Thread(target=self.receive_message, daemon=True).start()

    def get_peers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_host, self.server_port))
            s.send('get_peers'.encode('utf-8'))
            peers = s.recv(1024).decode('utf-8')
            if peers:
                print("Current peers:", peers)
            else:
                print("No peers found.")
            return peers.split(',')

    def send_message(self, peer_host, peer_port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_host, int(peer_port)))
            s.send(message.encode('utf-8'))

    def receive_message(self):
        while True:
            conn, addr = self.sock.accept()
            message = conn.recv(1024).decode('utf-8')
            print(f'\nMessage from {addr}: {message}')
            print("Enter the peer's host and port (host:port) or 'exit' to quit: ")
            # Store the received message in SQLite database
            with sqlite3.connect('messages.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO messages VALUES (datetime('now'), ?, ?)", (str(addr), message))
                conn.commit()

    def register_with_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_host, self.server_port))
            s.send(f'register {self.local_host}:{self.local_port}'.encode('utf-8'))

    def user_interface(self):
        while True:
            user_input = input("Enter command (send, get_peers, exit): ")
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'get_peers':
                self.get_peers()
            elif user_input.lower() == 'send':
                peer = input("Enter the peer's host and port (host:port): ")
                if ':' not in peer:
                    print("Invalid input. Format should be host:port.")
                    continue
                peer_host, peer_port = peer.split(':')
                message = input("Enter your message: ")
                self.send_message(peer_host, peer_port, message)
            else:
                print("Invalid command. Please use 'send', 'get_peers', or 'exit'.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python client.py <port>")
        sys.exit(1)
    port = sys.argv[1]
    try:
        port_num = int(port)
        assert 1024 <= port_num <= 65535
    except (ValueError, AssertionError):
        print("Port must be a number between 1024 and 65535.")
        sys.exit(1)

    client = P2PClient('localhost', 10000, port)
    client.register_with_server()
    user_thread = threading.Thread(target=client.user_interface, daemon=True)
    user_thread.start()
    user_thread.join()
