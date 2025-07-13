import json
import os
from datetime import datetime

RANKING_FILE = "rankings.json"

def save_score(score, mode, time_elapsed):
    """Guarda puntuación en archivo JSON"""
    entry = {
        "score": score,
        "mode": mode,
        "time": time_elapsed,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    rankings = []
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r') as f:
            try:
                rankings = json.load(f)
            except:
                rankings = []
    
    rankings.append(entry)
    # Ordenar por puntuación descendente
    rankings.sort(key=lambda x: x["score"], reverse=True)
    # Mantener solo top 10
    rankings = rankings[:10]
    
    with open(RANKING_FILE, 'w') as f:
        json.dump(rankings, f, indent=2)

def show_rankings():
    """Muestra el top 10 de puntuaciones"""
    if not os.path.exists(RANKING_FILE):
        print("No hay registros aún")
        return
    
    with open(RANKING_FILE, 'r') as f:
        try:
            rankings = json.load(f)
        except:
            print("Error al leer el archivo de rankings.")
            return
    
    print("\n🏆 TOP 10 PUNTUACIONES 🏆")
    print("Pos. Puntos  Tiempo  Modo        Fecha")
    print("─────────────────────────────────────────")
    for i, entry in enumerate(rankings, 1):
        print(f"{i:2}. {entry['score']:6}  {entry['time']:>5}s  {entry['mode']:10}  {entry['date']}")