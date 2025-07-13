import client

def start_multiplayer(host, port, rows, cols, mines):
    game_client = client.GameClient(host, port, rows, cols, mines)
    game_client.start()
