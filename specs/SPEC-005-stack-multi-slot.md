# SPEC-005 — Mengen-basiertes Mehrfach-Slot-Crafting (Stack füllt N Slots)

STATUS: erledigt (Dev 10.08.) · angelegt 2026-08-09 (Direktor-Triage) · Quelle: BACKLOG 2026-08-05 (Dev) — Design-Entscheidung an den Direktor delegiert.

## Problem
`Inventory.add` verschmilzt gleichnamige Items in einen Stack (`quantity`). Ein Blueprint, dessen zwei Slots dasselbe Tag-Anforderungs-Profil verlangen (z.B. Speer 2× `RIGID`), ist im CLI **nicht craftbar, wenn der Spieler nur eine Materialsorte hat**: 2× `stick` sind nie als zwei separate Items auswählbar, weil es nur einen Stack `stick ×N` gibt. Der Spieler ist gezwungen, zwei *distinkte* Materialien zu kombinieren (Speer = reeds+Ast statt 2×Ast) oder leer auszugehen, obwohl er 2+ Stöcke besitzt. Das ist eine Lücke in der Hand, keine Metrik-Schwäche — ein plausibles Craft von Hand kann das Spiel nicht ausführen.

## Mechanik
Ein Stack mit `quantity N` darf **N identische Slots** eines Blueprints füllen. Die Engine matcht nicht mehr nur per Item-Objekt, sondern berücksichtigt die Mengen-Grenze eines Stacks: derselbe Stack kann mehrfach in `selected_items` auftauchen, solange `quantity` die Mehrfach-Nutzung deckt; jede Nutzung konsumiert `quantity -= 1`.

## Adaption (konkret für PPP)
Dateien: `main.py` (CLI-Item-Auswahl), `engine/core.py` (`execute_experiment`/`_create_tool`), `engine/components.py` (`Inventory`), `tests/test_engine.py`.

1. **`main.py` — Auswahl:** selbes Item/Stack erlaubt mehrfach auswählen, wenn `quantity >= (Anzahl bisheriger Nutzungen + 1)`. Aktuell blockiert die Auswahl vermutlich Duplikate oder es fehlt die Menge-Nutzung. CLI zeigt: `[3] 4x Stock` → zweimal wählbar (Verbrauch 2 von 4).
2. **`engine/core.py::execute_experiment`:** Duplikat-Selektion des*selben Stack-Objekts* in `selected_items` bereits funktional — `_slot_satisfied` matcht pro Position, Permutations-Schleife behandelt identische Objekte an verschiedenen Positionen. Verifizieren, dass zwei identische Slots mit einem Stack `quantity>=2` matchen; sonst Menge-Logik ergänzen.
3. **`engine/core.py::_create_tool`:** Konsum-Zweig für Mehrfach-Nutzung desselben Stacks validieren (Loop wird bereits zweimal durchlaufen; `c.quantity>`-Dekremente müssen ≥ Anzahl Nutzungen decken). Kein `remove()` vor `quantity>1`.
4. **`Inventory`:** unbeabsichtigte Merge-Logik, die eine Mehrfach-Selektion während des Matchens zerstört, prüfen/entschärfen.
5. **Constitution-Check:** kein Rezeptbuch geändert, nur bestehende mathematische Lücke geschlossen; CLI-Text bleibt; stdlib only; entfernt/abschwächt keine Metrik — dürfte `craft_variety`/`session_depth` leicht stützen (mehr gültige Kombinationen pro Materialsortiment).

## Akzeptanzkriterien
- Blueprint mit 2 identischen Slot-Anforderungen: craftbar aus einem einzigen Stack (`quantity>=2`, z.B. Speer aus 2× Stick), sowie aus zwei distinkten Materialien wie bisher.
- Verbrauch korrekt: 2-Slot-Craft aus Stack `quantity=3` hinterlässt `quantity=1`. Kein doppeltes Entfernen, kein ValueError, kein Müll-Item.
- `quantity>=N` nötig für N-fache Nutzung desselben Stacks; unzureichende Menge → verständliches Feedback statt Fehlstart.
- Bestehende Pfade (distinkte Materialien) unverändert grün.
- `python -m pytest` grün (neue Tests: 2×gleicher Stack craftbar, Verbrauch, unzureichende Menge, distinkte Kontrolle).
- `session_depth`/`craft_variety` in der nächsten Scorecard **nicht** gefallen.

## Erwartete Metrik-Wirkung
- `craft_variety`/`session_depth`: leicht **stützend** (mehr legale Craft-Kombinationen pro Materialsortiment → weniger tote Enden). Kein Zielband versprochen — primär ein Hand-feeling-Fix.