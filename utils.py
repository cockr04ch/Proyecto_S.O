import os

def clearterm():
    """Limpia la terminal, compatible con Windows y Linux/Mac."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
