# SPEC-017 — Subset-Echo: die verwässerte Hand vor dem ersten Craft

> Research (Metrik-Modus), Cron 22.09.2026. Befund aus Play 21.09. + eigener
> read-only Probe (20 Scorecard-Seeds, Profil C). Metrik-Core unberührt.

## Problem

**Metrik-Befund:** Scorecard 21.09. ist über alle 13 Metriken byte-identisch —
das Signal liegt in `play/2026-09-21.md`: Profil C (Menü-naiv, 200 Aktionen,
20 Seeds) = **20/20 Kältetode @132, 0/20 Blueprints, 0/20 Prozesse,
first_craft nie, last_new median 23**. Beim Tod liegen die korrekten Zutaten
im Inventar — 8/11 Blueprints wären craftbar. Die Langeweile-/Todesstelle ist
die Experiment-Schwelle VOR dem ersten Craft.

**Systemische Wurzel (eigene Probe, /tmp/probe_arity2.py):** Über 20 Seeds:
327 Experimente, davon **521 Teilnahmen eines voll feasilben 2-Slot-Blueprints
IN einer 3-Item-Selektion — alle stumm** (nur 4 exakt-arity Fälle, gate- oder
state-blockiert). Ursache ist die Aritäts-Gate-Zeile
`if len(selected_items) != len(bp.slots): continue` — sie steht in
`execute_experiment` (engine/core.py:~698) UND im Near-Miss-Loop
(`_no_match_reason`, Block 2). Der Menü-Spieler wählt bis zu 3 distinct
Templates (`play/naive_menu.py::_step`, Rotation) — damit sind **alle
6 2-Slot-Blueprints (knife, knife_bone, knife_stone, spear, rope, snare)
von JEDEM Signal abgeschnitten**: kein Match, kein NEAR_MISS, kein
2b-Volldeckungssignal. Das Spiel schweigt exakt für den Spieler, der die
richtigen Dinge in der Hand hat, nur "zu viele auf einmal". SPEC-003s
NEAR_MISS würde sogar feuern — es kommt nur nie zur Prüfung.

## Mechanik

- **The Legend of Zelda: Breath of the Wild (Kochen):** beliebige Zutaten in
  den Topf — das Spiel *findet die wirksame Kombination in der Eingabe*, statt
  die Menge der Zutaten zu erzwingen. Die Welt antwortet auf die wirksame
  Teilmenge, nicht auf die Verpackung.
- **Doodle God / Little Alchemy:** Kombinationen werden immer auf dem
  minimalen Paar evaluiert — die "Hand" des Spielers verwässert nie das
  Signal.

Beide folgen demselben Prinzip: **Ein voll gedecktes Rezept in der Hand
verlangt ein Echo, auch wenn die Hand mehr hält als das Rezept braucht.**
Adaptiert als Signal, NICHT als Auto-Craft: Das Craften bleibt exakt
(exakte Arität, die Entdeckungsleistung bleibt beim Spieler) — nur das
Ja/nein-Echo wird teilmengen-bewusst.

## Adaption

- `engine/core.py::_no_match_reason` — neuer Block **2c (Subset-Echo)**,
  nach 2b, vor dem generischen Fallback:
  Enumeriere alle Teilmengen (Größe ≥ 2) von `selected_items`; für jede
  unbekannte, nicht in `near_misses` enthaltene Blueprint mit
  `len(bp.slots) == len(subset)`: wenn `_feasible_mapping(subset, bp)` →
  One-Shot-Hint `SUBSET_HINT:<bp.id>`, registriert in einem neuen
  `Player.subset_hints_seen: Set[str]` (analog `near_misses`, einmalig pro
  Blueprint). Gate-blockierte Volldeckung innerhalb der Selektion wird an den
  bestehenden 2b-Pfad weitergereicht (Subset statt Gesamtmenge prüfen).
- `engine/components.py::Player` — Feld `subset_hints_seen` ergänzen
  (stdlib, serialisiert wie die anderen Sets).
- **Hint-Text** (Feedback-Funktion bei `reason.startswith("SUBSET_HINT:")`),
  generisch, kein Item-/Tag-/Rezept-Leak:
  *"Was du hältst, enthält schon alles — nur nicht beisammen. Räum die Hand auf."*
  Benennt den Fehlermodus (Verwässerung, Über-Arität), nie die Zutaten.
- **Craft bleibt exakt:** `execute_experiment` ändert die Match-Logik NICHT —
  ein Superset-Experiment erzeugt weiterhin kein Werkzeug. Nur das Echo wird
  teilmengen-bewusst.
- `tests/` — Neue Tests: (a) Superset-Selektion mit feasible 2-Slot-Paar
  liefert genau einmal SUBSET_HINT, danach still; (b) Superset erzeugt nie
  ein Werkzeug (Auto-Craft-Gegenprobe); (c) exakter Match-Verhalten
  byte-identisch zum aktuellen Stand; (d) Serialisierung von
  `subset_hints_seen`.
- Constitution: ergänzende Hinweis-Klasse analog WEAR_HINT/PROCESS_HINT;
  kein Rezept-Leak; stdlib only; CLI-Texte bleiben; kein Scorecard-/METRICS-
  Touch.

## Akzeptanzkriterien

1. **Echo-Kriterium (read-only Probe, Profil C, 20 Scorecard-Seeds):** Ein
   3-Item-Experiment, dessen Selektion einen voll feasilben 2-Slot-Blueprint
   enthält, erzeugt mindestens einmal den SUBSET_HINT-Text statt Stille —
   Probe-Zähler > 0 (Vor-Befund dieser Cron: 521 stille Teilnahmen, 0 Echos).
2. **Kein Auto-Craft:** Über alle Probe-Experimente mit Superset-Selektion
   entsteht kein Werkzeug außerhalb der exakten Arität (Blueprints entdeckt
   nur via exakten Match).
3. **pytest grün** inkl. der vier neuen Tests; alle bestehenden Reason-Labels
   und deren Texte unverändert (feedback_quality-Label-Stimmigkeit hält,
   Erwartung: 1.0 ±0).
4. **Kein Scorecard-Write:** `tools/scorecard.py` unangetastet; eine
   compute_all-Delta-Tabelle (vor/nach, gleicher Seed-Satz) wird im
   Dev-Report geführt.

## erwartete Metrik-Wirkung

- **Primär (kein Scorecard-Metrik-Anker, aber messbar in `play/`):** Die
  Entdeckbarkeit VOR dem ersten Craft — Profil-C-Lesung nach Landing sollte
  Blueprints entdeckt > 0/20 zeigen und die Kältetode unter 20/20 senken
  (der Spieler bekommt erstmals Richtung, bevor ein Werkzeug existiert).
- **`discovery_gap` (0.545, Band 0.2–0.6):** kann sinken (naive
  Entdeckungsrate steigt) — Bewegung in die Bandmitte ist Wirkung, nicht
  Opfer; Bandverletzung ist Abbruchkriterium.
- **`session_depth` (52.5):** mögliches Aufwärts-Delta, wenn der naive Bot
  über den ersten Craft hinaus entdeckt — additive Wirkung, im PLAN-Ziel 1
  Sinne; keine Gate-/Metrik-Änderung.
- **`craft_variety` / `actions_to_first_craft`:** mögliche Nebeneffekte in
  ohnehin gewünschter Richtung (mehr Crafts, niedrigerer Kaltstart); sonst
  ±0. Alle übrigen Band-Metriken sind strukturell unberührt (kein neuer
  Content, keine Ökonomie-Änderung).
