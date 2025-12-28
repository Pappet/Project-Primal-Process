"""
main.py - Das Interface für Project Primal.
Verarbeitet Benutzerbefehle und steuert den Game-Loop.
"""
import sys
import os
from engine.core import GameEngine

def clear_screen():
    # Hilfsfunktion für ein sauberes Terminal
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(game):
    loc = game.current_location
    print("=" * 50)
    print(f" PROJECT PRIMAL [Alpha 0.1] | Tick: {game.tick_counter}")
    print(f" ORT: {loc.name}")
    print(f" ENERGIE: {int(game.player.energy)} kcal | HP: {int(game.player.hp)}")
    print("=" * 50)

def handle_experiment(game):
    """Der interaktive Modus zum Kombinieren von Items."""
    print("\n[ EXPERIMENTIER-MODUS ]")
    print("Wähle die Komponenten für dein Vorhaben aus (z.B. 0, 2, 3).")
    
    items = game.player.inventory.items
    if not items:
        print("Dein Inventar ist leer.")
        return

    for i, item in enumerate(items):
        attrs = ", ".join([f"{k}:{v}" for k, v in item.attributes.items()])
        print(f"[{i}] {item.quantity}x {item.name} | Tags: {list(item.tags.keys())} | {attrs}")

    try:
        raw_input = input("\nIDs (mit Komma getrennt) oder [c]ancel > ").lower().strip()
        if raw_input == 'c': return

        indices = [int(x.strip()) for x in raw_input.split(",")]
        # Wir wählen die Items aus
        selected_items = [items[i] for i in indices]
        
        print(f"\nDu versuchst {', '.join([it.name for it in selected_items])} zu kombinieren...")
        
        # Aufruf der Engine-Logik für das Experiment
        result = game.execute_experiment(selected_items)
        
        if result["success"]:
            print(f"ERFOLG: {result['message']}")
        else:
            print(f"FEHLGESCHLAGEN: {result['message']}")

    except (ValueError, IndexError):
        print("Ungültige Auswahl.")

def main():
    game = GameEngine()
    
    while True:
        clear_screen()
        print_header(game)
        print(f"Beschreibung: {game.current_location.description}")
        
        print("\nBefehle:")
        print("[g]ather      - Die Umgebung absuchen")
        print("[e]xperiment  - Items kombinieren / Crafting")
        print("[i]nventory   - Rucksack ansehen")
        print("[t]ravel      - Den Ort wechseln")
        print("[q]uit        - Spiel beenden")

        cmd = input("\nPrimal > ").lower().strip()

        if cmd == 'q':
            break
        elif cmd == 'g':
            results = game.gather()
            print("\n".join(results))
            input("\nWeiter mit Enter...")
        elif cmd == 'i':
            print("\n--- INVENTAR ---")
            print(game.player.inventory.list_contents())
            print(f"Gesamtgewicht: {game.player.inventory.current_weight:.1f} kg")
            input("\nWeiter mit Enter...")
        elif cmd == 'e':
            handle_experiment(game)
            input("\nWeiter mit Enter...")
        elif cmd == 't':
            print("\nVerfügbare Orte: forest_edge, river_bank")
            dest = input("Wohin reisen? > ")
            print(game.travel(dest))
            input("\nWeiter mit Enter...")
        else:
            print("Unbekannter Befehl.")

if __name__ == "__main__":
    main()