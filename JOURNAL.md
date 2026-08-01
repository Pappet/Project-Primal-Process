# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Review).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-08-01 — [Meta] Review-Cap auf 6 Tasks korrigiert — danach als Zahl entfernt

**Kontext:** Sprint-Cap „max 4 Tasks" stammte aus dem alten Dev-Schedule (Mo/Mi/Fr = 3 Sessions + 1 Puffer). Dev läuft jetzt Mo–Sa = 6 Sessions. Weiter verschärft: Dev bündelt jetzt Minifixes → konsumiert mehrere Tasks pro Session.

**Finale Struktur (nach Iteration mit Peter):**
- **Kein fixes Tasks-Cap mehr.** Review füllt den Sprint mit allen offenen 🔴 Bugs + top-priorisierten Refactors/Features, so viele wie sinnvoll und klar definiert — Kriterium ist Qualität, nicht eine Zahl. Nicht abgearbeitete Tasks rollen in die Folgewoche.
- **Dev bündelt Minifixes** (mehrere kleine Tasks/Session), Refactors/Features einzeln. Kein 1-Task-pro-Session-Zwang mehr.
- **Review übernimmt offene Tasks** aus der bisherigen Sprint-Sektion in die neue KW (kein Verlust beim KW-Wechsel).
- Review-Prompt liest den `qa/`-Ordner als Pflicht-Input. Delivery auf `discord:#general` (konsistent zu Research/Dev/QA).
- „Geschätzt"-Zeilen aus dem Task-Format entfernt — der Review muss nicht mehr schätzen.

**Triage-Testlauf (`187199c`):** Flow funktioniert — QA-Report → 5 Bug-Tasks, PLAN.md aktualisiert, committed + gepusht.

---

## 2026-08-01 — [Review] Weekly Triage + Sprint-Planung (KW 32)

**Kontext:** KW 31 lief zu grossen Teilen leer (3× "Sprint leer") — Dev wartete auf Triage. Der QA-Playtest #1 (heute) liefert endlich konkrete Arbeit: 5 🔴 Bugs, Spiel faktisch unspielbar.

### Erreicht (KW 31)
- **TASK-M03 (JSON-Loader Refactor)** abgeschlossen — 83/83 Tests grün, keine hartkodierten Dicts mehr in items/blueprints/locations
- **Research:** 4/6 Referenzspiele analysiert (URW, CDDA, Ancestors, Neo Scavenger)
- **QA-Playtest #1:** Smoke 30/30, Unit 83/83 — Engine stabil, aber Spiel als Ganzes unspielbar (5 🔴 Bugs)

### Blockiert
- Nichts extern. Der Stau war prozessual: keine Sprint-Tasks → Dev-Leerlauf. Jetzt behoben durch QA-Bugs.
- **M0.3 bleibt offen:** `processes.py` noch hartkodiert (Tech Debt), daher Milestone-Marker `[~]` statt `[x]`.

### Prioritäten KW 32
1. **Alle 5 🔴 Bugs** (Crafting strukturell unspielbar) — Vorrang, je eigener Task
2. Restliche Tech-Debt-Refactors (M0.3 abschliessen: processes.py, _create_tool)
3. QA-Balance (Fehlschlag-Feedback, Energie-Regeneration)
4. Research: Don't Starve + Vintage Story (geplant Di 04.08) + 5 neue Kandidaten in M0.2

### Triage (BACKLOG)
- **🔴 Bugs:** 5/5 → Sprint KW 32 (je eigener Task, nicht gebündelt)
- **🟡 Ideas:** tag-Substitution, Material-Quelle→Eigenschaften, Multi-Faktor-Crafting, Death-as-Legacy → nächste Woche (M0.4/M1.x); Rest (Condition-Web, Body-Part, Skills, Discovery, Biom, Starting Scenarios) → später (Phase 2/3)
- **🔵 Tech Debt:** `create_dynamic_item`-Fix in TASK-M03 erledigt; `processes.py` + `_create_tool` → Sprint KW 32
- **⚪ Research Leads:** 5 neue Survival-/Primitive-Tech-Spiele ergänzt (M0.2-Pipeline)

### Entscheidungen
- M0.3 auf `[~]` gesetzt (in Arbeit) — TASK-M03 fertig, processes-Loader steht noch aus.
- M0.2 erweitert: von 6 auf 11 Spiele, da nur noch 2 offen waren.

---

## 2026-07-30 — [Research] Ancestors + Neo Scavenger

### Ancestors: The Humankind Odyssey — Erkenntnisse
1. **Neuronales Entdeckungssystem:** Fähigkeiten durch Handlungen entdeckt und „verstärkt" — kein Tech-Tree-Kauf. Verstärkte Neuronen werden durch Fortpflanzung vererbt. Das ist das Vorbild für PPPs Blueprint-Discovery.
2. **Fear/Dopamin-Pacing:** Unbekannte Biome lösen Angst aus, erfolgreiche Aktionen bauen Dopamin auf. Organisches Gating ohne künstliche Barrieren. Für PPP: Biom-Vertrautheit als Erkundungsmechanik.
3. **Sensorische Discovery-UI:** Keine Minimap, kein Kompass. Sinne (Hören, Riechen, Intelligenz-Scan) ersetzen das HUD. Objekte müssen identifiziert werden, bevor sie nutzbar sind.
4. **Generationen-Lineage:** Tod = Clan-Mitglied-Wechsel, nicht Game Over. Entdecktes Wissen überlebt den Tod. Für PPP: Death-as-Legacy statt Death-as-Failure.
5. **Evolutionäre Physiologie:** Biologische Evolution ändert Mechaniken (Bipedalismus → Hände frei → tragen). Physiologie als Mechanik-Gate.

### Neo Scavenger — Erkenntnisse
1. **Substitutions-Crafting:** Rezepte definieren Kategorien (SHARP, CONTAINER), nicht Item-IDs. Beweist dass PPPs Tag-System im Survival-Genre funktioniert. Unterschiedliche Materialien = unterschiedliche Qualität.
2. **Condition-Web:** Multi-Condition-Metabolismus (Hunger, Durst, Fatigue, Hypothermie, Krankheit, Schmerz) mit Kaskaden. Tod fast nie durch eine Condition — es ist die Kaskade. Vorlage für M2.4.
3. **Permadeath + Spieler-Progression:** Kein XP, kein Leveling. Fortschritt = Spieler-Wissen. Philosophischer Beweis für PPPs Discovery-Ansatz.
4. **Abilities & Flaws:** Permanente Start-Traits definieren den Run. Für PPP: Starting Scenarios als Replayability-Multiplikator.
5. **Detailliertes Wundensystem:** Wunden mit Lokalisation, Typ, Infektionsstatus. Zeitdruck durch Infektions-Timer. Erweitert URWs Body-Part-System um systemische Konsequenzen.

### Für PPP adaptierbar (Top 5, spielübergreifend)
1. **Tag-basierte Item-Substitution** (NS) → Blueprints mit Tag-Slots statt Item-IDs — das Kernversprechen von PPP, durch NS validiert
2. **Neuronales Discovery-System** (Anc) → Blueprints durch wiederholte Experimente entdecken, nicht kaufen/finden
3. **Condition-Web** (NS) → HP/Energy ersetzen durch vernetzte Conditions mit Kaskaden-Interaktionen
4. **Angst/Dopamin-Pacing** (Anc) → Biom-Vertrautheit als natürliche Erkundungsbremse
5. **Permadeath-als-Legacy** (NS+Anc) → Tod = Wissens-Reset? Nein: entdeckte Blueprints überleben

### Backlog-Einträge
- Siehe BACKLOG.md (Ideas)

### Änderungen
- `research/ancestors.md` — 5 Mechaniken + Top-3-Adaptionen
- `research/neo-scavenger.md` — 5 Mechaniken + Top-3-Adaptionen
- `research/INDEX.md` — Querverweise für beide Spiele aktualisiert (4/6 analysiert)

### Nächster Schritt
- **Di 04.08. 10:00** — Research: Don't Starve + Vintage Story (letzte Research-Session von Phase 0)

---

## 2026-08-01 — [QA] Weekly Playtest #1

**Status:** Erster QA-Durchlauf. 83/83 Unit Tests grün, Smoke-Test 30/30 bestanden. Engine selbst stabil — keine Crashes, alle Edge Cases sauber behandelt.

**Kritisches Ergebnis: Spiel ist faktisch unspielbar.** Kein Blueprint im normalen Spielverlauf craftbar. Fünf 🔴 Bugs gefunden:

1. **Kein FIBER-Item droppbar:** `plant_fiber` und `reeds` in items.json definiert, aber in keiner Location. Beide Blueprints brauchen FIBER — strukturell unmöglich.
2. **`pebble`-Template fehlt:** `mountain_peak`-Node referenziert `"pebble"`, nicht in items.json → Spieler sammelt nutzlose "Unbekannt"-Items.
3. **Perception-Gates blocken alles:** Start=1.0, flint_shard braucht 1.5, berries 2.0, mushroom 2.0. Kein Weg perception zu erhöhen.
4. **Condition=0-Exploit:** Kaputte Items craften → Ergebnis hat condition=1.0. Kein Condition-Check in `execute_experiment`.
5. **Nachtstart:** tick_counter=0 → hour=0 → night_mod=-10. Effektive Temperatur 5°C. Hypothermie fast sofort.

**Edge Cases:** 12/12 getestet, alle sauber behandelt (keine Crashes). Nur condition=0 ist ein Bug.

**Balance:** Energie-Drain aggressiv (10/gather, 22.5/travel, 30/craft). Gather fühlt sich grindig an (nur 1 Item-Typ droppbar). Feedback `"Nichts passiert."` absolut uninformatisch.

**Änderungen:**
- `qa/_smoke_test.py` — 30-Check Engine-Smoke-Test
- `qa/_scenario_test.py` — New-Player-Szenario + 10 Edge Cases
- `qa/2026-08-01.md` — QA-Report
- `BACKLOG.md` — 5 🔴 Bugs
- `JOURNAL.md` — dieser Eintrag

---

## 2026-08-01 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) weiterhin leer. TASK-M03 abgeschlossen. Dritter Leerlauf in Folge.

**Aktion:** Keine Implementierung. Review morgen (So 02.08. 18:00) muss zwingend neue Tasks liefern — nächste Dev-Session Mo 04.08.

**Notiz:** M0.4 (Save/Load-System), M1.1 (Tag-Hierarchien), und M1.2 (Item-Content ×5) sind nächste priorisierbare Kandidaten. Phase 0 hängt ohne neue Tasks.

---

## 2026-07-31 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) weiterhin leer. TASK-M03 abgeschlossen, keine neuen Tasks hinzugefügt. Zweiter Leerlauf in Folge.

**Aktion:** Keine Implementierung. Warte auf Review (So 02.08. 18:00).

**Notiz:** M0.4 (Save/Load-System) und M1.1 (Tag-Hierarchien) stehen als nächste Kandidaten bereit. Review sollte zügig neue Sprint-Tasks priorisieren, sonst läuft Dev bis KW 33 leer.

---

## 2026-07-30 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) vollständig abgearbeitet. TASK-M03 ist `[x]`, keine weiteren offenen Tasks.

**Aktion:** Keine Implementierung. Warte auf Review (So 02.08. 18:00) für Triage und nächste Sprint-Planung.

**Offene Milestones in PLAN.md:**
- M0.3 (Datenmodell refactorn) — `[ ]` in Milestones, aber TASK-M03 hat die Akzeptanzkriterien bereits erfüllt. Milestone-Marker vermutlich veraltet.
- M0.4 (Save/Load-System) — `[ ]`, nächster Kandidat für Sprint-Aufnahme.

---

## 2026-07-29 — [Dev] TASK-M03: JSON-Loader Refactor (Session 1/3)

### Erreicht
- **JSON-Daten erstellt:** `data/items.json`, `data/blueprints.json`, `data/locations.json` — alle 1:1 aus den alten hartkodierten Dicts extrahiert
- **Loader-Modul:** `data/loader.py` mit pydantic-Validierung (ItemTemplate, BlueprintData, LocationData, ResourceNodeData)
- **data/items.py refactored:** `TEMPLATE_DB` jetzt aus `load_items()` statt hartkodiert — `create_item()` nutzt pydantic-Model-Attributzugriff
- **data/blueprints.py refactored:** `get_all_blueprints()` aus `load_blueprints()`
- **data/locations.py refactored:** `get_all_locations()` aus `load_locations()` — ResourceNode/LocationDef-Dataclasses bleiben als API erhalten
- **Bugfix:** `engine/crafting.py:create_dynamic_item` — hardcoded `components["head"]`/`components["handle"]` entfernt. Dynamische Suche nach sharpness und Name-Building
- **Neue Tests:** `tests/test_loader.py` — 18 Tests (Load, Validation, Roundtrip): fehlende Datei, invalides JSON, fehlende Pflichtfelder, falsche Typen

### Ergebnis
- **83/83 Tests grün** (65 bestehend + 18 neu), `python -m pytest` in 0.39s
- Alle Items, Blueprints, Locations verhalten sich identisch zur alten Version
- Keine hartkodierten Dicts mehr in `data/items.py`, `data/blueprints.py`, `data/locations.py`

### Notizen
- `data/processes.py` hat noch hartkodierte ProcessDefs — nicht im Task-Scope, aber konsistent wäre ein `processes.json` → BACKLOG
- `engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — hat Fallback aber inkonsistent mit fix in crafting.py → BACKLOG
- pydantic 2.13.4 verfügbar, Validierung funktioniert sauber

### Nächster Schritt
- TASK-M03 ist vollständig (alle Akzeptanzkriterien erfüllt). Review entscheidet ob Session 2/3 nötig.

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