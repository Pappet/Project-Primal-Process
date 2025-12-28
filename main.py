"""
main.py
"""
import os
from engine.core import GameEngine

def main():
    game = GameEngine()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        p = game.player
        loc = game.current_location
        amb_temp = game._get_ambient_temp()

        print(f"--- {loc.name} | Wetter: {game.current_weather} ---")
        print(f"Umgebung: {amb_temp:.1f}°C | Körper: {p.body_temp:.1f}°C")
        print(f"HP: {int(p.hp)}/100 | ENERGIE: {int(p.energy)}/1000 | Survival: {p.stats['survival']:.1f}")
        print("-" * 50)
        print("[g]ather, [e]xperiment, [f]eed, [k]nowledge, [i]nventory, [t]ravel, [q]uit")

        if p.hp <= 0:
            print("\n!!! DU BIST VERHUNGERT. GAME OVER !!!")
            break
            
        cmd = input("> ").lower().strip()
        if cmd == 'q': break
        
        if cmd == 'g':
            for line in game.gather(): print(f"  {line}")
            input("\nWeiter...")
            
        elif cmd == 'f':
            print("\nWas möchtest du essen?")
            for i, it in enumerate(p.inventory.items):
                if "EDIBLE" in it.tags:
                    print(f"[{i}] {it.name} (+{it.tags['EDIBLE']} Energie)")
            try:
                idx = int(input("Index > "))
                print(game.eat(idx))
            except: print("Ungültig.")
            input("\nWeiter...")

        elif cmd == 'i':
            print("\n--- INVENTAR ---")
            for i, it in enumerate(p.inventory.items):
                print(f"[{i}] {it.quantity}x {it.name} ({int(it.condition*100)}%) | Tags: {list(it.tags.keys())}")
            input("\nWeiter...")

        elif cmd == 'e':
            idx_str = input("IDs (z.B. 0,1,2) > ")
            try:
                sel = [p.inventory.items[int(i)] for i in idx_str.split(",")]
                res = game.execute_experiment(sel)
                print(f"\n{res['message']}")
            except: print("Fehler bei Auswahl.")
            input("\nWeiter...")

        elif cmd == 'k':
            print("\n--- BEKANNTE BAUPLÄNE ---")
            for bid in p.known_blueprints:
                bp = game.blueprints[bid]
                print(f"- {bp.result_name} ({list(bp.slots.values())})")
            input("\nWeiter...")

        elif cmd == 't':
            print("\n--- VERFÜGBARE ORTE ---")
            # Wir iterieren über alle Location-Objekte im Dictionary
            for loc_id, loc_obj in game.locations.items():
                # Wir zeigen den Namen und in Klammern die ID an, die man tippen muss
                print(f"- {loc_obj.name} (ID: {loc_id})")
            
            dest = input("\nWohin möchtest du reisen? (ID eingeben) > ").strip()
            # Die travel-Methode verarbeitet die ID und berechnet die Zeit
            result_msg = game.travel(dest)
            print(f"\n{result_msg}")
            input("\nWeiter mit Enter...")

if __name__ == "__main__": main()