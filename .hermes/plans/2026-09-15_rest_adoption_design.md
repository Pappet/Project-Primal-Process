# Design-Skizze (vor TDD, Pflicht laut Plan-Ziel 2 / Direktor-Freigabe 13.09.)

**Auftrag:** rest_adoption in METRICS aufnehmen (probation_until 2026-09-24).
Direktor-Freigabe liegt vor (JOURNAL 13.09. Zeile 377: "Aufnahme durch Dev im
nächsten Dev-Lauf — FREIGEGEBEN, Proposal verifiziert, Erstlesung 0.333,
Policy dokumentiert"). Constitution: Metriken dürfen ergänzt werden — die
Aufnahme ist ausdrücklich der freigegebene Fall; kein Entfernen/Umdefinieren.

**Eintrag (tools/scorecard.py, METRICS):**
```python
{"key": "rest_adoption",
 "desc": "Anteil Rast-Fenster mit Outcome (Heilung vollendet oder Nacht warm überstanden)",
 "fn": metric_rest_adoption, "direction": None, "version": 1,
 "band": (0.4, 0.85), "probation_until": "2026-09-24"}
```
Am Ende der METRICS-Liste (Dict-Order = Präzedenz, wie snare im Blueprints-
Array). v1, Band [0.4, 0.85] aus dem Proposal (beobachtend in der Probezeit —
Kalibrierung darf das Band nach Probe-Ende noch bewerten, kein Plan-Ziel bis 24.09.).

**Runner `run_rest_adoption(seed)` (neu, direkt vor METRICS-Block, neben
_run_warmth_stability):** Proposal-Skizze gefolgt, zwei dokumentierte
Abweichungen aus der Spielmechanik, beide eng am Erstlesungs-Bot (Play
11.09., guided-Grundierung):

- **Warmup statt Blind-Start:** die Proposal-Skizze startet blanko. Die
  Erstlesung 0.333 nutzte guided-Grundierung (Ausstattung + start_fire) —
  der Proposal-Text selbst nennt als Policy (1) "nach eigenem treat_*",
  d. h. der Bot muss die Behandlungskette besitzen, um den Trigger überhaupt
  lesen zu können. Erstlesungs-kompatible Grundierung (identische Items,
  forest_edge, Feuer sofort): flint_shard+stick→Messer-Experiment, fur_cloak,
  plant_fiber×4 (bandage→treat_cut), mushroom×2+clay_lump×2 (poultice→
  treat_strain), stick×12, tinder×5, log_oak×50. Danach blinder natürlicher
  Verlauf: gather, trigger-Prüfung, Rast-Fenster.
- **Nacht-Erkennung über die Uhr-Formel** (core.py:287: hour = tick%144/6;
  Nacht = hour < 6 oder > 20): der Proposal-Pseudocode prüft
  `night_mod aktiv` abstrakt — konkrete Formel hier verankert, getestet
  gegen die echte Ambient-Berechnung.

**Loop (HORIZON 500, Determinismus-Konventionen wie die Nachbar-Runner):**
`random.seed(seed)` + `rng = random.Random(seed)`; Energie-Gate `_eat_best`
unter 300 (Proposal-Skizze); Trigger-Prüfung: (1) unbehandelte Verletzung
heilen — treat-Prozess, dann Rast-Loop bis Verletzung weg oder Fenster 40
Ticks (Proposal-Trigger (1)); (2) Nacht-Beginn (hour 20→21-Crossing) mit
Feuer — Rast-Loop durch die Nacht bis hour ≥ 6, stoke wenn fire_fuel < 8
(FIRE_DYING-Schwelle, Proposal-Trigger (2)); (3) nie ohne `_resting_warm()`
(Proposal-Trigger (3): bei Nacht-Beginn ohne Feuer/Warm-Ort → travel nach
hidden_cave als Warm-Ort-Zugriff — kein Zuhause-Bau, keine Bot-Optimierung
über den Proposal-Text hinaus). Kein eigenes RNG in der Messschleife: der
einzige rng.draw ist die Gather-Location-Wahl (sammelt an forest_edge, aus
demselben Grund wie der Warmth-Bot). `rest()` führt keine neuen Würfe ein
(nur %-12-Wetter-Crossings des bestehenden `_advance_time`).

**Outcome-Buchung je Fenster (Proposal-Definition):** healed = Verletzung
während des Fensters entfernt; survived_night = body_temp >= 35.0 nach der
ersten Nacht-Phase im Fenster (night_mod aktiv). Fenster ohne potentielles
Outcome (kein Trigger möglich — kann im Bot-Design nicht entstehen, da nur
Trigger-Fenster zählen) → keine Buchung. None bei 0 Fenstern, wie die
anderen Band-Metriken.

**Erwartete Lesung:** Erstlesung 0.333 (p25 0.000, p75 0.500, n=20) lag
unter Band — BEVOR T1 (Komfort-Cutoff) und T2 (stick→WOOD) landeten. Mit
T1+T2 im Rücken (Feuer hält die Nacht, Rast am Feuer überhitzt nicht) sollte
der Wert steigen; die Probezeit-Kalibrierung liest, wo er jetzt steht. Keine
Scorecard-Wächter erwartet: die anderen 12 Metriken bleiben unberührt — der
neue Eintrag ist ADDITIV, compute_all() gibt die alten 12 Werte unverändert
zurück (Delta-Tabelle dokumentiert alle 13).

**Risiko-Abgrenzung (Constitution):** additiver Metrik-Eintrag = erlaubt
(ohne Peters Freigabe nötig — Entfernen/Umdefinieren bräuchte sie); die
bestehenden 12 Metriken werden weder berechnet noch definiert noch gelesen.
Kein Spiel-Code-Touch, kein Data-Touch. Die Probezeit-Markierung
(probation_until) verhindert Plan-Ziel-Status bis 24.09.

**Test-Plan (TDD, tests/test_scorecard.py-Erweiterung):**
- R1: METRICS-Eintrag vorhanden, key/desc/version/band/probation_until exakt;
  probation_label rendert "(Probe bis 24.09.)".
- R2: compute_all() liefert rest_adoption mit value (kein Error-Eintrag),
  version 1; die 12 Alt-Metriken byte-identisch gegen Tages-Baseline
  (Additivität — der eigentliche Wächter).
- R3: Runner-Verträge: deterministisch (gleicher Seed → gleicher Wert);
  None-Handling (0 Fenster → None → _collapse → None); Fenster-zählende
  Invariante (windows > 0 bei Standard-Setup — der Bot erreicht die Trigger
  im natürlichen Verlauf).
- R4: Nacht-Formel-Test: run-interner Nacht-Check identisch zur
  Ambient-Berechnung (hour < 6 oder > 20) — gegen core._get_ambient_temp
  mit/ohne Feuer-Setup verifiziert.
- R5: Outcome-Buchung: künstlicher treated-injury-Run heilt im Fenster
  (scored increment); künstlicher Nacht-Run mit Feuer + bt ≥ 35 bucht
  survived; Fenster ohne Outcome zählt windows ohne scored.
- R6: HASH-Seed-Stabilität: 3 Hash-Seeds → identischer Wert (Set-Iteration
  ist im Runner nicht am Stream).

## Abweichungen bei der Umsetzung (aus dem Test-Loop gelernt)

1. **Feuer-Upkeep im Tagespfad nötig:** die reine Trigger-Schleife ließ das
   Warmup-Feuer nach START_FIRE_FUEL=24 Ticks sterben → die erste Nacht-
   Kreuzung (tick 121) war feuerlos → 0 Nacht-Fenster → None. Erstlesung v5
   hatte diesen Upkeep implizit (Erbe aus `_warm_here` von guided_full).
   Fix: stoke bei fuel < REST_STOKE_AT, Neuzündung (start_fire) wenn möglich.
2. **REST_STOKE_AT = 15.0 statt 8.0:** die Erstlesungs-Policy (play 11.09.)
   stokt bei fuel < 15 (v5, dokumentiert) — nicht bei FIRE_LOW_FUEL=8.
   Konvention folgt der Erstlesung, nicht dem Proposal-Pseudocode.
3. **Verletzungs-Trigger bleibt rare-Path:** an forest_edge entsteht im
   Blind-Verlauf faktisch keine Verletzung (kein SHARP-Node, exposure 0.5 <
   0.8-Schwelle) — der Heil-Trigger trägt die Metrik über die Night-Achse
   hinweg sichtbar, genau wie in der Erstlesung (nur der Heil-Trigger las
   >0). Der Scorecard-Run bestätigt das Muster.
