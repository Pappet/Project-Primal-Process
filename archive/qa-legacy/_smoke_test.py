"""
QA Smoke-Test für Project Primal Process Engine.
Testet grundlegende Operationen und Edge Cases.
Läuft als Teil des wöchentlichen Playtest-Cron-Jobs.
"""
import sys
import random
sys.path.insert(0, '.')

from engine.core import GameEngine
from engine.components import Item

# Für reproduzierbare Tests
random.seed(42)

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    return condition

results = {"pass": 0, "fail": 0, "notes": []}

# ============================================================
section("1. SMOKE-TEST: Engine-Instantiation")
# ============================================================
game = GameEngine()

check(game.player.name == "Survivor", "Player name is 'Survivor'")
check(game.player.hp == 100.0, f"Player HP = {game.player.hp}")
check(game.player.max_hp == 100.0, f"Player max_hp = {game.player.max_hp}")
check(game.player.energy == 800.0, f"Player energy = {game.player.energy}")
check(game.player.max_energy == 1000.0, f"Player max_energy = {game.player.max_energy}")
check(game.player.body_temp == 37.0, f"Player body_temp = {game.player.body_temp}")
check(len(game.player.inventory.items) == 0, "Inventory empty at start")
check(game.current_location_id == "forest_edge", "Start location is forest_edge")
check(game.current_location.name == "Waldrand", f"Location name: {game.current_location.name}")

# Check stats
check(game.player.stats["perception"] == 1.0, f"perception = {game.player.stats['perception']}")
check(game.player.stats["survival"] == 1.0, f"survival = {game.player.stats['survival']}")
check(game.player.stats["strength"] == 1.0, f"strength = {game.player.stats['strength']}")

# ============================================================
section("2. SMOKE-TEST: gather()")
# ============================================================
game2 = GameEngine()
random.seed(42)
logs = game2.gather()
check(isinstance(logs, list), "gather() returns list")
check(len(logs) > 0, f"gather() produced logs: {logs}")

# Check what was gathered — at forest_edge, perception=1.0, only sticks are findable
# (berries need perception 2.0, log_oak needs CHOPPING tool)
items = game2.player.inventory.items
item_names = [i.name for i in items]
print(f"  Inventory after gather: {item_names} (qty: {[i.quantity for i in items]})")
check(any("Eichenast" in n for n in item_names), "Found sticks (Eichenast)")

# Energy drain: 5.0 * 2.0 * 1 = 10
check(game2.player.energy == 790.0, f"Energy after 1 gather = {game2.player.energy} (expected 790)")

# ============================================================
section("3. SMOKE-TEST: eat()")
# ============================================================
game3 = GameEngine()
random.seed(42)

# Give player a berry directly for testing
from data.items import create_item
berry = create_item("berries", 3)
game3.player.inventory.add(berry)

# Eat valid edible
item_idx = 0
msg = game3.eat(item_idx)
check("Du isst" in msg, f"eat() success message: {msg}")
check(game3.player.energy > 800.0, f"Energy after eating: {game3.player.energy}")

# Eat non-edible (stick)
stick = create_item("stick", 1)
game3.player.inventory.add(stick)
msg2 = game3.eat(1)  # stick is at index 1 now
check("nicht essbar" in msg2, f"eat() rejects non-edible: {msg2}")

# Eat invalid index
msg3 = game3.eat(99)
check("Ungültiges Item" in msg3, f"eat() rejects invalid index: {msg3}")

# Eat empty inventory
game4 = GameEngine()
msg4 = game4.eat(0)
check("Ungültiges Item" in msg4, f"eat() on empty inventory: {msg4}")

# ============================================================
section("4. SMOKE-TEST: travel()")
# ============================================================
game5 = GameEngine()

# Valid travel
msg = game5.travel("mountain_peak")
check("Gereist nach Gipfelkamm" in msg, f"travel() to mountain_peak: {msg}")
check(game5.current_location_id == "mountain_peak", "Location updated to mountain_peak")

# Energy drain: 5.0 * 1.5 * 3 = 22.5
check(game5.player.energy == 777.5, f"Energy after travel = {game5.player.energy} (expected 777.5)")

# Invalid travel
msg2 = game5.travel("atlantis")
check("Unbekannt" in msg2, f"travel() to invalid location: {msg2}")

# travel() to current location
msg3 = game5.travel("mountain_peak")
check("Gereist nach Gipfelkamm" in msg3, f"travel() to same location: {msg3}")

# ============================================================
section("5. SMOKE-TEST: execute_experiment()")
# ============================================================
game6 = GameEngine()
random.seed(42)

# Create axe ingredients: flint_shard (HARD+SHARP) + stick (RIGID) + plant_fiber (FIBER)
flint = create_item("flint_shard", 1)
stick = create_item("stick", 1)
fiber = create_item("plant_fiber", 1)
game6.player.inventory.add(flint)
game6.player.inventory.add(stick)
game6.player.inventory.add(fiber)

result = game6.execute_experiment([flint, stick, fiber])
check(result["success"] == True, f"execute_experiment() axe craft: {result}")
check("Hergestellt" in result["message"], f"Craft message: {result['message']}")
check(len(game6.player.inventory.items) == 1, f"Inventory has 1 item after craft (had 3, consumed 3, created 1)")
check("axe" in game6.player.known_blueprints, "Axe blueprint now known")

# Craft knife: flint (SHARP) + stick (RIGID) — only 2 items, no FIBER needed
game7 = GameEngine()
flint2 = create_item("flint_shard", 1)
stick2 = create_item("stick", 1)
game7.player.inventory.add(flint2)
game7.player.inventory.add(stick2)

result2 = game7.execute_experiment([flint2, stick2])
check(result2["success"] == True, f"execute_experiment() knife craft: {result2}")
check("Hergestellt" in result2["message"], f"Knife message: {result2['message']}")

# Failed experiment with wrong items (3 sticks)
game8 = GameEngine()
s1 = create_item("stick", 1)
s2 = create_item("stick", 1)
s3 = create_item("stick", 1)
game8.player.inventory.add(s1)
game8.player.inventory.add(s2)
game8.player.inventory.add(s3)

result3 = game8.execute_experiment([s1, s2, s3])
check(result3["success"] == False, f"execute_experiment() with 3 sticks fails: {result3}")
check("Nichts passiert" in result3["message"], f"Fail message: {result3['message']}")

print(f"\n{'='*60}")
print(f"  SMOKE-TEST RESULTS: {results['pass']} passed, {results['fail']} failed")
print(f"{'='*60}")

if results["fail"] > 0:
    sys.exit(1)