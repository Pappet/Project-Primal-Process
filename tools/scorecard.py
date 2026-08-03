#!/usr/bin/env python3
"""tools/scorecard.py — Fitness-Signal für Project Primal Process.

Berechnet 7 messbare Eigenschaften des Spiels aus echten Playthroughs.
Nicht Prozesstreue, sondern das Spiel selbst ist das Signal.

- Stdlib only. Deterministisch (fester Seed-Satz). Läuft ohne Argumente.
- Jede laufbasierte Metrik läuft über SEEDS (Median) statt über einen Run.
- Metriken hängen an Identitäten (blueprint_id/template_id/reason), nicht an
  Anzeigetext — damit lassen sie sich nicht durch String-Änderungen faken.

Output:
  - scorecard/YYYY-MM-DD.json   (Rohwerte + Details, schema=2)
  - scorecard/latest.json       (Kopie des aktuellsten Runs)
  - SCORECARD.md                (Markdown-Tabelle mit Delta zur Vorwoche)
"""
import json
import random
import statistics
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
SCHEMA = 2                                       # Zählweise der Metriken
SEEDS = tuple(BASE_SEED + i for i in range(20))
HORIZON = 500                                    # Tick-Cap für Überlebensmetriken
SCORECARD_DIR = ROOT / "scorecard"
ARCHIVE_DIR = SCORECARD_DIR / "archive"

# Reason-Codes, die als "informativ" gelten (Feedback sagt etwas aus).
# SUCCESS, BROKEN_ITEM, TOO_FEW_ITEMS und MISSING_TAG:* zählen; NO_MATCH ohne
# Detail und UNKNOWN zählen NICHT. Keine String-Blacklist.
INFORMATIVE_REASONS_PREFIX = ("MISSING_TAG:",)
INFORMATIVE_REASONS = {"SUCCESS", "BROKEN_ITEM", "TOO_FEW_ITEMS"}


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


def _travel_or_fail(game, loc_id):
    """Reist; schlägt HART fehl, wenn die Location nicht existiert."""
    if loc_id not in game.locations:
        raise RuntimeError(
            f"scorecard: referenzierte Location '{loc_id}' existiert nicht — "
            "Messung wäre still falsch.")
    game.travel(loc_id)


# ----------------------------------------------------------------------------
# Metrik 1 — actions_to_first_craft
# ----------------------------------------------------------------------------

def _run_first_craft(seed):
    """Aktionen bis zum ersten erfolgreichen Craft bei naivem Spiel (ein Run)."""
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    actions = 0
    since_travel = 0
    while actions < 20000:
        actions += 1
        if _drain_check(game):
            return None
        if game.player.energy < 150:
            _eat_best(game)
        if rng.random() < 0.45:
            if since_travel > 8:
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
                since_travel = 0
            game.gather()
            since_travel += 1
        else:
            sel = _random_sel(game, rng, kmin=2)
            if sel:
                if game.execute_experiment(sel)["success"]:
                    return actions
    return None


def metric_first_craft():
    return _aggregate(lambda s: _run_first_craft(s))


# ----------------------------------------------------------------------------
# Metrik 2 — blueprint_reachability (N=50, einzelner deterministischer Lauf)
# ----------------------------------------------------------------------------

def _pair_slots(game, bp):
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
        random.seed(BASE_SEED + 10_000 + run)
        game = GameEngine()
        for loc in loc_ids:
            _travel_or_fail(game, loc)
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
# Metrik 3 — craft_variety (distinkte blueprint_id)
# ----------------------------------------------------------------------------

def _run_craft_variety(seed, actions=100):
    """Distinkte erfolgreiche blueprints in N Aktionen (ein Run)."""
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
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
            game.gather()
        else:
            sel = _random_sel(game, rng, kmin=2)
            if sel:
                res = game.execute_experiment(sel)
                if res.get("blueprint_id"):
                    results.add(res["blueprint_id"])
    return len(results)


def metric_craft_variety():
    return _aggregate(lambda s: _run_craft_variety(s))


# ----------------------------------------------------------------------------
# Metrik 4 — skill_spread (datengetrieben, hart bei fehlender Location)
# ----------------------------------------------------------------------------

def _survival_staying(loc_id, seed):
    """Überleben, wenn man in loc_id bleibt und isst. Datensatz-getrieben."""
    random.seed(seed)
    game = GameEngine()
    if game.current_location_id != loc_id:
        _travel_or_fail(game, loc_id)
    while game.tick_counter < HORIZON:
        if _drain_check(game):
            break
        if game.player.energy < 300:
            _eat_best(game)
        game.gather()
    return min(game.tick_counter, HORIZON)


def _survival_optimal(seed):
    """Beste Überlebenszeit über alle erreichbaren Locations."""
    best = 0
    for loc_id in get_all_locations_ids():
        best = max(best, _survival_staying(loc_id, seed))
    return best


def get_all_locations_ids():
    return [l.id for l in get_all_locations()]


def _survival_random(seed):
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    while game.tick_counter < HORIZON:
        if _drain_check(game):
            break
        r = rng.random()
        if r < 0.25:
            _travel_or_fail(game, locs[rng.randrange(len(locs))])
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


def _run_skill_spread(seed):
    opt = _survival_optimal(seed)
    rnd = _survival_random(seed)
    return (opt - rnd) / opt if opt > 0 else 0.0


def metric_skill_spread():
    """Überlebenszeit optimal vs. zufällig — misst, ob Können etwas bringt."""
    return _aggregate(lambda s: _run_skill_spread(s))


# ----------------------------------------------------------------------------
# Metrik 5 — feedback_quality (Reason-Codes statt Blacklist)
# ----------------------------------------------------------------------------

def _run_feedback_quality(seed, steps=60):
    """Anteil informativer Aktionen über Reason-Codes (ein Run)."""
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
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
            # Sammeln: nicht-leere Ergebnisliste = informativ
            if game.gather():
                informative += 1
        else:
            sel = _random_sel(game, rng, kmin=1)
            res = game.execute_experiment(sel) if sel else \
                game.execute_experiment([])
            reason = res.get("reason", "UNKNOWN")
            if _is_informative_reason(reason):
                informative += 1
    return informative / total if total else 0.0


def _is_informative_reason(reason):
    if reason in INFORMATIVE_REASONS:
        return True
    if reason and reason.startswith(INFORMATIVE_REASONS_PREFIX):
        return True
    return False


def metric_feedback_quality():
    return _aggregate(lambda s: _run_feedback_quality(s))


# ----------------------------------------------------------------------------
# Metrik 6 — content_reachable (mit Absolutwerten gegen Löschen)
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
    return {
        "value": round(value, 3),
        "reachable_count": len(reachable),
        "defined_count": len(defined),
        "reachable": sorted(reachable),
        "unreachable": sorted(defined - reachable),
    }


# ----------------------------------------------------------------------------
# Metrik 7 — session_depth (Neuheit über template_id + blueprints + Prozesse)
# ----------------------------------------------------------------------------

def _known_process_ids(player):
    return set(getattr(player, "known_processes", set()))


def _novelty_set(game):
    """Identitäten, die 'Neuheit' ausmachen (template_id, nicht Name)."""
    tpl = {it.template_id or it.name for it in game.player.inventory.items}
    bps = set(game.player.known_blueprints)
    procs = _known_process_ids(game.player)
    return tpl | bps | procs


def _run_session_depth(seed, stall_limit=15, cap=1500):
    """Aktionen bis nichts Neues mehr passiert (ein Run)."""
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
        before = _novelty_set(game)
        if rng.random() < 0.5:
            if rng.random() < 0.15:
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
            game.gather()
        else:
            sel = _random_sel(game, rng, kmin=1)
            if sel:
                game.execute_experiment(sel)
        after = _novelty_set(game)
        stall = stall + 1 if after == before else 0
        if stall >= stall_limit:
            break
    return actions


def metric_session_depth():
    return _aggregate(lambda s: _run_session_depth(s))


# ----------------------------------------------------------------------------
# Aggregation über Seeds (Median + p25/p75)
# ----------------------------------------------------------------------------

def _aggregate(run_fn, cap=None):
    """Mittelt eine laufbasierte Metrik über alle Seeds."""
    values = []
    for seed in SEEDS:
        v = run_fn(seed)
        if v is not None:
            values.append(v)
    if not values:
        return {"value": None, "error": "no runs produced values"}
    values.sort()
    mid = statistics.median(values)
    q = len(values) // 4
    p25 = values[q] if q < len(values) else values[-1]
    p75 = values[len(values) - 1 - q]
    return {
        "value": round(mid, 3) if isinstance(mid, float) else mid,
        "p25": round(p25, 3) if isinstance(p25, float) else p25,
        "p75": round(p75, 3) if isinstance(p75, float) else p75,
        "n_runs": len(values),
    }


# ----------------------------------------------------------------------------
# Aggregation, JSON + Markdown
# ----------------------------------------------------------------------------

METRICS = [
    ("actions_to_first_craft", "Aktionen bis zum ersten erfolgreichen Craft (naiv)", metric_first_craft, "niedriger = besser"),
    ("blueprint_reachability", "Anteil erreichbarer Blueprints (N=50)", metric_reachability, "höher = besser"),
    ("craft_variety", "Unterschiedliche Craft-Typen in 100 Aktionen", metric_craft_variety, "höher = besser"),
    ("skill_spread", "Überlebens-Spanne optimal vs. zufällig", metric_skill_spread, "höher = besser"),
    ("feedback_quality", "Anteil informativer Rückmeldungen", metric_feedback_quality, "höher = besser"),
    ("content_reachable", "Anteil sammelbarer definierter Items", metric_content_reachable, "höher = besser"),
    ("session_depth", "Aktionen bis nichts Neues passiert", metric_session_depth, "höher = besser"),
]


def _collapse(result):
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
        except Exception as e:  # noqa: BLE001 — eine Metrik killt nicht alle
            out[key] = {"error": f"{type(e).__name__}: {e}"}
            print(f"[scorecard] WARN {key}: {e}", file=sys.stderr)
    return out


def load_previous(today):
    """Jüngste vergleichbare (schema==SCHEMA) Scorecard VOR heute."""
    best = None  # (datum, data)
    if not SCORECARD_DIR.exists():
        return None
    for path in SCORECARD_DIR.glob("????-??-??.json"):
        stem = path.stem
        if stem >= today:
            continue
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("schema") != SCHEMA:
            continue
        if best is None or stem > best[0]:
            best = (stem, data)
    return best[1] if best else None


def _fmt_num(v):
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _delta_cell(key, val, prev_val, direction):
    """Liefert (delta_text, arrow). prev_val aus VORWOCHENDATEI, nicht heute."""
    if prev_val is None:
        return "— (Baseline)", ""
    if not isinstance(val, (int, float)) or not isinstance(prev_val, (int, float)):
        return "—", ""
    if abs(val - prev_val) < 0.001:
        return "±0", "±0"
    better = (direction == "niedriger = besser" and val < prev_val) or \
             (direction == "höher = besser" and val > prev_val)
    arrow = "↑ besser" if better else "↓ schlechter"
    sign = "+" if (val - prev_val) > 0 else ""
    return f"{sign}{val - prev_val:.3f}", arrow


def build_table(data, prev):
    lines = [
        "# Project Primal Process — Scorecard",
        "",
        "> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.",
        "> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).",
        "",
        "| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |",
        "|--------|------|-----------|----------|--------------|",
    ]
    prev_metrics = (prev or {}).get("metrics", {}) if prev else {}
    for key, desc, _fn, direction in METRICS:
        val = _collapse(data.get(key))
        val_txt = _fmt_num(val) if val is not None else "n/a"
        # content_reachable: Content-Reduktion als Warnung statt als Verbesserung
        warn = ""
        if key == "content_reachable":
            cur = data.get("content_reachable") or {}
            pv = prev_metrics.get("content_reachable") or {}
            if (cur.get("defined_count") is not None and pv.get("defined_count")
                    and cur["defined_count"] < pv["defined_count"]):
                warn = " ⚠ Content entfernt"
        prev_val = _collapse(prev_metrics.get(key))
        delta, arrow = _delta_cell(key, val, prev_val, direction)
        if warn:
            delta = "⚠ Content entfernt"
            arrow = ""
        # Richtung: nur Richtungsbeschreibung; Arrow steckt im Delta
        dir_txt = "niedriger" if direction == "niedriger = besser" else "höher"
        if arrow and arrow != "±0":
            delta = f"{delta} {arrow}"
        lines.append(f"| {key} | {val_txt} | {delta} | {dir_txt} = besser | {desc}{warn} |")
    lines.append("")
    return "\n".join(lines)


def main():
    SCORECARD_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()

    prev = load_previous(today)
    data = compute_all()
    payload = {
        "schema": SCHEMA,
        "date": today,
        "base_seed": BASE_SEED,
        "seeds": list(SEEDS),
        "metrics": data,
    }
    path = SCORECARD_DIR / f"{today}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    (SCORECARD_DIR / "latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    body = build_table(data, prev)
    body += f"\n## Details ({today})\n\n"
    body += "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```\n"
    (ROOT / "SCORECARD.md").write_text(body)

    print(json.dumps({"schema": SCHEMA, "date": today, "metrics": {
        k: _collapse(v) for k, v in data.items()}}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
