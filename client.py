import socket
import pickle
import os
import sys
import time
import threading
from utils import clearterm

class GameClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.game = None
        self.game_id = None
        self.player_id = None
        self.error = None
        self.receive_thread_ready = threading.Event()

    def play_sound(self):
        """Reproduce sonido compatible con Termux"""
        if sys.platform == "linux":
            sys.stdout.write('\a')
            sys.stdout.flush()

    def receive_game_state(self):
        self.receive_thread_ready.set()
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    self.error = "Conexión perdida con el servidor."
                    break
                
                received_data = pickle.loads(data)

                if isinstance(received_data, dict):
                    if 'error' in received_data:
                        self.error = received_data['error']
                        # No imprimir aquí, el bucle principal lo hará
                        break

                    if 'game_id' in received_data and self.game_id is None:
                        self.game_id = received_data['game_id']
                    if 'player_id' in received_data and self.player_id is None:
                        self.player_id = received_data['player_id']

                    if 'game' in received_data:
                        self.game = received_data['game']
                        if received_data.get('your_turn', False):
                            self.play_sound()
                        self.display_board()
                    
                    if 'message' in received_data:
                        print(f"{' ' * 80}{received_data['message']}", end="\n")

            except (pickle.UnpicklingError, ConnectionResetError, BrokenPipeError) as e:
                self.error = f"Error de conexión: {e}"
                break
            except Exception as e:
                self.error = f"Error inesperado: {e}"
                break

    def display_board(self):
        clearterm()
        from ui import print_bordered_board
        print_bordered_board(
            self.game.board,
            self.game.state,
            self.game.rows,
            self.game.cols,
            self.game.elapsed_time,
            self.game.mines,
            self.game.score,
            show_mines=self.game.game_over
        )
        if not self.game.game_over:
            current_player_name = self.game.player_names[self.game.current_turn]
            if self.game.current_turn == self.player_id:
                print(f"Es tu turno ({current_player_name})")
            else:
                print(f"Turno de {current_player_name}")

    def send_action(self, action):
        try:
            self.client_socket.sendall(pickle.dumps(action))
        except (ConnectionResetError, BrokenPipeError):
            self.error = "No se pudo enviar la acción. El servidor cerró la conexión."

    def start(self, initial_action):
        receive_thread = threading.Thread(target=self.receive_game_state)
        receive_thread.daemon = True
        receive_thread.start()

        self.receive_thread_ready.wait()

        self.send_action(initial_action)

        print("Registrando en el servidor...")
        start_wait = time.time()
        while self.player_id is None and self.error is None:
            time.sleep(0.1)
            if time.time() - start_wait > 15:
                self.error = "No se recibió respuesta del servidor."
                break
        
        if self.error:
            print(f"\nError de conexión: {self.error}")
            input("Presione Enter para volver al menú...")
            self.client_socket.close()
            return

        if self.game is None and self.error is None:
            print("Esperando a que se una el oponente...")
            start_wait = time.time()
            while self.game is None and self.error is None:
                time.sleep(0.2)
                if time.time() - start_wait > 300:
                    self.error = "Tiempo de espera para el oponente agotado."
                    break

        if self.error and not self.game:
            print(f"\nNo se pudo iniciar la partida: {self.error}")
            input("Presione Enter para volver al menú...")
            self.client_socket.close()
            return
        
        while not self.game.game_over and self.error is None:
            action_str = input("Acción (r x y: revelar, f x y: bandera, q: salir): ").split()
            
            if not action_str or self.error:
                continue

            if action_str[0] == 'q':
                break

            if len(action_str) < 3:
                print("Comando inválido")
                continue

            try:
                x = int(action_str[1])
                y = int(action_str[2])
            except ValueError:
                print("Coordenadas inválidas")
                continue

            if self.game.current_turn != self.player_id:
                print("No es tu turno.")
                continue

            if action_str[0] == 'r':
                self.send_action({'type': 'reveal', 'x': x, 'y': y})
            elif action_str[0] == 'f':
                self.send_action({'type': 'flag', 'x': x, 'y': y})
            else:
                print("Acción inválida")

        if self.error:
             print(f"\nSe ha producido un error: {self.error}")
        elif self.game and self.game.win:
            print(f"¡Has ganado! Puntuación final: {self.game.score}")
        elif self.game:
            print(f"¡Juego terminado! Puntuación final: {self.game.score}")
        
        input("\nPresione Enter para volver al menú...")
        self.client_socket.close()
