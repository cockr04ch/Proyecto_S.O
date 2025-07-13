import client
from utils import clearterm
import os
import server
import threading
import time

def start_multiplayer(host, port, rows, cols, mines):
    clearterm()
    print("1. Crear partida (serás el anfitrión)")
    print("2. Unirse a una partida")
    choice = input("Opción: ").strip()
    
    if choice == '1':
        try:
            # Iniciar el servidor en un hilo separado
            game_server = server.GameServer(host, port)
            server_thread = threading.Thread(target=game_server.start)
            server_thread.daemon = True
            server_thread.start()
            print(f"Servidor local iniciado en {host}:{port}.")
            time.sleep(0.5)

            # Conectar el cliente anfitrión
            game_client = client.GameClient(host, port)
            action = {'type': 'create', 'rows': rows, 'cols': cols, 'mines': mines}
            game_client.start(action)

        except (ConnectionRefusedError, OSError) as e:
            print(f"Error de conexión: {e}")
            print("Asegúrate de que la IP y el puerto son correctos y no están en uso por otro programa.")
            input("Presione Enter para continuar...")
        except Exception as e:
            print(f"Error inesperado al crear la partida: {e}")
            input("Presione Enter para continuar...")

    elif choice == '2':
        game_id = input("Ingrese el ID de la partida: ").strip()
        try:
            game_id = int(game_id)
            game_client = client.GameClient(host, port)
            action = {'type': 'join', 'game_id': game_id}
            game_client.start(action)
        except ValueError:
            print("El ID de la partida debe ser un número.")
            input("Presione Enter para continuar...")
        except (ConnectionRefusedError, OSError) as e:
            print(f"Error de conexión: {e}")
            print(f"No se pudo conectar al servidor en {host}:{port}. Verifica que la IP y el puerto son correctos y que el anfitrión ha iniciado la partida.")
            input("Presione Enter para continuar...")
        except Exception as e:
            print(f"Error inesperado al unirse a la partida: {e}")
            input("Presione Enter para continuar...")
    else:
        print("Opción inválida")
        input("Presione Enter para continuar...")