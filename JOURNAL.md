# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Review).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-07-28 — [Research] UnReal World + Cataclysm: Dark Days Ahead

### UnReal World — Erkenntnisse
1. **Body-Part-Schaden:** Jeder Körperteil eigener Zustand (Frostbite, Bruch, Wunde). Lokalisierte Konsequenzen statt globaler HP. Direkt relevant für PPP M2.4.
2. **Material-Herkunft:** Fell-Qualität hängt vom Tier ab (Bär > Fuchs). Emergente Vielfalt durch Quell-Tags — kein Template-Overhead.
3. **Skill → Qualität:** 28 Skills, verbessern sich durch Nutzung (auch bei Fehlschlag!), modulieren Output-Qualität. Hardcap 95%, Softcap 5%. Learning from failure als Kernmechanik.
4. **Jahreszeiten-Welt:** Klima bestimmt Ressourcen-Verfügbarkeit, Prozesse (Trocknen nur bei >5°C), Tierverhalten. Winter-Survival fundamental anders als Sommer.
5. **Kein Geld:** Reine Tausch-Ökonomie. Fortschritt durch Selbstversorgung, nicht durch Kauf. Passt zu PPPs Discovery-Philosophie.

### CDDA — Erkenntnisse
1. **Nested Requirements:** Crafting = Rohstoffe + Tools + Skill + Proficiencies + Rezeptwissen + Umwelt (Licht/Werkbank/Gesundheit). Das Multi-Faktor-Modell für PPP-Blueprints.
2. **Proficiency-System:** `prof_carving`, `prof_welding` etc. — Sub-Skills unter generellen Skills. Lernen durch Wiederholung, reduzieren Fehlschlag-Rate. Bindeglied zwischen "kann generell" und "kann genau das".
3. **Known-Blueprints:** Rezepte sind nicht automatisch bekannt — müssen durch Bücher/Experimente entdeckt werden. Für PPP: `known_blueprints: set` auf Player.
4. **Komponenten-Fahrzeuge:** Fahrzeuge aus Einzelteilen (Frame, Rad, Motor) statt als Ganzes. Gleiches Prinzip für Gebäude. Relevant für M2.2 Shelter-System.
5. **Farming mit Pflanzenphysiologie:** Wachstumsrate × Temperatur × Dünger × Skill = Yield. Design-Vorlage für Phase 4.

### Für PPP adaptierbar (Top 5)
1. **Body-Part-System** (URW) → M2.4 Gesundheit, ggf. schon in M1.1 Tags vorbereiten
2. **Material-Quelle → Eigenschaften** (URW) → Tags wie `BEAR_FUR`, `OAK_WOOD` als Qualitäts-Multiplikatoren
3. **Multi-Faktor-Crafting** (CDDA) → M1.3 Blueprint-Conditions (Licht, Werkbank, Körperzustand)
4. **Proficiencies** (CDDA) → Sub-Skills, die Fehlschlag-Rate bei spezifischen Aktionen modulieren
5. **Known-Blueprints** (CDDA) → Discovery-System: nur craften, was vorher entdeckt wurde

### Backlog-Einträge
- Siehe BACKLOG.md (Research Leads + Ideas)

---

### Änderungen
- `tests/`-Ordner mit `conftest.py`, `__init__.py` angelegt
- `test_components.py` — 20 Tests: Item, Inventory, ToolBlueprint, Player
- `test_crafting.py` — 11 Tests: Blueprint, try_combine (Permutation, Multi-Tag, Mismatch), create_dynamic_item
- `test_data.py` — 13 Tests: create_item für alle 8 Templates, Edge Cases, Tag-Isolation
- `test_engine.py` — 21 Tests: execute_experiment (Axt/Messer), Eat, Travel, Weather, Thermodynamik
- 65/65 Tests grün, `python -m pytest` läuft in 0.31s

### Notizen
- `create_dynamic_item` in `crafting.py` ist hardcoded auf `components["head"]` — crasht bei generischen Blueprints ohne "head"-Slot. Tests dokumentieren das Verhalten, Refactor in M0.3.
- `_update_weather` triggert auch bei tick_counter=0 (0 % 12 == 0), also initialer Wetter-Random schon beim Start.
- `_get_ambient_temp` berechnet bei tick_counter=0 Nacht (hour=0 < 6) → night_mod=-10, daher 5°C statt 15°C.

### Nächster Schritt
- M0.3 — Datenmodell refactorn (JSON-Loader). Jetzt mit Test-Safety-Net.

---

## 2026-07-26 — [Setup] Projektübernahme & Initialisierung

- Repo von GitHub geklont, analysiert (~400 Zeilen, 8 Items, 2 Blueprints, 3 Orte)
- Stärke: Tag-basiertes Emergent Crafting als Kernmechanik
- Schwächen: kein Save/Load, Content-arm, keine Gefahren, keine Persistenz
- Vision festgelegt: Primitive Technology Discovery Game (Steinzeit → Eisenzeit)
- 4-Phasen-Plan über ~12 Wochen erstellt
- 3 Cron-Jobs eingerichtet: Research (Di+Do), Dev (Mo+Mi+Fr), Review (So)
- Repo: ~/projects/primal-process/, Remote: Pappet/Project-Primal-Process

## 2026-07-26 — [Review] Weekly #1

### Erreicht
- Repo geklont, analysiert, 4-Phasen-Plan erstellt
- Projekt-Dokumentation: PLAN.md, ANALYSIS.md, JOURNAL.md, BACKLOG.md
- Cron-Job-Struktur definiert: 3 Jobs (Research Di+Do, Dev Mo+Mi+Fr, Review So)
- Claude-Review-Feedback eingearbeitet (Session-State, Tests M0.2b, Review-Guardrails)
- M0.1 abgeschlossen ✓

### Backlog-Triage
- Backlog ist leer — Projekt ist brandneu, keine Einträge
- Einträge bereinigt: 0 archived, 0 deleted

### Blockiert/Probleme
- Nichts blockiert. Projektstart verlief sauber.

### Entscheidungen
- M0.2b (pytest) vor M0.3 (Datenmodell-Refactor) priorisiert — Claude hatte recht, Refactor ohne Tests = gefährlich
- Research: 2 Spiele pro Session statt 3 — Task-Granularität beachten
- research/INDEX.md als leeres Template angelegt, erste Session Di 28.07.

### Nächste Woche
- **Mo 27.07.** Dev: M0.2b pytest-Grundgerüst + Smoke-Tests
- **Di 28.07.** Research: UnReal World + CDDA analysieren
- **Mi 29.07.** Dev: Nächster Task (M0.2b fortsetzen oder M0.3 beginnen)
- **Do 30.07.** Research: Ancestors + Neo Scavenger
- **Fr 31.07.** Dev: Nächster Task

### Notizen
- Phase 0 läuft bis KW 33 (Mitte August). Genug Puffer für 6 Spiele + Test-Setup + Refactor + Save/Load.
- Keine ❓ an Peter nötig — alles im Plan.