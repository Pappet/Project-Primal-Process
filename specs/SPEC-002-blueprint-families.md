# SPEC-002 — Blueprint-Familien + Discovery-Feedback (Craft-Varietät)

STATUS: offen · angelegt 2026-08-03 · Quelle: Baseline-Scorecard

## Problem
**Metrik:** `craft_variety` = 1, `session_depth` = 16.
**Befund:** Nur 2 Blueprints (Axt, Messer). Der Spieler lernt nach dem ersten Fund alles, was es gibt — danach sind alle Experimente `"Nichts passiert."` und nichts Neues entsteht. Die Kombinatorik existiert, aber es gibt zu wenige Ziel-Blueprints und keinen Hinweis, dass Experimentieren überhaupt etwas bringt.

## Mechanik
Aus *Neo Scavenger* (Tag-basierte Item-Substitution) + *Ancestors* (neuronales Entdeckungssystem): Blueprints definieren **Tag-Slots** statt Item-IDs (`{head: [SHARP,STONE], handle: [LONG,RIGID]}`). Eine Familie von Blueprints (alle Axt-/Messer-/Werkzeug-Varianten) teilt dieselben Slot-Typen, sodass **viele verschiedene Item-Kombinationen** zu gültigen, unterschiedlichen Werkzeugen führen. Dazu ein Discovery-Log: Fehlschläge geben einen *kategorisierten* Grund (fehlender Tag-Typ, falsche Slot-Zahl) statt eines generischen Strings.

## Adaption (konkret für PPP)
Dateien: `data/blueprints.json`, `engine/crafting.py`, `engine/core.py:execute_experiment`.
1. Blueprint-Slots auf **Tag-Familien** erweitern: z.B. `{head: "HARD_OR_SHARP", handle: "RIGID", binding: "FIBER"}` mit Subsumptions-Regel (Layer über `tags`), sodass `flint_shard` (HARD+SHARP) mehrere Rollen füllen kann.
2. **Blueprint-Familien:** pro Werkzeug-Typ 2–3 Varianten (Axt: Stein-/Knochen-/Holzkopf) mit leicht abweichendem `result_name` und `base_efficiency` → mehr unterscheidbare Craft-Ergebnisse.
3. **Discovery-Feedback:** In `execute_experiment` liefert ein Fehlschlag statt `"Nichts passiert."` einen Grund, sobald der Spieler mind. einen Tag des gesuchten Typs kennt:
   - "Fast. Dieser Kombination fehlt ein scharfes Teil." (wenn ein RIGID+FIBER aber kein SHARP vorhanden)
   - Sonst weiterhin generisch, bis genug Tags gesammelt sind (kein Rezeptbuch-Kram).
4. Richtung zählt nicht ein in kraftvolles neues Tag; es erweitert nur vorhandene Slot-Matching-Logik.

## Akzeptanzkriterien
- Mind. 5 unterschiedliche erfolgreiche Craft-Ergebnisse (über Axt/Messer + Familien) in 100 Aktionen erreichbar.
- Ein Fehlschlag mit mind. einem bekannten Ziel-Tag nennt einen konkreten Grund (kein generisches `"Nichts passiert."`).
- Ein Spieler, der erst ein SHARP-Item gefunden hat, bekommt kategorisiertes Feedback.
- `python -m pytest` bleibt grün.

## Erwartete Metrik-Wirkung
- `craft_variety`: 1 → ≥ 4.
- `session_depth`: steigt deutlich (Experimentieren lohnt sich länger).
- `feedback_quality`: 0.6 → steigt (kategorisierte Fehlschläge zählen als informativ).
