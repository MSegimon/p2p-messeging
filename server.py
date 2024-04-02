import socket
import threading

# Server to manage peer addresses
class PeerDiscoveryHandler:
    peers = []

    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 10000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

    def handle_peer(self, conn):
        while True:
            data = conn.recv(1024).decode('utf-8')
            if data == 'get_peers':
                conn.send(','.join(self.peers).encode('utf-8'))
            elif data.startswith('register'):
                _, peer_address = data.split()
                if peer_address not in self.peers:
                    self.peers.append(peer_address)
            elif data == 'exit':
                conn.close()
                break

    def run(self):
        print(f'Server running on {self.host}:{self.port}')
        while True:
            conn, _ = self.server.accept()
            threading.Thread(target=self.handle_peer, args=(conn,)).start()

# Start the server
if __name__ == '__main__':
    server = PeerDiscoveryHandler()
    server.run()
