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
        self.board = []         # -1 = mina, 0-8 = número de minas adyacentes
        self.state = []         # HIDDEN, REVEALED o FLAGGED
        self.score = 0
        self.game_over = False
        self.win = False
        self.first_move = True
        self.start_time = None
        self.elapsed_time = 0
        self.loser_id = None    # ID del jugador que pisó una mina
        self.initialize_game()
    
    def initialize_game(self):
        """Inicializa el tablero con minas y números"""
        # Crear tableros vacíos
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.state = [[HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Colocar minas (se hará después del primer movimiento)
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
            
            # Actualizar números adyacentes
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols and self.board[nx][ny] != -1:
                        self.board[nx][ny] += 1

    def reveal(self, x, y, player_id=None):
        """Revela una celda y maneja la expansión de celdas vacías"""
        if self.game_over or self.state[x][y] != HIDDEN:
            return False
        
        # Colocar minas después del primer movimiento (para evitar perder en la primera jugada)
        if self.first_move:
            self.place_mines(x, y)
            self.start_timer()  # Iniciar el cronómetro en el primer movimiento
            self.first_move = False
        
        # Caso mina
        if self.board[x][y] == -1:
            self.state[x][y] = REVEALED
            self.score -= 5
            self.game_over = True
            self.loser_id = player_id
            return True
        
        # Caso número o vacío
        queue = deque([(x, y)])
        revealed_cells = set()
        
        while queue:
            cx, cy = queue.popleft()
            
            if (cx, cy) in revealed_cells:
                continue
            revealed_cells.add((cx, cy))
            
            # Solo procesar celdas ocultas
            if self.state[cx][cy] != HIDDEN:
                continue
            
            # Revelar celda
            self.state[cx][cy] = REVEALED
            cell_value = self.board[cx][cy]
            
            # Calcular puntos: base + valor de la celda (si es número)
            self.score += 1 + (cell_value if cell_value > 0 else 0)
            
            # Expansión para celdas vacías
            if cell_value == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            queue.append((nx, ny))
        
        return True

    def toggle_flag(self, x, y):
        """Alterna una bandera en la celda especificada"""
        if self.game_over or self.state[x][y] == REVEALED:
            return False
        
        # Colocar bandera
        if self.state[x][y] == HIDDEN:
            self.state[x][y] = FLAGGED
            if self.board[x][y] == -1:
                self.score += 5  # Bandera correcta
            else:
                self.score -= 3  # Bandera incorrecta
            return True
        
        # Quitar bandera
        if self.state[x][y] == FLAGGED:
            self.state[x][y] = HIDDEN
            if self.board[x][y] == -1:
                self.score -= 5  # Se quita bandera correcta
            else:
                self.score += 3  # Se corrige bandera incorrecta
            return True
        
        return False

    def check_win(self):
        """Verifica si el jugador ha ganado"""
        for x in range(self.rows):
            for y in range(self.cols):
                # Si hay celda sin mina oculta
                if self.board[x][y] != -1 and self.state[x][y] != REVEALED:
                    return False
        self.game_over = True
        self.win = True
        self.score += 10  # Bono por ganar
        return True

    def print_board(self, show_mines=False):
        """Imprime el tablero en la terminal"""
        # Actualizar tiempo
        if self.start_time and not self.game_over:
            self.elapsed_time = self.get_elapsed_time()
        
        # Mostrar tiempo en formato MM:SS
        mins, secs = divmod(self.elapsed_time, 60)
        print(f"Tiempo: {mins:02d}:{secs:02d} | Minas: {self.mines}")
        
        # Encabezado de columnas
        print("   " + " ".join(str(i) for i in range(self.cols)))
        
        for x in range(self.rows):
            # Encabezado de filas
            print(f"{x} |", end="")
            
            for y in range(self.cols):
                if self.state[x][y] == HIDDEN:
                    print(". ", end="")
                elif self.state[x][y] == FLAGGED:
                    print("F ", end="")
                elif self.state[x][y] == REVEALED:
                    if self.board[x][y] == -1:
                        print("* ", end="")
                    elif self.board[x][y] == 0:
                        print("  ", end="")
                    else:
                        print(f"{self.board[x][y]} ", end="")
                elif show_mines and self.board[x][y] == -1:
                    print("* ", end="")
                else:
                    print(". ", end="")
            print()
        
        print(f"Puntuación actual: {self.score}")