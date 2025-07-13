import socket
import pickle
import threading
import time
from game import Buscaminas

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.games = {}
        self.clients_per_game = {}
        self.settings_per_game = {}
        self.game_events = {}
        self.game_counter = 1
        self.lock = threading.Lock()

    def create_new_game_unlocked(self, settings):
        game_id = self.game_counter
        self.game_counter += 1
        rows, cols, mines = settings
        game = Buscaminas(rows, cols, mines)
        game.current_turn = 0
        self.games[game_id] = game
        self.settings_per_game[game_id] = settings
        self.clients_per_game[game_id] = []
        self.game_events[game_id] = threading.Event()
        return game_id

    def handle_connection(self, client_socket):
        game_id = None
        player_id = None
        is_creator = False
        
        try:
            initial_data = client_socket.recv(4096)
            if not initial_data:
                return
            
            action = pickle.loads(initial_data)

            # --- Critical Section: Find or Create Game ---
            # Prepare all socket data within the lock, but send it outside.
            response_to_send = None
            notifications_to_send = []

            with self.lock:
                if action['type'] == 'create':
                    settings = (action['rows'], action['cols'], action['mines'])
                    game_id = self.create_new_game_unlocked(settings)
                    player_id = 0
                    self.clients_per_game[game_id].append(client_socket)
                    is_creator = True
                    
                    response_to_send = pickle.dumps({
                        "game_id": game_id, "player_id": player_id,
                        "message": f"Partida creada con ID {game_id}. Esperando oponente..."
                    })

                elif action['type'] == 'join':
                    game_id = action.get('game_id')
                    if game_id in self.games and len(self.clients_per_game.get(game_id, [])) == 1:
                        player_id = 1
                        self.clients_per_game[game_id].append(client_socket)
                        game = self.games[game_id]
                        
                        # Prepare notifications for both players
                        for i, c in enumerate(self.clients_per_game[game_id]):
                            data = pickle.dumps({
                                "game": game, "game_id": game_id, "player_id": i,
                                "your_turn": (i == game.current_turn),
                                "message": "Oponente encontrado. ¡La partida comienza!"
                            })
                            notifications_to_send.append((c, data))
                        
                        self.game_events[game_id].set() # Signal the creator to start
                    else:
                        response_to_send = pickle.dumps({"error": "ID de partida inválido o la partida está llena"})
                else:
                    response_to_send = pickle.dumps({"error": "Acción inválida"})
            
            # --- Send responses/notifications outside the lock ---
            if response_to_send:
                client_socket.sendall(response_to_send)
                if b'error' in response_to_send: return

            for c, data in notifications_to_send:
                c.sendall(data)

            # --- Wait for game to start (if creator) ---
            if is_creator:
                if not self.game_events[game_id].wait(timeout=300):
                    print(f"Partida {game_id} expiró.")
                    try:
                        client_socket.sendall(pickle.dumps({"error": "Tiempo de espera para oponente agotado."}))
                    except: pass
                    return
            
            game = self.games[game_id]
            clients = self.clients_per_game[game_id]

            # --- Main Game Loop ---
            while not game.game_over:
                data = client_socket.recv(4096)
                if not data: break
                
                action = pickle.loads(data)
                
                update_notifications = []
                with self.lock:
                    if game.current_turn == player_id:
                        if action['type'] == 'reveal':
                            game.reveal(action['x'], action['y'])
                        elif action['type'] == 'flag':
                            game.toggle_flag(action['x'], action['y'])
                        
                        game.check_win()
                        if not game.game_over:
                            game.current_turn = 1 - game.current_turn
                        
                        # Prepare update for all clients
                        for i, c in enumerate(clients):
                            data = pickle.dumps({
                                "game": game,
                                "your_turn": (i == game.current_turn and not game.game_over)
                            })
                            update_notifications.append((c, data))
                    else:
                        # Prepare error for the current client only
                        error_data = pickle.dumps({"error": "No es tu turno"})
                        update_notifications.append((client_socket, error_data))
                
                # Send updates outside the lock
                for c, data in update_notifications:
                    try:
                        c.sendall(data)
                    except:
                        print(f"No se pudo enviar a un cliente en la partida {game_id}")


        except (pickle.UnpicklingError, ConnectionResetError, BrokenPipeError) as e:
            print(f"Cliente desconectado (Juego: {game_id}, Jugador: {player_id}): {e}")
        except Exception as e:
            print(f"Error en la conexión (Juego: {game_id}, Jugador: {player_id}): {e}")
        
        finally:
            # --- Cleanup ---
            with self.lock:
                if game_id and game_id in self.games:
                    self.games[game_id].game_over = True
                    
                    if client_socket in self.clients_per_game.get(game_id, []):
                        self.clients_per_game[game_id].remove(client_socket)
                    
                    # Notify remaining players
                    remaining_clients = self.clients_per_game.get(game_id, [])
                    for c in remaining_clients:
                        try:
                            c.sendall(pickle.dumps({"error": "El otro jugador se ha desconectado. Fin de la partida."}))
                        except: pass
                    
                    # Delete game if empty
                    if not remaining_clients:
                        print(f"Eliminando partida vacía {game_id}.")
                        if game_id in self.games: del self.games[game_id]
                        if game_id in self.clients_per_game: del self.clients_per_game[game_id]
                        if game_id in self.settings_per_game: del self.settings_per_game[game_id]
                        if game_id in self.game_events: del self.game_events[game_id]

            client_socket.close()

    def start(self):
        print(f"Servidor iniciado en {self.server_socket.getsockname()}, esperando jugadores...")
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Nueva conexión desde {addr}")
            threading.Thread(target=self.handle_connection, args=(client_socket,)).start()

if __name__ == "__main__":
    server = GameServer()
    server.start()
