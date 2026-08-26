# REC-002 — Tool-aware Reachability (Patch-Entwurf + Anwendung)

> STATUS: **Freigegeben + angewendet** (Peter, 2026-08-22 Pkt. 6, "Option A freigegeben"). Angewandt in Dev-Session 26.08.
> Quelle: PLAN.md Task REC-002; DECISIONS_Response_2026_08_21.md Pkt. 6.
> Constitution: `tools/scorecard.py` + `METRICS` sind unantastbarer Kern — die Änderung war
> freigabepflichtig und ist es geblieben. Die Freigabe (Pkt. 6) erteilt sie explizit,
> nachdem REC-001 dieselbe Gate-Familie geöffnet hat.

---

## Problem

`metric_reachability` fragt jeden Blueprint **einmal in Listenreihenfolge**
gegen das Re-Gather-Inventar ab und hat **nie Werkzeuge gebaut** und deren
erzeugte tragenden `tool_tags` (`CORD`/`CUTTING`/`CHOPPING`/`PIERCE`/`SHOVEL`)
**nicht als Zutat weiterverwendet**:

- `cord_spear` fordert Slot `bind: CORD`. `CORD` existiert in der Rohwelt nicht —
  es entsteht erst, wenn `rope` (dessen `tool_tags=["CORD"]`) gebaut wird.
- Der alte Zähler schaffte `cord_spear` **nur**, weil `rope` zufällig *vor*
  `cord_spear` in der Blueprint-Liste stand und das gebaute `rope` (traegt das
- **Listenkopplung, keine Engine-Wahrheit**: eine
  andere Blueprint-Reihenfolge (oder ein neuer Tier-2-Blueprint, der einen
  Werkzeug-Tag als Zutat braucht, wie SPEC-006) hätte ihn fälschlich als unerreichbar
  gemeldet oder vom Listentiming abhängig gemacht.

Das war der bekannte REC-001-Nachfolger: REC-001 löste die Familien; REC-002
muss den **Werkzeug-Bau als Vorschritt** modellieren, sonst kann SPEC-006
(Werkzeug als Zutat) den geschützten `blueprint_reachability` nicht sauber
hoch oder das Band halten.

## Vorgeschlagener / angewandter Patch

`tools/scorecard.py`:

1. Neue Helferin `_reachable_blueprints(game, bps, loc_ids, gather_initial=8, gather_refill=2)`:
   ein **Fixpunkt-Loop** über die Blueprint-Menge. Jeder Durchlauf versucht alle noch
   nicht gebauten Blueprints, deren Slots aus dem aktuellen Inventar (Rohmaterial +
   schon gebaute Werkzeuge) füllbar sind und deren `min_survival_req`-Gate offen ist.
   Gelingt ein neuer Craft, wird das gebaute Werkzeug (mit seinen `tool_tags`) dem
   Inventar hinzugefuegt und die Survival-Score steigt. Zwischen Durchläufen werden
   verbrauchte Rohmaterialien nachgesammelt, damit knapper Vorrat nicht faelschlich als
   Unerreichbarkeit zählt. Terminiert, weil jede Blueprint hoechstens einmal in die
   `crafted`-Menge wandert.
2. `metric_reachability` ruft statt des Ein-Schritt-LOOP pro Run genau diese
   Fixpunkt-Helferin auf.

Kein Engine-Code, kein Daten-Code verändert. Andere Metriken unberührt.

## Wirkungsabschätzung (verifiziert, n=50 & 20 Seeds, deterministisch)

| | alt (Ein-Schritt-Listenlaeufer) | neu (Werkzeug-Fixpunkt) |
|---|---|---|
| `blueprint_reachability` | 1.0 (nur per Listenkopplung, fragil) | **1.0** (Engine-Wahrheit, ordnungsunabh. + explizit Werkzeug-Vorschritt) |
| `per_blueprint` | alle True (nur weil rope vor cord_spear) | alle True (Fixpunkt baut rope, dann cord_spear) |
| `naive_discovery_rate` | 0.4 | **0.4 (unverändert — Engine-consistent)** |
| `discovery_gap` | 0.6 (Banddecke) | **0.6 (Banddecke, unverändert)** |
| Laufzeit sensor | — | ~+0.6 s / 50 Runs (vernachlaessigbar) |

- **Keine andere Metrik gesenkt:** `blueprint_reachability` 1.0, `discovery_gap` 0.6,
  `naive_discovery_rate` 0.4 — identisch. Der Fixpunkt hat denselben wahren Gap.
- Einzige Aenderung in der Zählweise: `_reachable_blueprints` statt `_pair_slots`-Einzelschritt.
- Der Kern wäre die **Ordnungsunabhängigkeit**: Der Zähler hängt nicht mehr daran, dass ein
  Werkzeug erzeugender Blueprint zufällig VOR seiner Verwendung in der Liste steht.

## Warum das die spec-006-Grundlage ist

SPEC-006 (Werkzeug als Zutat) fuegt Tier-2-Blueprints hinzu, deren Slots einen
Werkzeug-Tag als Zutat fordern. Der alte Zähler haette diese als unerreichbar
abgestempelt (reiner Listen-Zufall), `blueprint_reachability` waere unter 1.0
gefallen. Mit REC-002 baut der Oracle-Fixpunkt das Werkzeug zuerst und nutzt
dessen Tag als Zutat — die Erreichbarkeit misst jetzt echte Craftbarkeit, nicht
Listen-Timing. Damit kann SPEC-006 nur noch so viel melden, wie die Engine wirklich
kann.

## Tests (Bestandteil des Freigabe-Commit)

`tests/test_scorecard.py` — `TestRec002ToolAwareReachability`:
- `test_order_independent_closure`: gleiche Erreichbarkeit bei natuerlicher und
  reverse-Blueprint-Reihenfolge (Listenkopplung weg; rope im Fixpunkt).
- `test_blueprint_requiring_missing_gear_is_not_reachable`: ein Slot-Tag, den weder
  Node noch Werkzeug-Tag liefert, wird NICHT als erreichbar gelogen (kein falsches Positiv).
- `test_full_set_still_one`: `metric_reachability()["value"] == 1.0`, alle per_blueprint True.
- `test_discovery_gap_still_at_band`: gap ≤ 0.6, blueprint_reachability == 1.0.
- `test_closure_is_a_repeatable_set`: Fixpunkt stabil bei gleichem Seed.

Gesamtsuite: 236 passed.

## Constitution-Check

- **Constitution:** Metrik-Berechnung in `tools/scorecard.py` wurde geändert — **nur mit
  expliziter Freigabe** (Peter, 22.08. Pkt. 6). Keine Metrik entfernt/umdefiniert/
  geschwächt — der Zähler misst jetzt ehrlich, was die Engine kann (inkl. Werkzeug-Bau),
  die Werte bleiben identisch.
- Anwendung erst nach Peters Freigabe und nach Verifikation (Reachability = Engine-Truth,
  keine andere Metrik geschwächt) — erledigt.

## Ausblick

SPEC-006 (Werkzeug als Zutat) kann jetzt auf REC-002 aufsetzen: Tier-2-Blueprints mit
Tool-Tag-Slot registrieren sich im Fixpunkt als erreichbar, solange die Engine die
Werkzeuge bauen kann. `discovery_gap` als Bandmetrik wird dabei beobachtet.