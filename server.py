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

        # Player 1 connects and sends settings
        client_socket_p1, addr_p1 = self.server_socket.accept()
        print(f"Player 1 connected from {addr_p1}")
        try:
            settings_data = client_socket_p1.recv(4096)
            settings = pickle.loads(settings_data)
            rows, cols, mines = settings['rows'], settings['cols'], settings['mines']
            self.game = Buscaminas(rows, cols, mines)
            self.clients.append(client_socket_p1)
            print(f"Game created with settings from Player 1: {rows}x{cols}, {mines} mines.")
        except Exception as e:
            print(f"Error setting up game with Player 1: {e}")
            client_socket_p1.close()
            return

        # Player 2 connects and sends settings (which are ignored)
        print("Waiting for Player 2...")
        client_socket_p2, addr_p2 = self.server_socket.accept()
        print(f"Player 2 connected from {addr_p2}")
        try:
            # Read and discard settings from player 2
            client_socket_p2.recv(4096)
            self.clients.append(client_socket_p2)
        except Exception as e:
            print(f"Error connecting Player 2: {e}")
            client_socket_p2.close()
            if self.clients:
                self.clients[0].close()
            return

        # Both players connected, game is ready. Broadcast initial state.
        print("Both players connected. Starting game.")
        self.broadcast_game_state()

        # Start threads to handle client actions
        threading.Thread(target=self.handle_client, args=(self.clients[0], 0)).start()
        threading.Thread(target=self.handle_client, args=(self.clients[1], 1)).start()

if __name__ == "__main__":
    server = GameServer()
    server.start()
