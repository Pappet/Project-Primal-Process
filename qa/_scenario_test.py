"""
New-Player-Szenario & Edge-Case-Testing für Primal Process.
Simuliert eine naive Spieler-Session und testet Grenzfälle.
"""
import sys, random
sys.path.insert(0, '.')

from engine.core import GameEngine
from engine.components import Item
from data.items import create_item

random.seed(12345)

def header(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")

# ============================================================
header("NEW-PLAYER-SZENARIO: Naiver Erstkontakt")
# ============================================================
print("""
Szenario: Spieler startet ohne Anleitung. Weiss nichts über Tags,
Blueprints oder Locations. Versucht intuitiv zu handeln.
""")

game = GameEngine()
actions_taken = 0
craft_success = False

# --- Phase 1: Exploration ---
print("\n--- Phase 1: Was kann ich tun? ---")
print(f"Start: Energie={game.player.energy}, HP={game.player.hp}, "
      f"Ort={game.current_location.name}")

# Versuche zu sammeln
for i in range(5):
    actions_taken += 1
    logs = game.gather()
    inv = [f"{it.name} x{it.quantity}" for it in game.player.inventory.items]
    print(f"  Gather #{i+1}: {logs} | Inventar: {inv} | Energie: {game.player.energy:.0f}")

print(f"\nNach 5x gather: {len(game.player.inventory.items)} Item-Typen, "
      f"Energie={game.player.energy:.0f}")

# Versuche blind zu craften
print("\n--- Phase 2: Blindes Craften ---")
items = game.player.inventory.items[:]
if len(items) >= 2:
    # Versuche 2 sticks zu kombinieren
    actions_taken += 1
    result = game.execute_experiment([items[0], items[0]] if len(items) >= 2 else [items[0]])
    print(f"  Craft 2x Ast: {result}")

if len(items) >= 3:
    actions_taken += 1
    result = game.execute_experiment([items[0], items[0], items[0]])
    print(f"  Craft 3x Ast: {result}")

# Reise zum Gipfelkamm (vielleicht gibt's da mehr?)
print("\n--- Phase 3: Reise ---")
actions_taken += 1
msg = game.travel("mountain_peak")
print(f"  Travel → Gipfelkamm: {msg.strip()}")

# Sammle am Gipfelkamm
for i in range(5):
    actions_taken += 1
    logs = game.gather()
    inv = [f"{it.name} x{it.quantity}" for it in game.player.inventory.items]
    print(f"  Gather #{i+1} @ Gipfel: {logs} | Inventar: {inv} | Energie: {game.player.energy:.0f}")

print(f"\nNach Erkundung: {len(game.player.inventory.items)} Item-Typen im Inventar")
print(f"Energie: {game.player.energy:.0f}, HP: {game.player.hp:.0f}, Temp: {game.player.body_temp:.1f}°C")

# Versuche erneut zu craften mit allen Items
print("\n--- Phase 4: Craft-Versuche mit gemischten Items ---")
all_items = game.player.inventory.items[:]
if len(all_items) >= 2:
    for combo_size in [2, 3]:
        if len(all_items) >= combo_size:
            actions_taken += 1
            combo = all_items[:combo_size]
            result = game.execute_experiment(combo)
            print(f"  Craft {combo_size} items: {result}")
            if result.get("success"):
                craft_success = True

# Verzweifeltes Essen
print("\n--- Phase 5: Verzweifeltes Essen ---")
for idx, item in enumerate(game.player.inventory.items[:]):
    if item.quantity > 0:
        actions_taken += 1
        msg = game.eat(idx)
        print(f"  eat({idx}) = {item.name}: {msg}")
        if "nicht essbar" not in msg and "Ungültig" not in msg:
            break

print(f"\n=== NEW-PLAYER SUMMARY ===")
print(f"Aktionen bis erstes Craft: {actions_taken}")
print(f"Craft erfolgreich: {craft_success}")
print(f"End-Energie: {game.player.energy:.0f}")
print(f"End-HP: {game.player.hp:.0f}")
print(f"End-Temp: {game.player.body_temp:.1f}°C")

# ============================================================
header("EDGE-CASE-HUNTING")
# ============================================================

# --- Edge Case 1: Drei gleiche Items craften ---
print("\n--- Edge: 3x gleiches Item ---")
g1 = GameEngine()
for _ in range(3):
    g1.player.inventory.add(create_item("stick", 1))
items = g1.player.inventory.items[:3]
result = g1.execute_experiment(items)
print(f"  3x Stick craften: success={result['success']}, msg='{result['message']}'")
print(f"  Erwartet: FAIL (kein Blueprint mit 3x RIGID), Tatsächlich: {'FAIL' if not result['success'] else 'PASS (unerwartet)'}")

# --- Edge Case 2: Leeres Inventar + eat() ---
print("\n--- Edge: Leeres Inventar eat() ---")
g2 = GameEngine()
msg = g2.eat(0)
print(f"  eat(0) auf leerem Inventar: '{msg}'")

# --- Edge Case 3: travel() zu nicht-existenter Location ---
print("\n--- Edge: travel() zu nicht-existenter Location ---")
g3 = GameEngine()
msg = g3.travel("narnia")
print(f"  travel('narnia'): '{msg}'")

# --- Edge Case 4: execute_experiment() mit 0, 1, 10 Items ---
print("\n--- Edge: execute_experiment() mit verschiedenen Item-Anzahlen ---")
g4 = GameEngine()

# 0 Items
result = g4.execute_experiment([])
print(f"  0 Items: {result}")

# 1 Item
g4.player.inventory.add(create_item("stick", 1))
result = g4.execute_experiment([g4.player.inventory.items[0]])
print(f"  1 Item (Stick): {result}")

# 10 Items (füge 10 Sticks hinzu)
g5 = GameEngine()
sticks = [create_item("stick", 1) for _ in range(10)]
for s in sticks:
    g5.player.inventory.add(s)
result = g5.execute_experiment(sticks)
print(f"  10 Items (10x Stick): {result}")

# --- Edge Case 5: 20x gather() — Endlos/ Balance-Check ---
print("\n--- Edge: 20x gather() hintereinander ---")
g6 = GameEngine()
random.seed(999)
for i in range(20):
    logs = g6.gather()
    if i < 3 or i >= 17:
        print(f"  Gather #{i+1}: {logs} | Energie: {g6.player.energy:.0f}, HP: {g6.player.hp:.0f}, Temp: {g6.player.body_temp:.1f}")
print(f"  ... (14 gathers omitted)")
print(f"  Final: Energie={g6.player.energy:.0f}, HP={g6.player.hp:.0f}, Temp={g6.player.body_temp:.1f}")
print(f"  Items gathered: {[(it.name, it.quantity) for it in g6.player.inventory.items]}")
print(f"  Wetter: {g6.current_weather}")

# --- Edge Case 6: Spieler hat 1 HP — eat() mit falschem Item ---
print("\n--- Edge: 1 HP + eat() mit nicht-essbarem Item ---")
g7 = GameEngine()
g7.player.hp = 1.0
g7.player.inventory.add(create_item("stick", 1))
msg = g7.eat(0)
print(f"  HP=1.0, eat(Stick): '{msg}', HP nachher={g7.player.hp}")

# --- Edge Case 7: execute_experiment() mit kaputten Items (condition=0) ---
print("\n--- Edge: execute_experiment() mit condition=0 Items ---")
g8 = GameEngine()
bad_stick = create_item("stick", 1)
bad_stick.condition = 0.0
bad_flint = create_item("flint_shard", 1)
bad_flint.condition = 0.0
bad_fiber = create_item("plant_fiber", 1)
bad_fiber.condition = 0.0
g8.player.inventory.add(bad_flint)
g8.player.inventory.add(bad_stick)
g8.player.inventory.add(bad_fiber)
result = g8.execute_experiment([bad_flint, bad_stick, bad_fiber])
print(f"  Craft mit condition=0 Items: {result}")
if result["success"]:
    crafted = g8.player.inventory.items
    print(f"  Resultierendes Item: {[(it.name, it.condition) for it in crafted]}")

# --- Edge Case 8: 2x travel → Hypothermie-Tod ---
print("\n--- Edge: Rapid Travel → Hypothermia ---")
g9 = GameEngine()
for i in range(4):
    # travel zwischen zwei Locations
    target = "mountain_peak" if i % 2 == 0 else "forest_edge"
    msg = g9.travel(target)
    if i < 4:
        print(f"  Travel #{i+1} → {target}: HP={g9.player.hp:.1f}, Temp={g9.player.body_temp:.1f}")

# --- Edge Case 9: Energy bei 0 — was passiert? ---
print("\n--- Edge: Energy=0, weitere Aktionen ---")
g10 = GameEngine()
g10.player.energy = 0.0
g10.player.hp = 10.0  # noch lebendig
logs = g10.gather()
print(f"  gather() bei Energy=0: HP={g10.player.hp:.1f}, Energy={g10.player.energy:.0f}, logs={logs}")

# --- Edge Case 10: eat() letztes Item eines Stacks ---
print("\n--- Edge: eat() letztes Item eines Stacks ---")
g11 = GameEngine()
berry = create_item("berries", 1)  # quantity=1
g11.player.inventory.add(berry)
print(f"  Vor eat: {len(g11.player.inventory.items)} Items")
msg = g11.eat(0)
print(f"  eat(berry x1): '{msg}'")
print(f"  Nach eat: {len(g11.player.inventory.items)} Items (sollte 0 sein)")

print("\n" + "="*60)
print("  EDGE-CASE-HUNTING COMPLETE")
print("="*60)