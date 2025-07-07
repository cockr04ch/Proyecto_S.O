from game import Buscaminas

def start_game(rows, cols, mines):
    """Inicia y corre un juego de buscaminas con los parametros dados."""
    game = Buscaminas(rows, cols, mines)
    
    while not game.game_over:
        game.print_board()
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
    game.print_board(show_mines=True)
    if game.win:
        print(f"¡Ganaste! Puntuación final: {game.score}")
    else:
        print(f"¡Juego terminado! Puntuación final: {game.score}")
    input("Presione Enter para volver al menú...")

def main_menu_for_direct_run():
    """Menu para cuando el script se corre directamente."""
    print("Seleccione tamaño de tablero:")
    print("1. 8x8 (10 minas)")
    print("2. 10x10 (20 minas)")
    print("3. Personalizado")
    
    choice = input("Opción: ")
    
    if choice == '1':
        start_game(8, 8, 10)
    elif choice == '2':
        start_game(10, 10, 20)
    else:
        rows = int(input("Filas: "))
        cols = int(input("Columnas: "))
        mines = int(input("Minas: "))
        start_game(rows, cols, mines)

if __name__ == "__main__":
    main_menu_for_direct_run()
