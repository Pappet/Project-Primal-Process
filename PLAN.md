# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand
Das Spiel startet in Sekundenbruchteilen und läuft stabil: 93 Tests grün, Tag-basiertes Blueprint-Crafting (Axt, Messer) funktioniert, beide Blueprints erreichbar (Reachability 1.0). Aber es gibt zu wenig zu entdecken: In 100 Aktionen gelingt nur **1** unterscheidbarer Craft-Typ (`craft_variety`=1), und ab ~16 Aktionen passiert nichts Neues mehr (`session_depth`=16) — das Experimentiersystem ist da, aber es gibt fast keine Ziele dafür. Content-Deckung: nur 6 von 9 definierten Items sind sammelbar (`content_reachable`=0.667); `raw_meat`, `cooked_meat`, `reeds` hängen unerreichbar, weil das Prozess-System (`processes.json`) nicht in die Engine eingebunden ist. Können bringt bereits etwas (`skill_spread`=0.298) und Feedback ist zu 60% informativ — das ist solide, aber kein Differenzierer.

## Was als nächstes besser werden muss
1. **Craft-Varietät erhöhen** — `craft_variety` von 1 auf ≥ 4. Das Spiel braucht mehr erkennbare, unterscheidbare Craft-Wege (Prozesse + Blueprint-Familien), sonst stirbt die Entdeckung nach dem ersten Fund.
2. **Session-Tiefe erhöhen** — `session_depth` von 16 deutlich steigern. Mehr Aktionen, bis nichts Interessantes mehr passiert.
3. **Content-Deckung schließen** — `content_reachable` von 0.667 auf ≥ 0.8. Die 3 unerreichbaren Items über Mechaniken erreichbar machen (Start: Prozess-System aktivieren).

## Tasks
> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.
> `[ ]` offen · `[~]` in Arbeit · `[x]` erledigt

- [ ] **SPEC-001 — Prozess-System aktivieren.** `execute_process` in Engine, `[p]rocess` im CLI, `reeds` eine Quelle geben. Akzeptanz: `make_sharp_stone`, `create_tinder`, `start_fire` von frischem Start erreichbar; `cooked_meat` aus `raw_meat` das Koch-Prozess; Tests grün.
- [ ] **SPEC-002 — Blueprint-Familien + Discovery-Feedback.** Tag-Familien-Slots, 2–3 Varianten pro Werkzeug-Typ, kategorisierte Fehlschlags-Meldungen. Akzeptanz: ≥ 4 unterscheidbare Crafts in 100 Aktionen; Fehlschlag mit bekanntem Tag nennt Grund; Tests grün.
- [ ] **Baseline verankern.** Scorecard-Lauf einmal pro Woche via Play-Job; `craft_variety`/`session_depth`/`content_reachable` als Ziel-Metriken fahren.

---
*Nächste Scorecard-Kontrolle: nächster Play-Job. Plan-Neufassung: nächster Direktor (So).*
