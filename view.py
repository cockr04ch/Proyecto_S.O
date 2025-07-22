import one_player
import multiplayer 
import rankings
from utils import clearterm

def dashboard():
    print(r"""
··············································································
: ________  ___  ___  ________  ________  ________                           :
:|\   __  \|\  \|\  \|\   ____\|\   ____\|\   __  \                          :
:\ \  \|\ /\ \  \\\  \ \  \___|\ \  \___|\ \  \|\  \                         :
: \ \   __  \ \  \\\  \ \_____  \ \  \    \ \   __  \                        :
:  \ \  \|\  \ \  \\\  \|____|\  \ \  \____\ \  \ \  \                       :
:   \ \_______\ \_______\____\_\  \ \_______\ \__\ \__\                      :
:    \|_______|\|_______|\_________\|_______|\|__|\|__|                      :
:                       \|_________|                                         :
:                                                                            :
:                                                                            :
:                     _____ ______   ___  ________   ________  ________      :
:                    |\   _ \  _   \|\  \|\   ___  \|\   __  \|\   ____\     :
:                    \ \  \\\__\ \  \ \  \ \  \\ \  \ \  \|\  \ \  \___|_    :
:                     \ \  \\|__| \  \ \  \ \  \\ \  \ \   __  \ \_____  \   :
:                      \ \  \    \ \  \ \  \ \  \\ \  \ \  \ \  \|____|\  \  :
:                       \ \__\    \ \__\ \__\ \__\\ \__\ \__\ \__\____\_\  \ :
:                        \|__|     \|__|\|__|\|__| \|__|\|__|\|__|\_________\:
:                                                                \|_________|:
··············································································

          """)

def menu():
    # Iniciar música en un hilo separado
    while True :
        clearterm()
        dashboard()
        print("[ 1 Solo Jugador ]")
        print("[ 2 Jugadores Online]")
        print("[ 3 Ver Rankings ]")
        print("[ 0 Salir]")
        opcion = input("Ingrese Opcion : ").strip() #.strip() Elimina Espacion restante
        sltc_menu(opcion)


        if opcion=='0':
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
                while True:
                    mines = int(input("Minas: "))
                    if mines < rows * cols:
                        break
                    print(f"El número de minas no puede ser mayor o igual al número de casillas ({rows * cols}).")
                one_player.start_game(rows, cols, mines)
            except ValueError:
                print("Entrada inválida. Por favor ingrese números.")
                input("Presione Enter para continuar...")
    elif opc == '2':
        host = input("Ingrese la IP del servidor (ej. localhost o 192.168.1.100): ").strip()
        port = input("Ingrese el puerto del servidor (ej. 12345): ").strip()
        try:
            port = int(port)
            # Iniciar el modo multijugador
            clearterm()
            dashboard()
            print("Seleccione tamano del Tablero:")
            print("1. 8x8 (10 Minas)")
            print("2. 10x10 (20 Minas)")
            print("3. Personalizado")
            opc_menu = input("Ingrese Opcion : ").strip()

            if opc_menu == '1':
                multiplayer.start_multiplayer(host, port, 8, 8, 10)
            elif opc_menu == '2':
                multiplayer.start_multiplayer(host, port, 10, 10, 20)
            elif opc_menu == '3':
                try:
                    rows = int(input("Filas: "))
                    cols = int(input("Columnas: "))
                    while True:
                        mines = int(input("Minas: "))
                        if mines < rows * cols:
                            break
                        print(f"El número de minas no puede ser mayor o igual al número de casillas ({rows * cols}).")
                    multiplayer.start_multiplayer(host, port, rows, cols, mines)
                except ValueError:
                    print("Entrada inválida. Por favor ingrese números.")
                    input("Presione Enter para continuar...")

        except ValueError:
            print("Puerto inválido. Por favor ingrese un número.")
            input("Presione Enter para continuar...")
    elif opc == '3':
        clearterm()
        rankings.show_rankings()
        input("\nPresione Enter para volver al menú...")
