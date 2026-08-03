#!/usr/bin/env python3
"""tools/scorecard.py — Fitness-Signal für Project Primal Process.

Berechnet 7 messbare Eigenschaften des Spiels aus echten Playthroughs.
Nicht Prozesstreue, sondern das Spiel selbst ist das Signal.

- Stdlib only. Deterministisch (fester Seed-Satz). Läuft ohne Argumente.
- Simuliert echte GameEngine-Runs mit scripted/naiven Spielern.

Output:
  - scorecard/YYYY-MM-DD.json   (Rohwerte + Details)
  - scorecard/latest.json       (Kopie des aktuellsten Runs)
  - SCORECARD.md                (Markdown-Tabelle mit Delta zur Vorwoche)
"""
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.core import GameEngine              # noqa: E402
from data.items import TEMPLATE_DB              # noqa: E402
from data.blueprints import get_all_blueprints  # noqa: E402
from data.locations import get_all_locations    # noqa: E402
from data.loader import load_processes          # noqa: E402

BASE_SEED = 20260803
GENERIC_FEEDBACK = {"nichts passiert."}          # zählt NICHT als informativ
HORIZON = 500                                    # Tick-Cap für Überlebensmetriken
SCORECARD_DIR = ROOT / "scorecard"


# ----------------------------------------------------------------------------
# Spieler-Helfer
# ----------------------------------------------------------------------------

def _edible(game):
    return [it for it in game.player.inventory.items if "EDIBLE" in it.tags]


def _eat_best(game):
    eds = _edible(game)
    if not eds:
        return
    eds.sort(key=lambda it: it.tags["EDIBLE"], reverse=True)
    inv = game.player.inventory.items
    idx = inv.index(eds[0])
    game.eat(idx)


def _random_sel(game, rng, kmin=2):
    inv = [it for it in game.player.inventory.items if it.quantity >= 1]
    if len(inv) < kmin:
        return None
    k = rng.randint(kmin, min(3, len(inv)))
    sel = list(inv)
    rng.shuffle(sel)
    return sel[:k]


def _drain_check(game):
    return game.player.hp <= 0


# ----------------------------------------------------------------------------
# Metrik 1 — actions_to_first_craft
# ----------------------------------------------------------------------------

def metric_first_craft():
    """Aktionen bis zum ersten erfolgreichen Craft bei naivem Spiel."""
    random.seed(BASE_SEED + 1)
    rng = random.Random(BASE_SEED + 1)
    game = GameEngine()
    locs = list(game.locations.keys())
    actions = 0
    since_travel = 0
    while actions < 20000:
        actions += 1
        p = game.player
        if _drain_check(game):
            return None
        if p.energy < 150:
            _eat_best(game)
        if rng.random() < 0.45:
            if since_travel > 8:
                game.travel(locs[rng.randrange(len(locs))])
                since_travel = 0
            game.gather()
            since_travel += 1
        else:
            sel = _random_sel(game, rng, kmin=2)
            if sel:
                res = game.execute_experiment(sel)
                if res["success"]:
                    return actions
    return None


# ----------------------------------------------------------------------------
# Metrik 2 — blueprint_reachability
# ----------------------------------------------------------------------------

def _pair_slots(game, bp):
    """Findet je ein distinctes Item pro Slot-Tag, falls möglich."""
    inv = [it for it in game.player.inventory.items
           if it.quantity >= 1 and it.condition > 0]
    by_tag = {}
    for it in inv:
        for t in it.tags:
            by_tag.setdefault(t, []).append(it)
    slot_tags = [tag for _slot, tag in bp.slots.items()]
    candidates = [by_tag.get(tag, []) for tag in slot_tags]

    chosen = []

    def backtrack(i, used):
        if i == len(candidates):
            return True
        for it in candidates[i]:
            if id(it) in used:
                continue
            used.add(id(it))
            chosen.append(it)
            if backtrack(i + 1, used):
                return True
            used.remove(id(it))
            chosen.pop()
        return False

    if not backtrack(0, set()):
        return None
    return list(chosen)


def metric_reachability(n=50):
    """Anteil der Blueprints, die von frischem Start aus erreichbar sind."""
    bps = get_all_blueprints()
    loc_ids = [l.id for l in get_all_locations()]
    seen = {bp.id: 0 for bp in bps}
    for run in range(n):
        random.seed(BASE_SEED + 100 + run)
        game = GameEngine()
        for loc in loc_ids:
            game.travel(loc)
            for _ in range(8):
                game.gather()
        for bp in bps:
            sel = _pair_slots(game, bp)
            if sel and game.execute_experiment(sel)["success"]:
                seen[bp.id] += 1
    total = max(1, len(bps))
    value = sum(1 for v in seen.values() if v > 0) / total
    return {"value": round(value, 3),
            "per_blueprint": {k: (v > 0) for k, v in seen.items()}}


# ----------------------------------------------------------------------------
# Metrik 3 — craft_variety
# ----------------------------------------------------------------------------

def metric_craft_variety(actions=100):
    """Verschiedene erfolgreiche Crafts in N Aktionen."""
    seed = BASE_SEED + 200
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    results = set()
    done = 0
    while done < actions:
        if _drain_check(game):
            break
        done += 1
        if game.player.energy < 150:
            _eat_best(game)
        if rng.random() < 0.5:
            if rng.random() < 0.2:
                game.travel(locs[rng.randrange(len(locs))])
            game.gather()
        else:
            sel = _random_sel(game, rng, kmin=2)
            if sel:
                res = game.execute_experiment(sel)
                if res["success"]:
                    results.add(res["message"])
    return {"distinct_results": len(results), "value": len(results)}


# ----------------------------------------------------------------------------
# Metrik 4 — skill_spread
# ----------------------------------------------------------------------------

def _survival_optimal():
    random.seed(BASE_SEED + 300)
    game = GameEngine()
    while game.tick_counter < HORIZON:
        if _drain_check(game):
            break
        if game.current_location_id != "hidden_cave":
            game.travel("hidden_cave")
        if game.player.energy < 300:
            _eat_best(game)
        game.gather()
    return min(game.tick_counter, HORIZON)


def _survival_random():
    random.seed(BASE_SEED + 301)
    rng = random.Random(BASE_SEED + 301)
    game = GameEngine()
    locs = list(game.locations.keys())
    while game.tick_counter < HORIZON:
        if _drain_check(game):
            break
        r = rng.random()
        if r < 0.25:
            game.travel(locs[rng.randrange(len(locs))])
        elif r < 0.7:
            game.gather()
        else:
            if rng.random() < 0.5:
                _eat_best(game)
            if rng.random() < 0.3:
                sel = _random_sel(game, rng, kmin=1)
                if sel:
                    game.execute_experiment(sel)
    return min(game.tick_counter, HORIZON)


def metric_skill_spread():
    """Überlebenszeit optimal vs. zufällig — misst, ob Können etwas bringt."""
    opt = _survival_optimal()
    rnd = _survival_random()
    value = (opt - rnd) / opt if opt > 0 else 0.0
    return {"optimal_ticks": opt, "random_ticks": rnd,
            "value": round(value, 3)}


# ----------------------------------------------------------------------------
# Metrik 5 — feedback_quality
# ----------------------------------------------------------------------------

def metric_feedback_quality(steps=60):
    """Anteil der Aktionen mit informativer Rückmeldung."""
    seed = BASE_SEED + 400
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    total, informative = 0, 0
    for _ in range(steps):
        if _drain_check(game):
            break
        total += 1
        if rng.random() < 0.5:
            if rng.random() < 0.2:
                game.travel(locs[rng.randrange(len(locs))])
            msg = " ".join(game.gather()).strip()
            if msg:
                informative += 1
        else:
            sel = _random_sel(game, rng, kmin=1)
            res = game.execute_experiment(sel) if sel else \
                game.execute_experiment([])
            m = res["message"].strip().lower()
            if m and m not in GENERIC_FEEDBACK:
                informative += 1
    return {"value": round(informative / total, 3) if total else 0.0,
            "informative": informative, "total": total}


# ----------------------------------------------------------------------------
# Metrik 6 — content_reachable
# ----------------------------------------------------------------------------

def metric_content_reachable():
    """Anteil der definierten Items, die tatsächlich sammelbar sind."""
    defined = set(TEMPLATE_DB.keys())
    gather_ids = {node.result_template_id
                  for loc in get_all_locations() for node in loc.nodes}
    process_out = set()
    for pr in load_processes():
        process_out.update(pr.outputs.keys())
    reachable = {i for i in defined if i in gather_ids or i in process_out}
    value = len(reachable) / len(defined) if defined else 0.0
    return {"value": round(value, 3),
            "reachable": sorted(reachable),
            "unreachable": sorted(defined - reachable)}


# ----------------------------------------------------------------------------
# Metrik 7 — session_depth
# ----------------------------------------------------------------------------

def metric_session_depth(stall_limit=15, cap=2000):
    """Aktionen bis nichts Neues mehr passiert (Langeweile-Proxy)."""
    seed = BASE_SEED + 500
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    stall, actions = 0, 0
    while actions < cap:
        if _drain_check(game):
            break
        actions += 1
        if game.player.energy < 150:
            _eat_best(game)
        before = {it.name for it in game.player.inventory.items} | \
                 set(game.player.known_blueprints)
        if rng.random() < 0.5:
            if rng.random() < 0.15:
                game.travel(locs[rng.randrange(len(locs))])
            game.gather()
        else:
            sel = _random_sel(game, rng, kmin=1)
            if sel:
                game.execute_experiment(sel)
        after = {it.name for it in game.player.inventory.items} | \
                set(game.player.known_blueprints)
        stall = stall + 1 if after == before else 0
        if stall >= stall_limit:
            break
    return {"value": actions, "stall_limit": stall_limit}


# ----------------------------------------------------------------------------
# Aggregation, JSON + Markdown
# ----------------------------------------------------------------------------

METRICS = [
    ("actions_to_first_craft", "Aktionen bis zum ersten erfolgreichen Craft (naiv)", metric_first_craft, "niedriger = besser"),
    ("blueprint_reachability", "Anteil erreichbarer Blueprints (N=50)", metric_reachability, "höher = besser"),
    ("craft_variety", "Unterschiedliche Crafts in 100 Aktionen", metric_craft_variety, "höher = besser"),
    ("skill_spread", "Überlebens-Spanne optimal vs. zufällig", metric_skill_spread, "höher = besser"),
    ("feedback_quality", "Anteil informativer Rückmeldungen", metric_feedback_quality, "höher = besser"),
    ("content_reachable", "Anteil sammelbarer definierter Items", metric_content_reachable, "höher = besser"),
    ("session_depth", "Aktionen bis nichts Neues passiert", metric_session_depth, "höher = besser"),
]


def _collapse(result):
    """Zieht den Haupt-Skalar aus einem Metrik-Dict oder -Wert."""
    if result is None:
        return None
    if isinstance(result, dict):
        return result.get("value")
    return result


def compute_all():
    out = {}
    for key, _desc, fn, _dir in METRICS:
        try:
            out[key] = fn()
        except Exception as e:  # noqa: BLE001 — ein Messfehler killt nicht alles
            out[key] = {"error": f"{type(e).__name__}: {e}"}
            print(f"[scorecard] WARN {key}: {e}", file=sys.stderr)
    return out


def _prev_value(key):
    files = sorted(SCORECARD_DIR.glob("????-??-??.json"))
    if not files:
        return None
    data = json.loads(files[-1].read_text())
    return _collapse(data.get(key))


def build_table(data):
    lines = [
        "# Project Primal Process — Scorecard",
        "",
        "> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue.",
        "> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only).",
        "",
        "| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |",
        "|--------|------|-----------|----------|--------------|",
    ]
    for key, desc, _fn, direction in METRICS:
        val = _collapse(data.get(key))
        if val is None:
            val_txt = "n/a"
        elif isinstance(val, float):
            val_txt = f"{val:.3f}"
        else:
            val_txt = str(val)
        prev = _prev_value(key)
        if prev is None:
            delta = "— (Baseline)"
        else:
            d = (val - prev) if isinstance(val, (int, float)) and isinstance(prev, (int, float)) else None
            if d is None:
                delta = "—"
            elif abs(d) < 0.001:
                delta = "±0"
            else:
                sign = "+" if d > 0 else ""
                delta = f"{sign}{d:.3f}"
        lines.append(f"| {key} | {val_txt} | {delta} | {direction} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def main():
    SCORECARD_DIR.mkdir(exist_ok=True)
    data = compute_all()
    today = date.today().isoformat()
    path = SCORECARD_DIR / f"{today}.json"
    payload = {
        "date": today,
        "base_seed": BASE_SEED,
        "metrics": data,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    (SCORECARD_DIR / "latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    # SCORECARD.md aktualisieren, ohne den Kopf zu duplizieren
    body = build_table(data)
    # Detail-Block anhängen (nur beim ersten Run als Baseline komplett)
    lines = list(data.items())
    body += "\n## Baseline-Details (" + today + ")\n\n"
    body += "```json\n" + json.dumps({k: v for k, v in lines},
                                      indent=2, ensure_ascii=False) + "\n```\n"
    (ROOT / "SCORECARD.md").write_text(body)

    print(json.dumps({"date": today, "metrics": {
        k: _collapse(v) for k, v in data.items()}}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
