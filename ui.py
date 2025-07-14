from colorama import init, Fore, Back, Style

init(autoreset=True)  # Auto-reset de estilos

# Constantes para estados de las celdas (importadas de game.py)
HIDDEN = 0
REVEALED = 1
FLAGGED = 2

# Sistema de colores para el buscaminas
COLOR_MAP = {
    1: Fore.BLUE,
    2: Fore.GREEN,
    3: Fore.RED,
    4: Fore.MAGENTA,
    5: Fore.YELLOW,
    6: Fore.CYAN,
    7: Fore.BLACK,
    8: Fore.WHITE,
    "mine": Fore.RED + Style.BRIGHT,
    "flag": Fore.YELLOW + Style.BRIGHT,
    "hidden": Style.DIM,
    "border": Fore.LIGHTBLUE_EX
}

def print_bordered_board(board, state, rows, cols, elapsed_time=0, mines=0, score=0, show_mines=False):
    """Imprime tablero con bordes estilizados y colores"""
    # Actualizar tiempo
    mins, secs = divmod(elapsed_time, 60)
    time_str = f"Tiempo: {mins:02d}:{secs:02d}"
    mines_str = f"Minas: {mines}"
    print(f"{time_str} | {mines_str}")
    
    # Encabezado de columnas
    header = "" + " ".join(f"{COLOR_MAP['border']}{i:^3}{Style.RESET_ALL}" for i in range(cols))
    print(f"{COLOR_MAP['border']}  ╔{'╦'.join(['═══']*cols)}╗")
    print(f"  ║{header}║")
    
    for x in range(rows):
        # Separador entre filas
        if x > 0:
            print(f"  ╠{'╬'.join(['═══']*cols)}╣")
        
        # Contenido de la fila
        row_str = f"{COLOR_MAP['border']}{x} ║{Style.RESET_ALL}"
        for y in range(cols):
            if state[x][y] == HIDDEN:
                if show_mines and board[x][y] == -1:
                    cell = f"{COLOR_MAP['mine']} * "
                else:
                    cell = f"{COLOR_MAP['hidden']} ░ "
            elif state[x][y] == FLAGGED:
                if show_mines and board[x][y] != -1:
                    cell = f"{Fore.RED} X "
                else:
                    cell = f"{COLOR_MAP['flag']} ⚑ "
            elif board[x][y] == -1:
                cell = f"{COLOR_MAP['mine']} * "
            elif board[x][y] == 0:
                cell = "   "
            else:
                color = COLOR_MAP.get(board[x][y], Fore.WHITE)
                cell = f"{color} {board[x][y]} "
            
            row_str += cell + COLOR_MAP['border'] + "║" + Style.RESET_ALL
        
        print(row_str)
    
    print(f"{COLOR_MAP['border']}  ╚{'╩'.join(['═══']*cols)}╝")
    print(f"Puntuación actual: {score}")
