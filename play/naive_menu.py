"""Profil C — Menü-naiver Spieler (B10-Menürest, PLAN T3/T4).

Ein Spieler, der NUR die Menü-Verben aus main.py kennt: gather, eat,
experiment, process, travel, [w]ärmen, [r]asten. Kein Rezept-Wissen, kein
Engine-Interna-Zugriff: er reagiert auf die Log-Zeilen, die main.py im
Terminal zeigen würde (SPEC-014-Hinweise, Prozess-Hinweise, FIRE_OUT) und
nimmt Prozesse aus `available_processes()`, die das Menü namentlich listet.

Kein stoke_fire()-Direktruf an Stellen, die ein Menü-Spieler nicht sehen
würde: [w] wird gedrückt, wenn der sichtbare Stream das Feuer schwach
meldet (SPEC-014) oder das Feuer gerade ausging (FIRE_OUT-Zeile).

Repert die Menü-Lesung (14.09.: 20/20 Kälte-Tode, 200 Aktionen, 20 Seeds)
als committetes Messwerkzeug — kein /tmp-Wegwerfcode mehr (PLAN T4).
Ziel explorativ: Tode deutlich unter 20/20 nach T1/T2/SPEC-014/016.

Aufruf:  python play/naive_menu.py [--seeds 20] [--actions 200]
Deterministisch: Seed-Satz wie tools/scorecard.py (BASE_SEED + i).
"""
import sys, argparse
sys.path.insert(0, ".")
from engine.core import GameEngine

BASE_SEED = 20260803

FIRE_DYING = "Das Feuer wird schwach"
COLD_HINT = "Die Kälte nagt"
FIRE_OUT_MARK = "FIRE_OUT"

LOC_CYCLE = ["forest_edge", "hilltop", "hidden_cave", "forest_edge",
             "hilltop", "hidden_cave"]  # naive Wander-Routine, fixe Reihenfolge


def _edible_index(game):
    for i, it in enumerate(game.player.inventory.items):
        if "EDIBLE" in it.tags and it.template_id != "raw_meat":
            return i
    return None


def _step(game, action_no, last_logs, stats):
    """EIN Menü-Zug. Liefert die Ausgabezeilen der gewählten Aktion."""
    # 1. Essen bei Hunger (Menü [f])
    idx = _edible_index(game)
    if idx is not None and game.player.energy < 200:
        return [game.eat(idx)]
    # 2. Feuer schwach sichtbar → [w]ärmen (SPEC-014-Affordance)
    if FIRE_DYING in last_logs and game.current_location.fire_active:
        res = game.stoke_fire()
        stats["stokes"] += 1
        if res["success"]:
            stats["stokes_ok"] += 1
        return [res["message"]]
    # 3. Feuer aus sichtbar → nachlegen versuchen ([w] mit Holz im Inventar)
    if FIRE_OUT_MARK in last_logs:
        res = game.stoke_fire()
        if res["success"]:
            stats["revives"] += 1
            return [res["message"]]
        return [game.gather(), ]  # naives Ressourcen-Beschaffen
    # 4. Kälte-Hinweis sichtbar → zum warmen Ort (Menü [t], der Spieler
    #    kennt Orte nur vom Umherlaufen; forest_edge ist sein Start)
    if COLD_HINT in last_logs and game.current_location_id != "forest_edge":
        return [game.travel("forest_edge")]
    # 5. Rotations-Routine: gelegentlich experiment / wandern / rasten
    if action_no % 5 == 4:
        sel, seen = [], set()
        for it in game.player.inventory.items:
            if it.template_id not in seen and it.quantity > 0:
                sel.append(it); seen.add(it.template_id)
            if len(sel) == 3:
                break
        if len(sel) >= 2:
            res = game.execute_experiment(sel)
            return [res["message"]]
    if action_no % 7 == 6:
        dest = LOC_CYCLE[(action_no // 7) % len(LOC_CYCLE)]
        return [game.travel(dest)]
    if action_no % 11 == 10:
        res = game.rest()
        return [res["message"]]
    return list(game.gather())


def run_profile_c(seed, max_actions=200):
    """Ein Menü-naiver Run. Liefert die Lesungs-Zahlen."""
    random_state = __import__("random")
    random_state.seed(seed)
    game = GameEngine()
    stats = {"stokes": 0, "stokes_ok": 0, "revives": 0, "fire_outs": 0,
             "cold_ticks": 0, "last_new": 0}
    known = set()
    logs = []
    first_craft = None
    death_at = None

    def snapshot():
        s = set(game.player.known_blueprints) | set(game.player.known_processes)
        s |= {it.template_id or it.name for it in game.player.inventory.items}
        return s

    for a in range(1, max_actions + 1):
        if game.player.hp <= 0:
            death_at = a
            break
        before = snapshot()
        # sichtbare Logzeilen des letzten Zugs (was main.py anzeigen würde)
        lines = []
        for chunk in logs:
            if isinstance(chunk, list):
                lines.extend(chunk)
            else:
                lines.extend(str(chunk).split("\n"))
        try:
            out = _step(game, a, "\n".join(lines), stats)
        except Exception as e:               # Bot-Fehler zählt als Aktion
            out = [f"<bot-error: {e}>"]
        stats["fire_outs"] += sum(FIRE_OUT_MARK in str(x) for x in out)
        if game.player.body_temp < 35.0:
            stats["cold_ticks"] += 1
        after = snapshot()
        if after - before:
            stats["last_new"] = a
            if not first_craft and (game.player.known_blueprints
                                    | game.player.known_processes) - known:
                first_craft = a
        known = after
        logs = out
    return {"seed": seed, "died": death_at is not None, "death_at": death_at,
            "first_craft": first_craft, "bps": len(game.player.known_blueprints),
            "procs": len(game.player.known_processes),
            "last_new": stats["last_new"], "hp": game.player.hp,
            "bt_min": round(game.player.body_temp, 1), **stats}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--actions", type=int, default=200)
    args = ap.parse_args()

    runs = [run_profile_c(BASE_SEED + i, args.actions) for i in range(args.seeds)]
    deaths = [r for r in runs if r["died"]]
    lastnews = sorted(r["last_new"] for r in runs)
    median_ln = lastnews[len(lastnews) // 2]

    def med(xs):
        s = sorted(xs); return s[len(s) // 2]

    print(f"Profil C (Menü-naiv): {len(runs)} Seeds, {args.actions} Aktionen")
    print(f"  Kälte-Tode: {len(deaths)}/{len(runs)}"
          + (f" @Aktion {[r['death_at'] for r in deaths]}" if deaths else ""))
    print(f"  first_craft: median {med([r['first_craft'] or 999 for r in runs])}")
    print(f"  last_new: median {median_ln}, "
          f"min {lastnews[0]}, max {lastnews[-1]}  ← Langeweile-Stelle")
    print(f"  Ende: bps median {med([r['bps'] for r in runs])}, "
          f"procs median {med([r['procs'] for r in runs])}")
    print(f"  Feuer: FIRE_OUTs median {med([r['fire_outs'] for r in runs])}, "
          f"Stokes median {med([r['stokes'] for r in runs])}, "
          f"Revives median {med([r['revives'] for r in runs])}")
    print(f"  Kälte-Ticks median {med([r['cold_ticks'] for r in runs])}")
    for r in runs[:5]:
        print(f"    seed {r['seed']}: died={r['died']} @{r['death_at']} "
              f"hp={int(r['hp'])} bps={r['bps']} procs={r['procs']} "
              f"last_new={r['last_new']}")


if __name__ == "__main__":
    main()
