"""
main.py
"""
import os
from engine.core import GameEngine

def main():
    game = GameEngine()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        loc = game.current_location
        print(f"--- {loc.name} | Tick: {game.tick_counter} | Energie: {int(game.player.energy)} ---")
        print(f"{loc.description}\n")
        print("[g]ather, [e]xperiment, [i]nventory, [t]ravel, [q]uit")
        
        cmd = input("> ").lower()
        if cmd == 'q': break
        if cmd == 'g':
            for line in game.gather(): print(f"  {line}")
            input("\nWeiter...")
        if cmd == 'i':
            for i, it in enumerate(game.player.inventory.items):
                print(f"[{i}] {it.name} | Zustand: {int(it.condition*100)}% | Tags: {list(it.tags.keys())}")
            input("\nWeiter...")
        if cmd == 'e':
            # Vereinfachte Auswahl für das Experiment
            idx_str = input("IDs (z.B. 0,1,2) > ")
            try:
                sel = [game.player.inventory.items[int(i)] for i in idx_str.split(",")]
                res = game.execute_experiment(sel)
                print(res["message"])
            except: print("Fehler bei Auswahl.")
            input("\nWeiter...")
        if cmd == 't':
            dest = input("Ziel (forest_edge, river_bank) > ")
            print(game.travel(dest))
            input("\nWeiter...")

if __name__ == "__main__": main()