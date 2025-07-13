import socket
import pickle
import os

def clearterm():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

class GameClient:
    def __init__(self, host, port, rows, cols, mines):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.game = None
        self.client_socket.sendall(pickle.dumps({'rows': rows, 'cols': cols, 'mines': mines}))

    def receive_game_state(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                received_data = pickle.loads(data)
                if isinstance(received_data, dict) and 'error' in received_data:
                    print(received_data['error'])
                else:
                    self.game = received_data
                    self.display_board()

            except Exception as e:
                print(f"Error receiving game state: {e}")
                break

    def display_board(self):
        clearterm()
        self.game.print_board()

    def send_action(self, action):
        self.client_socket.sendall(pickle.dumps(action))

    def start(self):
        import threading
        receive_thread = threading.Thread(target=self.receive_game_state)
        receive_thread.daemon = True
        receive_thread.start()

        while self.game is None:
            pass # Wait for initial game state

        while not self.game.game_over:
            action_str = input("Action (r x y: reveal, f x y: flag, q: quit): ").split()
            
            if not action_str:
                continue

            if action_str[0] == 'q':
                break

            if len(action_str) < 3:
                print("Invalid command")
                continue

            try:
                x = int(action_str[1])
                y = int(action_str[2])
            except ValueError:
                print("Invalid coordinates")
                continue

            if action_str[0] == 'r':
                self.send_action({'type': 'reveal', 'x': x, 'y': y})
            elif action_str[0] == 'f':
                self.send_action({'type': 'flag', 'x': x, 'y': y})
            else:
                print("Invalid action")

        if self.game.win:
            print(f"You won! Final score: {self.game.score}")
        else:
            print(f"Game over! Final score: {self.game.score}")
        input("Press Enter to return to the menu...")

if __name__ == "__main__":
    # Asume que el servidor está en localhost y puerto 12345 por defecto
    # Si el servidor está en otra IP, cámbiala aquí.
    client = GameClient('127.0.0.1', 12345)
    client.start()
