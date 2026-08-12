# REC-001 — Patch-Entwurf: `_pair_slots` Tag-Familien auflösen (Vorschlag an Peter)

> STATUS: **Vorschlag — wartet auf Peters Freigabe.** Nicht anwenden/committen bis Freigabe.
> Erstellt: 2026-08-12 (Dev cron). Quelle: PLAN.md Task REC-001, BACKLOG 07.08./11.08.
> Constitution: Metrik-Berechnung (`tools/scorecard.py`, `METRICS`) ist unantastbarer Kern → **Änderung braucht Peters Freigabe.**

---

## Problem

`blueprint_reachability` meldet **0.75** statt wahr **1.0** — `_pair_slots` matcht Slot-Tags **literal**
(`by_tag.get(tag)`), kennt `TAG_FAMILIES` (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`, `SHARP_OR_HARD`) nicht.
`spear` und `spear_bound` haben Familien-Slots (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`); kein Item trägt den
Familien-Namen als literalen Tag → beide zählen fälschlich als **unreachable**, obwohl die Engine sie
sauber craftet (alle 8 Blueprints enginseitig SUCCESS, verifiziert).

Folge: `discovery_gap = reach − naive` ist **unterschätzt** (0.375, komfortabel im Band 0.2–0.6),
während der **wahre Wert 0.625 über der Band-Obergrenze** liegt.

## Vorgeschlagener Patch

Nur `tools/scorecard.py::_pair_slots` — Familien auf Mitglieds-Tags auflösen, analog
`engine.core._slot_satisfied` (das die Engine fürs Crafting nutzt). Damit zählt der Zähler exakt das,
was die Engine wirklich craften kann.

```python
def _pair_slots(game, bp):
    from engine.core import TAG_FAMILIES  # oder oben importieren
    inv = [it for it in game.player.inventory.items
           if it.quantity >= 1 and it.condition > 0]
    by_tag = {}
    for it in inv:
        for t in it.tags:
            by_tag.setdefault(t, []).append(it)

    # Slot-Tag auf die Menge der Tags auflösen, die ihn erfüllen (Familie o. selbst)
    candidates = []
    for _slot, tag in bp.slots.items():
        members = TAG_FAMILIES.get(tag, {tag})
        pool = []
        for m in members:
            pool.extend(by_tag.get(m, []))
        candidates.append(pool)

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
```

Der Rest von `_pair_slots` (Backtracking über distinkte Item-Objekte) bleibt unverändert. Kein
Engine-Code, kein Daten-Code, keine andere Metrik wird angefasst.

## Wirkungsabschätzung (verifiziert, n=50 & 20 Seeds, deterministisch)

| | gemeldet (jetzt) | wahr (mit Patch) |
|---|---|---|
| `blueprint_reachability` | 0.75 | **1.0** |
| `naive_discovery_rate` | 0.375 | 0.375 (unverändert — Engine-consistent) |
| `discovery_gap` | 0.375 (im Band) | **0.625 (über Band 0.6)** |

- Einzige Änderung: `spear`, `spear_bound` gehen `False → True` im `per_blueprint`-Detail. Alle 6 anderen
  Blueprints bleiben `True`.
- **Der gemeldete "komfortable" Gap war ein Artefakt.** Der wahre Gap liegt über dem Band und heißt:
  naive Spieler findet (0.375) deutlich weniger als erreichbar wäre (1.0) — die Discovery-Lücke ist
  **real groß**, nicht klein.

## Optionen für Peter

- **A (empfohlen):** Patch freigeben → `discovery_gap` steigt auf ~0.625, wird ehrlich über Band gemeldet.
  Danach ist SPEC-003 (partieller Match) erst **verifizierbar** — sein Ziel war Gap-Reduktion, und ohne
  echten Wert lässt sich die Wirkung nicht messen. Das ist das explizite Gatter in PLAN.
- **B:** Patch ablehnen / zurückstellen — `discovery_gap` bleibt unterschätzt und als Ziel unbrauchbar;
  SPEC-003 bleibt suspendiert.

## Tests (nur falls freigegeben — Bestandteil des späteren Freigabe-Commit)

`tests/test_scorecard.py`:
- `_pair_slots` löst `SHARP_OR_RIGID` / `RIGID_OR_FIBER` auf (spear, spear_bound reachable).
- `metric_reachability() == 1.0` für den aktuellen 8-Blueprint-Satz.
- `discovery_gap` wird korrekt > Band gemeldet (kein stilles Abschwächen).

## Beziehung zu SPEC-006 / tool-aware reachability

Dieser Patch **reicht NICHT** für SPEC-006. Er löst nur Familien auf; ein Tier-2-Slot mit echtem
Tool-Tag (`CUTTING`/`CHOPPING`) bleibt unreachable, weil `metric_reachability` im Fresh-Gather-Lauf
**nie Werkzeuge baut**. Tool-gated Tier-2 braucht zusätzlich "tool-aware reachability" (Zähler modelliert
Tool-Bau als Vorschritt) — separate, ebenfalls freigabepflichtige Entscheidung (JOURNAL 11.08., Optionen
A/B/C). REC-001 ist davon unabhängig lieferbar.

## Constitution-Check

- Keine Metrik entfernt/umdefiniert/abgeschwächt — nur die **Berechnung** einer Zählweise korrigiert
  (Version 1 → 2 der Metrik `discovery_gap`/`blueprint_reachability`). Erhöht ehrlich den Wert, der bisher
  unterschätzt wurde. Das ist ein Korrektur-Entwurf, kein Metrik-Spiel.
- Anwendung erst nach Peters Freigabe (Constitution: `tools/scorecard.py` + `METRICS` = unantastbar).
