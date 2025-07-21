import socket
import pickle
import threading
import time
from game import Buscaminas
import rankings # Importar el módulo de rankings

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.games = {}
        self.clients_per_game = {}
        self.settings_per_game = {}
        self.player_names = {}
        self.game_events = {}
        self.game_counter = 1
        self.lock = threading.Lock()
        self.running = True

    def update_timers(self):
        """Actualiza el tiempo transcurrido para todos los juegos activos."""
        while self.running:
            with self.lock:
                for game_id, game in self.games.items():
                    if game.start_time and not game.game_over:
                        game.elapsed_time = game.get_elapsed_time()
            time.sleep(1)

    def create_new_game_unlocked(self, settings):
        game_id = self.game_counter
        self.game_counter += 1
        rows, cols, mines = settings
        game = Buscaminas(rows, cols, mines)
        self.games[game_id] = game
        self.settings_per_game[game_id] = settings
        self.clients_per_game[game_id] = []
        self.player_names[game_id] = []
        self.game_events[game_id] = threading.Event()
        return game_id

    def handle_connection(self, client_socket):
        game_id = None
        player_id = None
        is_creator = False
        game_ended_gracefully = False
        
        try:
            initial_data = client_socket.recv(4096)
            if not initial_data: return
            
            action = pickle.loads(initial_data)
            username = action.get('username', f"Jugador_{int(time.time())}")

            with self.lock:
                if action['type'] == 'create':
                    settings = (action['rows'], action['cols'], action['mines'])
                    game_id = self.create_new_game_unlocked(settings)
                    player_id = 0
                    self.clients_per_game[game_id].append(client_socket)
                    self.player_names[game_id].append(username)
                    is_creator = True
                    client_socket.sendall(pickle.dumps({"game_id": game_id, "player_id": player_id, "message": f"Partida creada con ID {game_id}. Esperando oponente..."}))

                elif action['type'] == 'join':
                    game_id = action.get('game_id')
                    if game_id in self.games and len(self.clients_per_game.get(game_id, [])) == 1:
                        player_id = 1
                        self.clients_per_game[game_id].append(client_socket)
                        self.player_names[game_id].append(username)
                        game = self.games[game_id]
                        game.player_names = self.player_names[game_id]
                        
                        notification = {"game": game, "game_id": game_id, "message": "Oponente encontrado. ¡La partida comienza!"}
                        for i, c in enumerate(self.clients_per_game[game_id]):
                            notification.update({"player_id": i, "your_turn": (i == game.current_turn)})
                            c.sendall(pickle.dumps(notification))
                        self.game_events[game_id].set()
                    else:
                        client_socket.sendall(pickle.dumps({"error": "ID de partida inválido o la partida está llena"}))
                        return
                else:
                    client_socket.sendall(pickle.dumps({"error": "Acción inválida"}))
                    return

            if is_creator:
                if not self.game_events[game_id].wait(timeout=300):
                    client_socket.sendall(pickle.dumps({"error": "Tiempo de espera para oponente agotado."}))
                    return
            
            game = self.games[game_id]
            clients = self.clients_per_game[game_id]

            while not game.game_over:
                data = client_socket.recv(4096)
                if not data: break
                
                action = pickle.loads(data)
                
                with self.lock:
                    if game.current_turn == player_id:
                        move_was_valid = False
                        if action['type'] == 'reveal':
                            move_was_valid = game.reveal(action['x'], action['y'], player_id)
                        elif action['type'] == 'flag':
                            move_was_valid = game.toggle_flag(action['x'], action['y'], player_id)
                        
                        if move_was_valid:
                            game.check_win()
                            message = ""
                            if game.game_over:
                                game_ended_gracefully = True
                                winner_id = -1
                                if game.win:
                                    winner_id = game.current_turn # El jugador actual gana
                                    message = f"¡Gana {game.player_names[winner_id]}!"
                                elif game.loser_id is not None:
                                    winner_id = 1 - game.loser_id
                                    winner_name = game.player_names[winner_id]
                                    loser_name = game.player_names[game.loser_id]
                                    message = f"{loser_name} pisó una mina. ¡Gana {winner_name}!"
                                
                                # Guardar puntuación del ganador
                                if winner_id != -1:
                                    winner_score = game.scores[winner_id]
                                    mode = f"{game.rows}x{game.cols}-{game.mines}"
                                    rankings.save_score(winner_score, mode, int(game.elapsed_time))

                            else:
                                game.current_turn = 1 - game.current_turn
                            
                            notification = {"game": game, "message": message}
                            for i, c in enumerate(clients):
                                notification.update({"your_turn": (i == game.current_turn and not game.game_over)})
                                c.sendall(pickle.dumps(notification))
                        else:
                            client_socket.sendall(pickle.dumps({"message": "Movimiento inválido."}))
                    else:
                        client_socket.sendall(pickle.dumps({"message": "No es tu turno"}))

        except (pickle.UnpicklingError, ConnectionResetError, BrokenPipeError) as e:
            print(f"Cliente desconectado: {e}")
        finally:
            with self.lock:
                if game_id and game_id in self.games:
                    if not game_ended_gracefully:
                        self.games[game_id].game_over = True
                        remaining_clients = [c for c in self.clients_per_game.get(game_id, []) if c != client_socket]
                        for c in remaining_clients:
                            c.sendall(pickle.dumps({"error": "El otro jugador se ha desconectado."}))
                    
                    if client_socket in self.clients_per_game.get(game_id, []):
                        self.clients_per_game[game_id].remove(client_socket)
                    
                    if not self.clients_per_game.get(game_id):
                        if game_id in self.games: del self.games[game_id]
                        if game_id in self.clients_per_game: del self.clients_per_game[game_id]
                        if game_id in self.settings_per_game: del self.settings_per_game[game_id]
                        if game_id in self.game_events: del self.game_events[game_id]
                        if game_id in self.player_names: del self.player_names[game_id]

            client_socket.close()

    def stop(self):
        self.running = False
        self.server_socket.close()

    def start(self):
        print(f"Servidor iniciado en {self.server_socket.getsockname()}, esperando jugadores...")
        timer_thread = threading.Thread(target=self.update_timers)
        timer_thread.daemon = True
        timer_thread.start()
        
        self.running = True
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(client_socket,)).start()
            except OSError:
                break # Socket cerrado