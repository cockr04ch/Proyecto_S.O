import random
from collections import deque
import time

# Constantes para estados de las celdas
HIDDEN = 0
REVEALED = 1
FLAGGED = 2

class Buscaminas:
    def __init__(self, rows=8, cols=8, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = []
        self.state = []
        # Cambiado a una lista para soportar multijugador
        self.scores = [0, 0]
        self.game_over = False
        self.win = False
        self.first_move = True
        self.start_time = None
        self.elapsed_time = 0
        self.loser_id = None
        self.player_names = ["Jugador 0", "Jugador 1"]
        # Añadido para llevar el turno en el modelo de juego
        self.current_turn = 0
        self.initialize_game()
    
    @property
    def score(self):
        """Para compatibilidad con modo de un jugador, devuelve la puntuación del primer jugador."""
        return self.scores[0]

    def initialize_game(self):
        """Inicializa el tablero con minas y números"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.state = [[HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        self.mine_locations = set()
    
    def start_timer(self):
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)
    
    def place_mines(self, first_x, first_y):
        """Coloca minas evitando la posición inicial y sus vecinos"""
        safe_area = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    safe_area.add((nx, ny))
        
        mines_placed = 0
        while mines_placed < self.mines:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            
            if (x, y) in safe_area or (x, y) in self.mine_locations:
                continue
            
            self.board[x][y] = -1
            self.mine_locations.add((x, y))
            mines_placed += 1
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols and self.board[nx][ny] != -1:
                        self.board[nx][ny] += 1

    def reveal(self, x, y, player_id=0): # player_id por defecto es 0
        """Revela una celda y maneja la puntuación para el jugador específico."""
        if self.game_over or self.state[x][y] != HIDDEN:
            return False
        
        if self.first_move:
            self.place_mines(x, y)
            self.start_timer()
            self.first_move = False
        
        if self.board[x][y] == -1:
            self.state[x][y] = REVEALED
            self.scores[player_id] -= 5
            self.game_over = True
            self.loser_id = player_id
            return True
        
        queue = deque([(x, y)])
        revealed_cells = set()
        
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in revealed_cells or self.state[cx][cy] != HIDDEN:
                continue
            
            revealed_cells.add((cx, cy))
            self.state[cx][cy] = REVEALED
            cell_value = self.board[cx][cy]
            
            self.scores[player_id] += 1 + (cell_value if cell_value > 0 else 0)
            
            if cell_value == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            queue.append((nx, ny))
        return True

    def toggle_flag(self, x, y, player_id=0): # player_id por defecto es 0
        """Alterna una bandera y ajusta la puntuación del jugador."""
        if self.game_over or self.state[x][y] == REVEALED:
            return False
        
        if self.state[x][y] == HIDDEN:
            self.state[x][y] = FLAGGED
            if self.board[x][y] == -1:
                self.scores[player_id] += 5
            else:
                self.scores[player_id] -= 3
            return True
        
        if self.state[x][y] == FLAGGED:
            self.state[x][y] = HIDDEN
            if self.board[x][y] == -1:
                self.scores[player_id] -= 5
            else:
                self.scores[player_id] += 3
            return True
        return False

    def check_win(self):
        """Verifica si se ha ganado la partida."""
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board[x][y] != -1 and self.state[x][y] != REVEALED:
                    return False
        
        self.game_over = True
        self.win = True
        # Bono de victoria para el jugador actual
        if self.loser_id is None: # Si nadie ha perdido, es una victoria normal
            winner_id = self.current_turn
            self.scores[winner_id] += 10
        return True
