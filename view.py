import os #Importar llamada del Sistema Operativo
import one_player
import multiplayer 

def clearterm():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')



def dashboard():
    print("""
 ____  _  _  ____   ___   __              
(  _ \/ )( \/ ___) / __) / _\             
 ) _ () \/ (\\___ \( (__ /    \            
(____/\____/(____/ \___)\_/\_/            
               _  _  __  __ _   __   ____ 
              ( \/ )(  )(  ( \ / _\ / ___)
              / \/ \ )( /    //    \\___ \\
              \_)(_/(__)\_)__)\_/\_/(____/ """)

def menu():
    while True :
        clearterm()
        dashboard()
        print("[ 1 Solo Jugador ]")
        print("[ 2 Jugadores Online]")
        print("[ 0 Salir]")
        opcion = input("Ingrese Opcion : ").strip() #.strip() Elimina Espacion restante
        sltc_menu(opcion)
        if opc=='0':
            break

def sltc_menu(opc):

    if opc == '1':
        clearterm()
        dashboard()
        print("Seleccione tamano del Tablero:")
        print("1. 8x8 (10 Minas)")
        print("2. 10x10 (20 Minas)")
        print("3. Personalizado")
        opc_menu = input("Ingrese Opcion : ").strip()

        if opc_menu == '1':
            one_player.start_game(8, 8, 10)
        elif opc_menu == '2':
            one_player.start_game(10, 10, 20)
        elif opc_menu == '3':
            try:
                rows = int(input("Filas: "))
                cols = int(input("Columnas: "))
                mines = int(input("Minas: "))
                one_player.start_game(rows, cols, mines)
            except ValueError:
                print("Entrada inválida. Por favor ingrese números.")
                input("Presione Enter para continuar...")
    elif opc == '2':
        multiplayer.start_multiplayer()
        clearterm()
        dashboard()
        print("Seleccione tamano del Tablero:")
        print("1. 8x8 (10 Minas)")
        print("2. 10x10 (20 Minas)")
        print("3. Personalizado")
        opc_menu = input("Ingrese Opcion : ").strip()

        if opc_menu == '1':
            one_player.start_game(8, 8, 10)
        elif opc_menu == '2':
            one_player.start_game(10, 10, 20)
        elif opc_menu == '3':
            try:
                rows = int(input("Filas: "))
                cols = int(input("Columnas: "))
                mines = int(input("Minas: "))
                one_player.start_game(rows, cols, mines)
            except ValueError:
                print("Entrada inválida. Por favor ingrese números.")
                input("Presione Enter para continuar...")