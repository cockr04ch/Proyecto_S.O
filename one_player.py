from game import Buscaminas
import rankings
import time
from ui import print_bordered_board

def start_game(rows, cols, mines):
    """Inicia y corre un juego de buscaminas con los parametros dados."""
    game = Buscaminas(rows, cols, mines)
    mode = f"{rows}x{cols}-{mines}minas"
    start_time = time.time()
    
    while not game.game_over:
        # Actualizar tiempo
        if game.start_time and not game.game_over:
            game.elapsed_time = game.get_elapsed_time()
        
        # Usar la nueva función de impresión
        print_bordered_board(
            game.board,
            game.state,
            game.rows,
            game.cols,
            game.elapsed_time,
            game.mines,
            game.score
        )
        
        action = input("Acción (r x y: revelar, f x y: bandera, q: salir): ").split()
        
        if not action:
            continue
            
        if action[0] == 'q':
            break
            
        if len(action) < 3:
            print("Comando inválido")
            continue
            
        try:
            x = int(action[1])
            y = int(action[2])
        except ValueError:
            print("Coordenadas inválidas")
            continue
            
        if x < 0 or x >= game.rows or y < 0 or y >= game.cols:
            print("Coordenadas fuera de rango")
            continue
            
        if action[0] == 'r':
            game.reveal(x, y)
        elif action[0] == 'f':
            game.toggle_flag(x, y)
        else:
            print("Acción inválida")
        
        game.check_win()
    
    # Mostrar resultado final
    game.elapsed_time = game.get_elapsed_time()
    print_bordered_board(
        game.board,
        game.state,
        game.rows,
        game.cols,
        game.elapsed_time,
        game.mines,
        game.score,
        True
    )
    elapsed_time = game.elapsed_time
    if game.win:
        print(f"¡Ganaste! Puntuación final: {game.score}")
        rankings.save_score(game.score, mode, int(elapsed_time))
    else:
        print(f"¡Juego terminado! Puntuación final: {game.score}")
    input("Presione Enter para volver al menú...")
