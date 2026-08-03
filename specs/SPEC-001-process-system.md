# SPEC-001 — Prozess-System aktivieren (Craft-Varietät & Content)

STATUS: offen · angelegt 2026-08-03 · Quelle: Baseline-Scorecard

## Problem
**Metrik:** `craft_variety` = 1 (nur 1 erfolgreicher Craft-Typ in 100 Aktionen), `session_depth` = 16, `content_reachable` = 0.667.
**Befund:** Das Prozess-System (`data/processes.py`, `processes.json`) existiert mit 3 Prozessen (Knapping, Zunder, Feuer), ist aber **nicht in die Engine eingebunden**. Spieler können nur über `execute_experiment` (Blueprints Axt/Messer) craften. Ergebnis: Es gibt fast keine erkennbaren Craft-Wege, nichts Neues passiert nach ~16 Aktionen, und 3 definierte Items (`raw_meat`, `cooked_meat`, `reeds`) sind unerreichbar, weil keine Mechanik sie erzeugt/transformiert.

## Mechanik
Aus *Cataclysm: Dark Days Ahead* / *UnReal World*: Prozesse sind **Transformationen** mit Umgebungs-Kontext — anders als kombinierendes Blueprint-Crafting verwandeln sie ein Item mit Werkzeug in ein anderes (trocknen, kochen, brennen, fermentieren). `ProcessDef` trägt bereits `inputs`, `tools`, `outputs`, `duration_ticks`, `required_tag_in_env`.

## Adaption (konkret für PPP)
Dateien: `engine/core.py`, ggf. `main.py`.
1. Neue Engine-Methode `execute_process(process_id, player)`:
   - Prüft `required_tag_in_env` gegen die aktuelle Location (z.B. `HEAT_SOURCE` für Kochen — vorerst optional/weich, kein neues Tag nötig).
   - Konsumiert `inputs` (item_id: menge) und `tools`-Tags aus dem Inventar.
   - Erzeugt `outputs`; fügt sie dem Inventar hinzu.
   - Kostet `duration_ticks` an Aktion + Energie (analog `_advance_time`).
2. `main.py`: Action `[p]rocess` mit Auswahl der verfügbaren Prozesse für die aktuelle Location.
3. **Blocker-Behob:** `reeds` bekommt eine Quelle (Hidden-Cave-Node) ODER `make_sharp_stone` bleibt, damit `create_tinder` (braucht reeds) überhaupt erreichbar wird.
4. Für die Scorecard nutzbar: Prozesse zählen als eigener Craft-Typ in `craft_variety`.

## Akzeptanzkriterien
- `game.execute_process("make_sharp_stone", ...)` mit 2× pebble liefert `sharp_stone`.
- `create_tinder` und `start_fire` sind von einem frischen Start aus erreichbar (alle Inputs sammelbar).
- `cooked_meat` ist aus `raw_meat` durch einen Koch-Prozess erzeugbar.
- `[p]rocess` im CLI aufrufbar.
- `python -m pytest` bleibt grün.

## Erwartete Metrik-Wirkung
- `craft_variety`: 1 → ≥ 3 (Axt/Messer + mind. 2 Prozess-Outputs).
- `content_reachable`: 0.667 → ≥ 0.8 (raw_meat/cooked_meat/reeds erreichbar).
- `session_depth`: steigt (mehr erkennbare Wege).
