import os
import one_player 

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
        opcion = input("Ingrese Opcion : ").strip() #.strip() Elimina Espacion restante
        sltc_menu(opcion)
        if opcion=='0':
            break

def sltc_menu(opc):

    if opc == '1':
        print("Mostraria Juego ")
