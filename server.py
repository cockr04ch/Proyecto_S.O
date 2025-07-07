import socket
import pickle
import threading
from game import Buscaminas

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(2)
        self.clients = []
        self.game = None
        self.current_turn = 0

    def handle_client(self, client_socket, player_id):
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                action = pickle.loads(data)
                
                if self.current_turn == player_id:
                    if action['type'] == 'reveal':
                        self.game.reveal(action['x'], action['y'])
                    elif action['type'] == 'flag':
                        self.game.toggle_flag(action['x'], action['y'])
                    
                    self.game.check_win()
                    self.current_turn = 1 - self.current_turn  # Switch turns
                    self.broadcast_game_state()
                else:
                    # It's not this player's turn
                    client_socket.sendall(pickle.dumps({'error': 'Not your turn'}))

            except Exception as e:
                print(f"Error handling client: {e}")
                break
        
        client_socket.close()
        self.clients.remove(client_socket)

    def broadcast_game_state(self):
        for client in self.clients:
            try:
                client.sendall(pickle.dumps(self.game))
            except Exception as e:
                print(f"Error broadcasting game state: {e}")

    def start(self):
        print("Server started, waiting for players...")
        while len(self.clients) < 2:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            print(f"Player {len(self.clients)} connected from {addr}")

        self.game = Buscaminas()
        self.broadcast_game_state()

        for i, client in enumerate(self.clients):
            threading.Thread(target=self.handle_client, args=(client, i)).start()

if __name__ == "__main__":
    server = GameServer()
    server.start()
