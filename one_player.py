from game import Buscaminas
import rankings
import time
from ui import print_bordered_board

def start_game(rows, cols, mines):
    """Inicia y corre un juego de buscaminas con los parametros dados."""
    # El jugador en modo de un jugador es siempre el jugador 0
    player_id = 0
    game = Buscaminas(rows, cols, mines)
    mode = f"{rows}x{cols}-{mines}minas"
    
    while not game.game_over:
        if game.start_time and not game.game_over:
            game.elapsed_time = game.get_elapsed_time()
        
        print_bordered_board(
            game.board,
            game.state,
            game.rows,
            game.cols,
            game.elapsed_time,
            game.mines,
            # Usar la puntuación del jugador 0
            game.scores[player_id]
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
            # Pasar el player_id a los métodos de juego
            game.reveal(x, y, player_id)
        elif action[0] == 'f':
            game.toggle_flag(x, y, player_id)
        else:
            print("Acción inválida")
        
        game.check_win()
    
    if game.start_time:
        game.elapsed_time = game.get_elapsed_time()
    
    final_score = game.scores[player_id]
    
    print_bordered_board(
        game.board,
        game.state,
        game.rows,
        game.cols,
        game.elapsed_time,
        game.mines,
        final_score,
        True # Mostrar minas al final
    )
    
    elapsed_time = game.elapsed_time
    
    if game.win:
        print(f"¡Ganaste! Puntuación final: {final_score}")
    else:
        print(f"¡Juego terminado! Puntuación final: {final_score}")
    
    # Guardar la puntuación independientemente de si se gana o se pierde
    rankings.save_score(final_score, mode, int(elapsed_time))
    print("Tu puntuación ha sido guardada en el ranking.")
    
    input("Presione Enter para volver al menú...")