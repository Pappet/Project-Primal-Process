# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand
Das Spiel startet in Sekundenbruchteilen und läuft stabil: 130 Tests grün, Tag-basiertes Blueprint-Crafting (Axt, Messer) funktioniert, beide Blueprints erreichbar (Reachability 1.0), und Spieler-Feedback nennt jetzt die fehlende Eigenschaft statt „Nichts passiert." (feedback_quality misst die Spielersicht). Aber es gibt zu wenig zu entdecken: `craft_variety`=0.5 (Median), `session_depth`=24 — das Experimentiersystem ist da, aber es gibt fast keine Ziele dafür. `discovery_gap`=0.5 (Band 0.2–0.6): das Orakel erreicht 100%, ein naiver Spieler nur 50% — die Lücke ist im Zielband, aber an der oberen Grenze. Content-Deckung: nur 6 von 9 definierten Items sammelbar (`content_reachable`=0.667); `raw_meat`, `cooked_meat`, `reeds` hängen unerreichbar, weil das Prozess-System nicht eingebunden ist.

## Was als nächstes besser werden muss
1. **Discovery-Gap im Band halten** — `discovery_gap` (Band 0.2–0.6) liegt bei 0.5. Neue Mechaniken müssen die naive Entdeckungsrate heben, ohne die Lücke über 0.6 zu treiben (unentdeckbar) oder unter 0.2 zu drücken (Überführung).
2. **Session-Tiefe erhöhen** — `session_depth` von 24 steigern. Mehr Aktionen, bis nichts Interessantes mehr passiert.
3. **Content-Deckung schließen** — `content_reachable` von 0.667 auf ≥ 0.8. Die 3 unerreichbaren Items über Mechaniken erreichbar machen (Start: Prozess-System aktivieren).

## Tasks
> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.
> `[ ]` offen · `[~]` in Arbeit · `[x]` erledigt

- [x] **SPEC-001 — Prozess-System aktivieren.** `execute_process` in Engine, `[p]rocess` im CLI, `reeds` eine Quelle geben. Akzeptanz: `make_sharp_stone`, `create_tinder`, `start_fire` von frischem Start erreichbar; `cooked_meat` aus `raw_meat` das Koch-Prozess; Tests grün.
- [x] **SPEC-002 — Blueprint-Familien + Discovery-Feedback.** Tag-Familien-Slots, 2–3 Varianten pro Werkzeug-Typ, kategorisierte Fehlschlags-Meldungen. Akzeptanz: ≥ 3 Werkzeugtypen mit je ≥ 2 Varianten; Fehlschlag mit bekanntem Tag nennt Grund; Tests grün. *(Dev 2026-08-05)*
- [ ] **SPEC-003 — Partielle Match-Erkennung (Discovery).** ⚠️ **Konflikt (BACKLOG 05.08.):** `discovery_gap` ist laut aktueller Scorecard bereits 0.25 (Unterkante) und `naive_p25` = 0.5 — die Effekte, die SPEC-003 liefern sollte, sind durch SPEC-001/Content-Bau schon eingetreten. Umsetzung riskt die Gap unter 0.2 (Überführung). **Aussetzung bis Direktor-Review (So) — nicht blind umsetzen.**
- [x] **SPEC-004 — Ressourcenerschöpfung & Regeneration (Foraging).** Vorratsbasierte Nodes: Ernte reduziert Vorrat, Erfolg skaliert mit `stock/max_stock`, Regeneration über `_advance_time`. Akzeptanz: erschöpfter Node liefert `DEPLETED`+Meldung statt "nichts"; Regen stellt ihn wieder her; `session_depth` steigend; Tests grün. Ohne bestehende Metrik zu verschieben — vertieft Nachhaltigkeit/Zeit-Horizont. Metrik-Vorschlag: `forage_pressure` (Band 0.1–0.5), aufgenommen in Probezeit bis 20.08. (Erstwert 0.71, über Band — Kalibrierung offen, siehe BACKLOG). *(Dev 2026-08-06)*
- [ ] **Rückwärtsprüfung verankern (Fix-Session 03.08.).** `skill_spread` (0.298→0.315) und `session_depth` (16→24) stiegen durch die Zählweisen- und Median-Umstellung, ohne Spielerlebnis-Änderung. Nicht stillschweigend stehen lassen: beim nächsten Play-Lauf prüfen, dass diese Werte echte Spielerfahrung abbilden, sonst Metrik-Version bumpen.
- [ ] **Baseline verankern.** Scorecard-Lauf einmal pro Woche via Play-Job; `discovery_gap`/`session_depth`/`content_reachable` als Ziel-Metriken fahren.

---
*Nächste Scorecard-Kontrolle: nächster Play-Job. Plan-Neufassung: nächster Direktor (So).*
