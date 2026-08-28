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
import itertools
import json
import random
import statistics
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.core import (GameEngine, _label_for, TAG_LABELS, TAG_FAMILIES,  # noqa: E402
                         _slot_satisfied)
from data.items import TEMPLATE_DB, create_item  # noqa: E402
from data.blueprints import get_all_blueprints  # noqa: E402
from data.locations import get_all_locations    # noqa: E402
from data.loader import load_processes          # noqa: E402

BASE_SEED = 20260803
SCHEMA = 2                                       # Zählweise der Metriken
SEEDS = tuple(BASE_SEED + i for i in range(20))
HORIZON = 500                                    # Tick-Cap für Überlebensmetriken
SCORECARD_DIR = ROOT / "scorecard"
ARCHIVE_DIR = SCORECARD_DIR / "archive"


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

def _engine_first_match(game, selected):
    """Rein: Welchen Blueprint würde die Engine mit dieser Auswahl craften?

    Spiegelt execute_experiments Dict-Order-Präzedenz (Länge, Survival-Gate,
    Permutationen, _slot_satisfied) OHNE State-Mutation — selbe Slot-Logik
    (importiert), nur die Schleife ist kopiert. Der Zähler braucht sie, um
    Shadowing zu erkennen: Eine Auswahl, die einen FRÜHEREN Blueprint voll
    trifft, craftet in der Engine diesen — nicht den beabsichtigten.
    (BROKEN_ITEM/NOT_ENOUGH_QUANTITY können hier nicht auftreten: _pair_slots
    filtert condition <= 0 und wählt nur distinkte Objekte.)
    """
    for bp in game.blueprints.values():
        if len(selected) != len(bp.slots):
            continue
        if game.player.stats["survival"] < bp.min_survival_req:
            continue
        for p in itertools.permutations(selected):
            if all(_slot_satisfied(p[i].tags, slot_value)
                   for i, slot_value in enumerate(bp.slots.values())):
                return bp.id
    return None


def _pair_slots(game, bp):
    """Findet je ein distinctes Item pro Slot-Tag, Familien aufgelöst.

    Slot-Tags können Tag-Familien sein (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`…);
    das lösen wir wie die Engine auf die Mitglieder auf, damit der Zähler exakt
    das misst, was die Engine wirklich craften kann (REC-001, freigegeben).

    REC-002-Korrektur (28.08.): Familien werden SORTIERT iteriert — Set-
    Iteration hing am PYTHONHASHSEED und machte den Zähler prozessabhängig
    flaky. Und: Eine fundige Paarung zählt nur, wenn die Engine sie WIRKLICH
    als diesen Blueprint craftet (Dict-Order-Präzedenz!). Gegenbeispiel:
    ropes naive Paarung (reeds=FIBER, stick=RIGID) trifft Spear voll — die
    Engine baute Spear, gebucht wurde rope, und die Ordnungsunabhängigkeit
    war nur Seed-Glück. Shadowende Auswahlen werden verworfen, die Suche
    läuft weiter (Backtrack über die restlichen Kandidaten).
    """
    inv = [it for it in game.player.inventory.items
           if it.quantity >= 1 and it.condition > 0]
    by_tag = {}
    for it in inv:
        for t in it.tags:
            by_tag.setdefault(t, []).append(it)

    candidates = []
    for _slot, tag in bp.slots.items():
        members = sorted(TAG_FAMILIES.get(tag, {tag}))
        pool = []
        for m in members:
            pool.extend(by_tag.get(m, []))
        candidates.append(pool)

    chosen = []

    def backtrack(i, used):
        if i == len(candidates):
            # Erst die Engine-Präzedenz prüfen, dann akzeptieren: Die Auswahl
            # muss in der Engine WIRKLICH diesen Blueprint ergeben.
            return _engine_first_match(game, list(chosen)) == bp.id
        for it in candidates[i]:
            # SPEC-005-Konform: Derselbe Stack darf mehrere Slots füllen,
            # solange quantity reicht (Engine validiert das exakt so). Früher
            # untersagte der Zähler jede Wiedernutzung und unterdeckte die
            # Engine dadurch (Spear aus EINEM stick-Stack war "unerreichbar").
            if used.get(id(it), 0) >= it.quantity:
                continue
            used[id(it)] = used.get(id(it), 0) + 1
            chosen.append(it)
            if backtrack(i + 1, used):
                return True
            used[id(it)] -= 1
            chosen.pop()
        return False

    if not backtrack(0, {}):
        return None
    return list(chosen)


def _reachable_blueprints(game, bps, loc_ids, gather_initial=8, gather_refill=2):
    """Tool-aware Erreichbarkeits-Sicht: Welche Blueprints kann die Engine
    von frischem Start aus craften — inkl. Werkzeug-Bau als Vorschritt?

    REC-002 (freigegeben 22.08.): Der Zähler misst, was die Engine wirklich
    craften kann, nicht was ein naive Ein-Schritt-Lauf über die Blueprint-Liste
    zufällig schafft. Ein Blueprint, dessen Slots einen Werkzeug-Tag fordern
    (z.B. `CORD` von rope, `CUTTING`/`CHOPPING` von Messer/Axt), ist nur dann
    erreichbar, wenn der Zähler das Werkzeug ERST baut und DANN als Zutat nutzt.

    Implementierung: Fixpunkt-Schleife über die Blueprint-Menge. In jedem
    Durchlauf werden alle Blueprints versucht, deren Slots aus dem aktuellen
    Inventar (Rohmaterial + bereits gebaute Werkzeuge) füllbar sind und deren
    Survival-Gate offen ist. Gelingt ein neuer Craft, wird das gebaute Werkzeug
    dem Inventar hinzugefügt (trägt seine tool_tags) und die Survival-Score
    steigt — so öffnet ein Tier-1-Fund den Tier-2-Zugang (min_survival_req)
    genau wie in echtem Play. Zwischen Durchläufen werden verbrauchte
    Rohmaterialien nachgesammelt, damit ein knapper Vorrat nicht fälschlich als
    Unerreichbarkeit zählt.

    Ordnungsunabhängigkeit (Korrektur 28.08.): Die Versuche laufen in der
    KANONISCHEN Engine-Dict-Order, unabhängig davon, in welcher Reihenfolge
    der Aufrufer die Blueprint-Liste übergibt. Die Engine-eigene Präzedenz
    (execute_experiment matcht in Dict-Order) IST die Engine-Wahrheit — ein
    Zähler, der die Versuchsreihenfolge selbst dreht, dreht auch, WEM knappe
    Rohstoffe (flint_shard: Axt oder Messer?) in die Hände fallen, und das
    Ergebnis hing an der zufälligen Listenordnung. Buchung: was die Engine
    WIRKLICH gebaut hat (blueprint_id), nie der Versuchs-id.

    Liefert das Set erreichbarer Blueprints (eine Sichtung, deterministisch
    durch den Run-Seed gesteuert; Aufrufer setzt `random.seed` außen).
    """
    canonical = {bid: i for i, bid in enumerate(game.blueprints)}
    ordered = sorted(bps, key=lambda b: canonical.get(b.id, len(canonical)))
    crafted = set()
    while True:
        progressed = False
        for bp in ordered:
            if bp.id in crafted:
                continue
            if game.player.stats["survival"] < bp.min_survival_req:
                continue
            sel = _pair_slots(game, bp)
            if sel:
                res = game.execute_experiment(sel)
                if res["success"]:
                    # REC-002-Korrektur (28.08.): buche, was die Engine
                    # WIRKLICH gebaut hat (blueprint_id) — nie den Versuchs-id.
                    # Nach der _pair_slots-Verifikation sind beide identisch;
                    # gebucht wird trotzdem die Engine-Wahrheit.
                    crafted.add(res.get("blueprint_id") or bp.id)
                    progressed = True
        if not progressed:
            break
        # verbrauchte Rohmaterialien nachsammeln (knapper Vorrat ≠ Unerreichbar)
        for loc in loc_ids:
            _travel_or_fail(game, loc)
            for _ in range(gather_refill):
                game.gather()
    return crafted


def metric_reachability(n=50):
    """Anteil der Blueprints, die von frischem Start aus erreichbar sind.

    REC-002 (freigegeben 22.08.): Der Zähler misst jetzt, was die Engine
    wirklich craften kann — inkl. Werkzeug-Bau als Vorschritt. Statt jeden
    Blueprint einmal in Listenreihenfolge zu versuchen, laesst ein
    Fixpunkt-Lauf so lange craften, wie Material/Werkzeug/Survival es
    erlauben: Ein gebautes Werkzeug (rope → `CORD`, Messer → `CUTTING`) ist
    selbst wieder Baustein für höherwertige Blueprints. Damit bleibt die
    Zählung Ordnung-unabhängig und bleibt Engine-Wahrheit.
    """
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
        for bp_id in _reachable_blueprints(game, bps, loc_ids):
            seen[bp_id] += 1
    total = max(1, len(bps))
    value = sum(1 for v in seen.values() if v > 0) / total
    return {"value": round(value, 3),
            "per_blueprint": {k: (v > 0) for k, v in seen.items()}}


# ----------------------------------------------------------------------------
# Metrik 3 — craft_variety (distinkte blueprint_id)
# ----------------------------------------------------------------------------

def _run_craft_variety(seed, actions=100):
    """Distinkte blueprint_ids + process_ids in N Aktionen (ein Run)."""
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
        r = rng.random()
        if r < 0.5:
            if rng.random() < 0.2:
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
            game.gather()
        elif r < 0.9:
            sel = _random_sel(game, rng, kmin=2)
            if sel:
                res = game.execute_experiment(sel)
                if res.get("blueprint_id"):
                    results.add(res["blueprint_id"])
        else:
            # v2: Prozess-Pfad zählt mit (Entscheid 22.08., Pkt. 2). Das
            # Prozess-System ist ein vollwertiger Craft-Pfad — ein naiver Spieler
            # versucht gelegentlich einen Prozess, zu dem er (zufällig) die
            # Mittel hält, und trägt den Prozess bei Erfolg als divergente.
            procs = list(game.processes.keys())
            if procs:
                pid = procs[rng.randrange(len(procs))]
                pres = game.execute_process(pid)
                if pres.get("process_id"):
                    results.add(pres["process_id"])
    return len(results)


def metric_craft_variety():
    """Distinkte erfolgreiche blueprints UND Prozesse in 100 Aktionen (v2)."""
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
    """Einsteiger-Decke: Überlebens-Lücke optimal vs. zufällig (Option A, umgedeutet).

    Formel bleibt exakt (Optimum minus Zufall, über das Optimum normiert) — aber
    die Richtung ist umgedeutet (Entscheid 22.08., Pkt. 1): Ein FALLENDER Wert
    bedeutet eine GEHOBENE Einsteiger-Decke — ein Zufallsspieler überlebt näher
    am Optimum, das Spiel straft Unwissen weniger hart. Es ist kein Tiefenverlust
    der Experten-Ökonomie. Version bleibt 1 (Formel unverändert).
    """
    return _aggregate(lambda s: _run_skill_spread(s))


# ----------------------------------------------------------------------------
# Metrik 5 — feedback_quality (Spielersicht: Label passt zum Reason)
# ----------------------------------------------------------------------------

# Erwartetes Text-Fragment pro Reason-Code — der Konsistenz-Wächter zwischen
# interner Wahrheit und Spielertext. Informativ NUR, wenn die Meldung das zum
# Code gehörende Label wirklich enthält. Verrät die Engine den Grund nicht im
# Text, zählt die Aktion als NICHT informativ (auch wenn der Code stimmt).
#
# Ein `None`-Eintrag ist eine BEWUSSTE Entscheidung, kein "vergessener" Code:
# Der Reason ist von Natur aus nicht-informativ (generisch) und wird hier als
# solcher dokumentiert. Der Vollständigkeits-Test (`test_..._cover_all_emittable`)
# erzwingt, dass jeder Reason, den die Engine emittieren kann, entweder ein
# Fragment trägt oder als dokumentierter `None`-Grund gehandelt wird.
_EXPECTED_FRAGMENTS = {
    "SUCCESS": "Hergestellt",
    "TOO_FEW_ITEMS": "mindestens zwei",
    "NOT_ENOUGH_QUANTITY": "mehr von demselben",
    "BROKEN_ITEM": "zerbrochen",
    "NO_MATCH": "ergibt nichts",
    "NEAR_MISS": "gehören",          # SPEC-003: absichtlich vage, aber informativ
    "DEPLETED": "erschöpft",
    "FIRE_OUT": "erlischt",
    "NO_FIRE": "kein Feuer",
    "MISSING_FUEL": "Brennholz",
    "NO_INJURY": "nicht verletzt",
    "BLEEDING": "blutest",
    "TREATED": "behandelt",
    "HEALED": "heilt",
    "MISSING_ENV": "in der Umgebung",
    "MISSING_TOOL": "als Werkzeug",
    # Dokumentiert NICHT-informativ (bewusst generisch, kein Handlungs-Hinweis):
    "UNKNOWN": None,           # Engine-Fallback "Das geht so nicht."
    "UNKNOWN_PROCESS": None,   # Prozess existiert nicht → kein Fragment sinnvoll
    "MISSING_INPUT": None,     # Meldung nennt den Item-Namen, kein stabiles Fragment
}

# Parameterisierte Codes, deren Fragment über den Parameter aufgelöst wird.
# MISSING_TAG: das Label des fehlenden Tags (z.B. SHARP → "etwas Scharfes").
# MISSING_ENV/MISSING_TOOL: statisches Fragment aus der Map (das Label ist
# nur der Parameter, der Meldungs-Rest "in der Umgebung"/"als Werkzeug" zählt).


def _expected_fragment(reason):
    if reason is None:
        return None
    # MISSING_TAG: der Parameter (Tag) bestimmt das Label — das informativ
    # machende Fragment ist das Tag-Label, nicht ein fester Text.
    if reason.startswith("MISSING_TAG:"):
        tag = reason.split(":", 1)[1]
        return _label_for(tag)
    key = reason.split(":", 1)[0]
    return _EXPECTED_FRAGMENTS.get(key)


# Alle Reason-Codes, die die Engine emittieren kann — Quelle der Wahrheit für
# den Vollständigkeits-Test. Parameterisierte Codes werden als Präfix geführt.
EMITTABLE_REASONS = {
    "SUCCESS", "TOO_FEW_ITEMS", "NOT_ENOUGH_QUANTITY", "BROKEN_ITEM",
    "NO_MATCH", "NEAR_MISS", "DEPLETED", "FIRE_OUT", "NO_FIRE",
    "MISSING_FUEL", "MISSING_TAG", "MISSING_ENV", "MISSING_TOOL",
    "MISSING_INPUT", "NO_INJURY", "BLEEDING", "TREATED", "HEALED",
    "UNKNOWN", "UNKNOWN_PROCESS",
}


def _informative_experiment(message, reason):
    fragment = _expected_fragment(reason)
    return fragment is not None and fragment in message


def _run_feedback_quality(seed, steps=60):
    """Anteil informativer Aktionen — Meldung muss den Reason widerspiegeln."""
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
            # Sammeln: nicht-leere Ergebnisliste = Spieler sieht einen Fund
            if game.gather():
                informative += 1
        else:
            sel = _random_sel(game, rng, kmin=1)
            res = game.execute_experiment(sel) if sel else \
                game.execute_experiment([])
            if _informative_experiment(res["message"], res.get("reason")):
                informative += 1
    return informative / total if total else 0.0


def metric_feedback_quality():
    return _aggregate(lambda s: _run_feedback_quality(s))


# ----------------------------------------------------------------------------
# Metrik 8 — discovery_gap (Abstand erreichbar vs. tatsächlich gefunden)
# ----------------------------------------------------------------------------

def _run_naive_discovery(seed, actions=150):
    """Anteil der Blueprints, die ein naiver Spieler in N Aktionen entdeckt."""
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    total = max(1, len(get_all_blueprints()))
    discovered = set()
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
                    discovered.add(res["blueprint_id"])
    return len(discovered) / total


def metric_discovery_gap():
    """Abstand zwischen Erreichbarem und dem, was ein Spieler wirklich findet."""
    reach_val = _collapse(metric_reachability())
    reach = float(reach_val) if reach_val is not None else 0.0
    naive = _aggregate(lambda s: _run_naive_discovery(s))
    naive_rate = float(naive["value"]) if naive.get("value") is not None else 0.0
    gap = reach - naive_rate
    return {
        "value": round(gap, 3),
        "blueprint_reachability": round(reach, 3),
        "naive_discovery_rate": naive_rate,
        "naive_p25": naive.get("p25"),
        "naive_p75": naive.get("p75"),
        "band": [0.2, 0.6],
    }



# ----------------------------------------------------------------------------
# Metrik 6 — content_reachable (mit Absolutwerten gegen Löschen)
# ----------------------------------------------------------------------------

def metric_content_reachable():
    """Anteil der definierten Items, die tatsächlich sammelbar sind (v2).

    v2 (Entscheid 22.08., Pkt. 3): prüft zusätzlich Node-Referenzen. Ein Node,
    dessen result_template_id kein Template hat, deklariert Inhalt, der nicht
    existiert → zählt als definiert-aber-unerreichbar und senkt die Metrik
    sichtbar. Genau das hätte B06/B07 am Tag 1 gezeigt. Die
    `⚠ Content entfernt`-Warnt-Logik (defined_count-Vergleich) bleibt unverändert.
    """
    defined = set(TEMPLATE_DB.keys())
    nodes = [node for loc in get_all_locations() for node in loc.nodes]
    gather_ids = {node.result_template_id for node in nodes}
    # dangling = deklarierte, aber nicht existente Node-Referenzen
    dangling = {tid for tid in gather_ids if tid not in TEMPLATE_DB}
    process_out = set()
    for pr in load_processes():
        process_out.update(pr.outputs.keys())
    # "definiert" = echte Templates + deklarierte, aber fehlende Node-Referenzen.
    all_defined = defined | dangling
    # Erreichbar nur, was wirklich existiert — dangling ist nie erreichbar, auch
    # wenn der Node es beim Sammeln "liefert" (das Item existiert ja nicht).
    reachable = {i for i in defined if i in gather_ids or i in process_out}
    value = len(reachable) / len(all_defined) if all_defined else 0.0
    return {
        "value": round(value, 3),
        "reachable_count": len(reachable),
        "defined_count": len(all_defined),
        "reachable": sorted(reachable),
        "unreachable": sorted(all_defined - reachable),
        "dangling_refs": sorted(dangling),
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


def _bp_overlap(bp, held_tags):
    """Wie viele Slots eines Blueprints decken die gehaltenen Tags ab?
    Löst Familien (SHARP_OR_RIGID) wie die Engine via TAG_FAMILIES auf."""
    o = 0
    for sv in bp.slots.values():
        req = set(TAG_FAMILIES.get(sv, {sv}))
        if req & held_tags:
            o += 1
    return o


def _v2_selection(game, rng):
    """Zielgerichtete, rezeptfreie Auswahl für den session_depth-v2-Bot.

    Modelliert 'einen Spieler, der nicht kalt aufgibt': Er versucht einen
    unbekannten, gate-offenen Blueprint zu vervollständigen, für den er
    bereits >= 2/3 der Materialien hält, und bevorzugt Blueprints, die ihm
    die Engine per NEAR_MISS-Hinweis als 'nah' gemeldet hat. Kein Orakel:
    Er muss die Materialien erst sammeln, findet sie nur mit RNG-Zufall und
    scheitert, wenn ein Slot-Tag nicht (in passender Menge) da ist.
    """
    inv = [it for it in game.player.inventory.items if it.quantity >= 1]
    if len(inv) < 2:
        return None
    held = set()
    for it in inv:
        held.update(it.tags)
    survival = game.player.stats["survival"]

    candidates = []
    for bp in game.blueprints.values():
        if bp.id in game.player.known_blueprints:
            continue
        if survival < bp.min_survival_req:
            continue  # gated und Gate noch nicht offen → erst später versuchen
        o = _bp_overlap(bp, held)
        n = len(bp.slots)
        if o * 3 < 2 * n:  # < 2/3 der Slots gedeckt → noch nicht nah genug
            continue
        priority = 0 if bp.id in game.player.near_misses else 1
        # Vorrang: höchste Overlap-Quote (n/n = vollendbar schlägt 2/3), dann
        # NEAR_MISS als Tiebreak bei gleicher Quote, dann eindeutige Ordnung.
        # Ein 100%-Match (z.B. rope mit FIBER+RIGID, 2/2) schlägt einen nur
        # teilweise nahen Near-Miss-BP (axe 2/3), der noch ein Kopf-Material
        # bräuchte, das gar nicht da ist.
        ratio = o / n
        candidates.append((-ratio, priority, bp.id, bp))
    if not candidates:
        return None
    candidates.sort()
    bp = candidates[0][3]

    # Zu jedem Slot des Ziel-Blueprints das passende Item wählen (Familien
    # aufgelöst); nur gezählte Items, pro Objekt einmal. Fehlende Slots werden
    # mit zufälligen Rest-Items aufgefüllt, damit der Versuch überhaupt
    # stattfindet und (bei Teiltreffer) ein NEAR_MISS-Hinweis feuern kann —
    # so konvergiert der Bot über Versuch + Hinweis statt nur bei 100%-Match.
    sel, used = [], set()
    for sv in bp.slots.values():
        req = set(TAG_FAMILIES.get(sv, {sv}))
        pick = None
        for it in inv:
            if id(it) in used:
                continue
            if req & set(it.tags):
                pick = it
                break
        if pick is not None:
            sel.append(pick)
            used.add(id(pick))
        else:
            # Slot nicht (passend) gedeckt → zufälliges anderes Item als Füller
            fillers = [it for it in inv if id(it) not in used]
            if fillers:
                f = rng.choice(fillers)
                sel.append(f)
                used.add(id(f))
    if len(sel) < 2:
        return None
    return sel


def _run_session_depth(seed, stall_limit=15, cap=1500):
    """Aktionen bis nichts Neues mehr passiert (ein Run). v2: ziel-bewusster
    naiver Bot — verfolgt NEAR_MISS-Hinweise, versucht Blueprints, für die er
    >= 2/3 Materialien hält, und darf ab survival >= 0.4 auch gated Blueprints
    versuchen. Kein Orakel, kein Rezeptbuch — nur ein Spieler, der nicht
    'kalt' aufgibt. (Spec session_depth v2, Peter 22.08.)"""
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    stall, actions = 0, 0
    # Frischer Spieler startet am Waldrand — Kopf-Materialien (STONE/FLINT/BONE)
    # liegen woanders. Ein nicht aufgebender Spieler reist, statt am selben Ort
    # zu verhungern: abwechselnd sammeln (mit Reisen) und zielgerichtet versuchen.
    while actions < cap:
        if _drain_check(game):
            break
        actions += 1
        if game.player.energy < 150:
            _eat_best(game)
        before = _novelty_set(game)
        # Halb sammeln/reisen (Material suchen — auch Kopf-Material an anderen
        # Orten), halb zielgerichtet versuchen. Ein persistenter Spieler spinnt
        # nicht am selben Ort, sondern holt das fehlende Material, bevor er
        # erneut versucht — ohne Oracle also: reisen, bis der Kopf da ist.
        if rng.random() < 0.5:
            # Material-Phase: reisen + sammeln (Kopf-Material woanders)
            if rng.random() < 0.4:
                _travel_or_fail(game, locs[rng.randrange(len(locs))])
            elif rng.random() < 0.10:
                s2 = _random_sel(game, rng, kmin=1)
                if s2:
                    game.execute_experiment(s2)
                else:
                    game.gather()
            else:
                game.gather()
        else:
            sel = _v2_selection(game, rng)
            if sel is not None:
                game.execute_experiment(sel)
            else:
                game.gather()
        after = _novelty_set(game)
        stall = stall + 1 if after == before else 0
        if stall >= stall_limit:
            break
    return actions


def metric_session_depth():
    return _aggregate(lambda s: _run_session_depth(s))


# ----------------------------------------------------------------------------
# Metrik 9 — forage_pressure (Knappheit wird gefühlt) — SPEC-004, Probezeit
# ----------------------------------------------------------------------------

def _run_forage_pressure(seed, actions=200):
    """Anteil der Gather-Versuche an einem nicht-vollen Node (Knappheit greift).

    Fixe naive Policy: immer der erste erntbare Node am aktuellen Ort, mit
    gelegentlichem Ortswechsel (Rotation). Zählt, ob eine Sammel-Aktion auf
    lokale Knappheit trifft (stock < max_stock) — der Entscheidungsdruck,
    den SPEC-004 bewusst erzeugen will.
    """
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    n_attempts, n_underperform = 0, 0
    for _ in range(actions):
        if _drain_check(game):
            break
        node = None
        for n in game.current_location.nodes:
            if game.player.stats["perception"] < n.req_perception:
                continue
            if n.req_tool_tag and not game.player.inventory.find_item_by_tag(n.req_tool_tag):
                continue
            node = n
            break
        if node is None:
            break
        n_attempts += 1
        if node.stock < node.max_stock:
            n_underperform += 1
        game.gather()
        if rng.random() < 0.2:
            _travel_or_fail(game, locs[rng.randrange(len(locs))])
    return n_underperform / max(1, n_attempts)


def metric_forage_pressure():
    """Anteil der Sammel-Versuche an einem nicht-vollen Node (Band-Metrik)."""
    return _aggregate(lambda s: _run_forage_pressure(s))


# ----------------------------------------------------------------------------
# Metrik 10 — warmth_stability (SPEC-007, Probezeit)
# "Kälte ist spürbar, aber durch eigenes Handeln (Feuer/Isolation) abwendbar."
# ----------------------------------------------------------------------------

# Kälte-Stress = ein Tick, an dem die ROHEN Umgebungstemperatur (ohne Feuer)
# unter der Komfortschwelle liegt — d.h. wo OHNE Gegenmechanik die Unterkühlung
# Richtung 35°C drückte. "warm" = der Spieler hält body_temp trotzdem >= 35°C
# (durch ein unterhaltenes Feuer + isolierende Kleidung). Abweichung von der
# Vorschlagsskizze (die effektive Temp. inkl. Feuer zählte): so misst die Metrik
# die tatsächlich erlebte Kälte-Bedrohung, nicht den Moment, in dem das Feuer sie
# schon weggewärmt hat — sonst gäbe es bei funktionierendem Feuer gar keinen
# Kälte-Stress-Tick mehr und der Wert wäre nichtssagend.
WARMTH_COMFORT = 25.0      # rohe Umgebung < dem = Kälte-Stress-Tick
WARMTH_HYPOTHERMIA = 35.0  # body_temp-Schwelle für "warm überlebt"
WARMTH_HORIZON = 200
WARMTH_SEEDS = tuple(BASE_SEED + 2000 + i for i in range(20))


def _run_warmth_stability(seed, horizon=WARMTH_HORIZON):
    """Anteil der Kälte-Stress-Ticks, in denen der Spieler warm bleibt.

    Geführte, survival-sound Policy mit Mid-Game-Ausstattung (Spieler hat die
    Gegenmechanik entdeckt): Messer (CUTTING) für Feueraufbau, Fell-Umhang
    (Isolation), Brennholz. Bei Kälte wird das Feuer unterhalten (anzünden bzw.
    nachlegen). Gemessen: wie oft bleibt body_temp trotz Kälte-Stress >= 35°C?
    """
    random.seed(seed)
    rng = random.Random(seed)  # noqa: F841 — Seed-Vielfalt für Gather-Determinismus
    game = GameEngine()
    inv = game.player.inventory

    def give(tpl, qty=1):
        inv.add(create_item(tpl, qty))

    # --- Geführte Mid-Game-Ausstattung ---
    give("flint_shard"); give("stick")
    game.execute_experiment(list(inv.items))          # Messer (CUTTING)
    give("fur_cloak")                                  # Isolation
    give("reeds", 5)                                   # KINDLING + Brennstoff
    give("tinder", 5)                                  # start_fire Input (mehrfach)
    give("stick", 10)                                  # start_fire Input
    give("log_oak", 50)                                # Nachlege-Holz (WOOD)

    # Kalte, aber abwendbare Location: Waldrand bei Sturm — Kälte-Stress entsteht
    # v. a. nachts, ein unterhaltenes Feuer hält den Spieler warm.
    game.travel("forest_edge")
    game.current_weather = "STORM"

    cold_ticks, warm_ticks = 0, 0
    for i in range(horizon):
        # Tag/Nacht-Zyklus: überwiegend Nacht, damit periodischer Kälte-Stress
        # entsteht (nachts am kältesten).
        game.tick_counter = 25 if (i % 4 < 3) else 40
        loc = game.current_location
        # Policy: Feuer unterhalten — anzünden, wenn aus; NACHLEGEN, BEVOR der
        # Brennstoff zur Neige geht (sonst würde ein Feuer-Ende den Spieler in
        # der Kälte kaltstellen, obwohl er Holz zum Nachlegen hätte).
        if not (loc.fire_active and loc.fire_fuel > 0):
            game.execute_process("start_fire")
        elif loc.fire_fuel < 15:
            game.stoke_fire()
        # Roh-Umgebung (ohne Feuer) — die tatsächliche Kälte-Bedrohung
        raw = game._get_ambient_temp()
        game._advance_time(1, effort_multiplier=1.0)
        if raw < WARMTH_COMFORT:
            cold_ticks += 1
            if game.player.body_temp >= WARMTH_HYPOTHERMIA:
                warm_ticks += 1
    return warm_ticks / max(1, cold_ticks)


def metric_warmth_stability():
    """Anteil der Kälte-Stress-Ticks mit body_temp >= 35°C (Band-Metrik)."""
    return _aggregate(lambda s: _run_warmth_stability(s))


# ----------------------------------------------------------------------------
# Metrik 11 — recovery_stability (SPEC-009, Probezeit)
# "Verletzung ist spürbar, aber durch Behandlung + Ruhe abwendbar."
# ----------------------------------------------------------------------------

# Verletzungs-Tick = ein Tick, an dem Player.injuries nicht-leer ist (cut blutet
# oder strain aktiv). recovery = der Tick, an dem die Wunde BEHANDELT ist UND der
# Spieler an einem warmen/ruhigen Ort rastet (Feuer oder sheltered) — nur dort
# heilt sie (SPEC-009-Regel). Band 0.3–0.7: unter 0.3 entgleist die Verletzung
# (Heilung wirkungslos → Mechanik tot); über 0.7 ist sie nie eine echte Frist.
RECOVERY_EXPOSE = 30     # Ticks in exponierter, unbehandelter Wund-Phase
RECOVERY_RECOVER = 40    # Ticks in behandelter Ruhe-Phase (Heilfenster)


def _run_recovery_stability(seed, expose=RECOVERY_EXPOSE, recover=RECOVERY_RECOVER):
    """Anteil der Verletzungs-Ticks, die Behandlung + Ruhe abwenden.

    Geführte Policy: Mid-Game-Ausstattung (Heilmaterial + Brennholz vorhanden,
    also Vorbereitung möglich). Eine Wunde wird am exponierten Ort erlitten und
    eine Zeitlang unbehandelt getragen (Phase 1), dann an warmem Ort behandelt
    und gerastet (Phase 2) — die echte `_advance_time`-Heilung entscheidet, ob
    sie abklingt. Deterministisch (kein RNG in der Messschleife).
    """
    random.seed(seed)
    random.Random(seed)  # noqa: F841 — deterministische Ausstattung
    game = GameEngine()
    inv = game.player.inventory

    def give(t, q=1):
        inv.add(create_item(t, q))

    # --- Geführte Mid-Game-Ausstattung (Vorbereitung möglich) ---
    give("plant_fiber", 4); give("mushroom", 2); give("clay_lump", 2)
    give("stick", 8); give("tinder", 4); give("log_oak", 50)

    # Phase 1: exponierte, unbehandelte Schnittwunde (kein Ruhe-Ort, kein Verband)
    game.travel("mountain_peak")
    game.current_weather = "CLEAR"
    game.tick_counter = 45  # Tag — Kälte ist hier Nebensache, es zählt die Wunde
    game.player.injuries["cut"] = {"severity": 1.0, "ticks": 0, "treated": False}
    inj_ticks = rec_ticks = 0
    for _ in range(expose):
        game._advance_time(1)
        if game.player.injuries:
            inj_ticks += 1

    # Phase 2: Rückkehr, Verband anlegen (Behandlung) + Ruhe am Feuer → Heilung
    game.travel("forest_edge")
    game.current_weather = "CLEAR"
    game.tick_counter = 45
    game._light_fire()
    game.player.injuries["cut"]["treated"] = True
    for _ in range(recover):
        game._advance_time(1)
        if game.player.injuries:
            inj_ticks += 1
            if game.player.injuries["cut"]["treated"] and game._resting_warm():
                rec_ticks += 1
    return rec_ticks / max(1, inj_ticks)


def metric_recovery_stability():
    """Anteil der Verletzungs-Ticks, die behandelt+in Ruhe abgewendet werden."""
    return _aggregate(lambda s: _run_recovery_stability(s))


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

# version: wird bei Umdefinition einer Metrik erhöht. Beim Delta wird eine
# Metrik übersprungen, deren Version sich geändert hat → "— (neu definiert)".
# band: optionale Zielbandgrenzen [unter, ober] — Band-Metriken haben keine
# Richtung (kein "höher = besser"), nur "im/unter/über Band".
METRICS = [
    {"key": "actions_to_first_craft", "desc": "Aktionen bis zum ersten erfolgreichen Craft (naiv)", "fn": metric_first_craft, "direction": "niedriger = besser", "version": 1},
    {"key": "blueprint_reachability", "desc": "Anteil erreichbarer Blueprints (N=50)", "fn": metric_reachability, "direction": "höher = besser", "version": 1},
    {"key": "craft_variety", "desc": "Unterschiedliche Craft-Typen (Blueprints + Prozesse) in 100 Aktionen", "fn": metric_craft_variety, "direction": "höher = besser", "version": 2},
    {"key": "skill_spread", "desc": "Überlebens-Spanne optimal vs. zufällig (fallend = gehobene Einsteiger-Decke)", "fn": metric_skill_spread, "direction": "niedriger = besser", "version": 1},
    {"key": "feedback_quality", "desc": "Anteil informativer Rückmeldungen (Label-Stimmt, inkl. NEAR_MISS)", "fn": metric_feedback_quality, "direction": "höher = besser", "version": 3},
    {"key": "content_reachable", "desc": "Anteil sammelbarer definierter Items (inkl. Node-Ref-Prüfung)", "fn": metric_content_reachable, "direction": "höher = besser", "version": 2},
    {"key": "session_depth", "desc": "Aktionen bis nichts Neues passiert (ziel-bewusster naiver Bot, v2)", "fn": metric_session_depth, "direction": "höher = besser", "version": 2, "probation_until": "2026-09-08"},
    {"key": "discovery_gap", "desc": "Abstand erreichbar vs. tatsächlich gefunden", "fn": metric_discovery_gap, "direction": None, "version": 1, "band": (0.2, 0.6)},
    {"key": "forage_pressure", "desc": "Anteil Sammel-Versuche an nicht-volem Node (Knappheit)", "fn": metric_forage_pressure, "direction": None, "version": 1, "band": (0.1, 0.5), "probation_until": "2026-08-20"},
    {"key": "warmth_stability", "desc": "Anteil Kälte-Stress-Ticks, die warm überstanden werden (Feuer/Isolation)", "fn": metric_warmth_stability, "direction": None, "version": 1, "band": (0.4, 0.9), "probation_until": "2026-08-27"},
    {"key": "recovery_stability", "desc": "Anteil Verletzungs-Ticks, die Behandlung + Ruhe abwenden (Verband/Umschlag)", "fn": metric_recovery_stability, "direction": None, "version": 1, "band": (0.3, 0.7), "probation_until": "2026-09-03"},
]

METRIC_VERSIONS = {m["key"]: m["version"] for m in METRICS}


def _probation_label(m):
    """Optional: '(Probe bis TT.MM.)' für neue Metriken in Probezeit."""
    until = m.get("probation_until")
    if not until:
        return ""
    try:
        from datetime import datetime
        d = datetime.strptime(until, "%Y-%m-%d")
        return f" (Probe bis {d.strftime('%d.%m.')})"
    except ValueError:
        return f" (Probe bis {until})"


def _collapse(result):
    if result is None:
        return None
    if isinstance(result, dict):
        return result.get("value")
    return result


def compute_all():
    out = {}
    for m in METRICS:
        key = m["key"]
        try:
            val = m["fn"]()
            if isinstance(val, dict):
                val.setdefault("version", m["version"])
            out[key] = val
        except Exception as e:  # noqa: BLE001 — eine Metrik killt nicht alle
            out[key] = {"error": f"{type(e).__name__}: {e}", "version": m["version"]}
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
    sign = "+" if (val - prev_val) > 0 else ""
    num = f"{sign}{val - prev_val:.3f}"
    if direction is None:  # Band-Metrik — keine Richtungsbewertung
        return num, ""
    better = (direction == "niedriger = besser" and val < prev_val) or \
             (direction == "höher = besser" and val > prev_val)
    arrow = "↑ besser" if better else "↓ schlechter"
    return num, arrow


def _metric_version(data_metrics, key):
    """Version einer Metrik (default 1, falls nicht vorhanden)."""
    m = data_metrics.get(key) or {}
    return m.get("version", 1)


def _band_status(val, band):
    if val is None or band is None:
        return ""
    lo, hi = band
    if val < lo:
        return "unter Band"
    if val > hi:
        return "über Band"
    return "im Band"


def build_table(data, prev):
    lines = [
        "# Project Primal Process — Scorecard",
        "",
        "> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.",
        "> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).",
        "> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.",
        "",
        "| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |",
        "|--------|------|-----------|----------|--------------|",
    ]
    prev_metrics = (prev or {}).get("metrics", {}) if prev else {}
    for m in METRICS:
        key = m["key"]
        version = m["version"]
        band = m.get("band")
        direction = m["direction"]
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
        # Versionswechsel → Metrik nicht mit Vorgänger vergleichbar
        prev_version = _metric_version(prev_metrics, key) if prev_metrics.get(key) else None
        neu_definiert = prev_version is not None and prev_version != version
        if warn:
            delta = "⚠ Content entfernt"
            arrow = ""
        elif prev_version is None:
            delta = "— (Baseline)"
            arrow = ""
        elif neu_definiert:
            delta = "— (neu definiert)"
            arrow = ""
        else:
            delta, arrow = _delta_cell(key, val, prev_val, direction)
            if arrow and arrow != "±0":
                delta = f"{delta} {arrow}"
        # Richtungsspalte: Band-Metrik zeigt Band-Status statt Richtung
        if band is not None:
            dir_txt = _band_status(val, band)
        elif direction == "niedriger = besser":
            dir_txt = "niedriger"
        else:
            dir_txt = "höher"
        lines.append(f"| {key} (v{version}){_probation_label(m)} | {val_txt} | {delta} | {dir_txt} | {m['desc']}{warn} |")
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
    # Band-Metriken dokumentieren (Begründung + Zielband)
    for m in METRICS:
        band = m.get("band")
        if band is not None:
            md = data.get(m["key"]) or {}
            body += f"\n## {m['key']} — Zielband\n\n"
            body += (f"**Band: {band[0]} – {band[1]}.** Keine Richtung (kein "
                     f"\"höher = besser\"). Unter {band[0]} nimmt das Spiel den Spieler "
                     f"an die Hand; über {band[1]} ist es faktisch unentdeckbar. "
                     f"`blueprint_reachability` ({md.get('blueprint_reachability')}) "
                     f"misst, was ein Orakel erreichen kann; `naive_discovery_rate` "
                     f"({md.get('naive_discovery_rate')}) was ein Spieler wirklich "
                     f"findet. Der Abstand dazwischen ist das eigentliche Spiel.\n\n")
    body += f"\n## Details ({today})\n\n"
    body += "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```\n"
    (ROOT / "SCORECARD.md").write_text(body)

    print(json.dumps({"schema": SCHEMA, "date": today, "metrics": {
        k: _collapse(v) for k, v in data.items()}}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
