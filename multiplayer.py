import client

def start_multiplayer(host, port):
    game_client = client.GameClient(host, port)
    game_client.start()
