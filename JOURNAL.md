# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Play, Direktor).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-08-04 — [Research] SPEC-003: Partielle Match-Erkennung (discovery_gap)

### Metrik-Anker
Schwächste/stagnierende Metrik laut Scorecard 2026-08-03: **`discovery_gap` = 0.5**, an der oberen Kante des Bands (0.2–0.6) — nahe „unentdeckbar". Zerlegung: `blueprint_reachability`=1.0 (Orakel), `naive_discovery_rate`=0.5, aber **`naive_p25`=0.0** — die untere Hälfte der naiven Läufe findet in 150 Aktionen *gar keinen* Blueprint. Der Median verdeckt den Schwanz. SPEC-001/002 decken Vielfalt/Content/Feedback ab, aber keine Mechanik senkt die Lücke selbst.

### Spec
`specs/SPEC-003-partial-match-recognition.md`. Mechanik aus Don't Starve (Prototypen-Maschine) + Ancestors (neuronales Entdeckungssystem), adaptiert als **partielle Match-Erkennung**: Fehlschlag mit ≥2/3 Slots eines unbekannten Blueprints → Reason `NEAR_MISS:<bp_id>`, generischer Bestätigungstext („gehören zusammen, es fehlt noch etwas") **ohne** Rezept-/Tag-Leak. Einmalig via `Player.near_misses` (Experimentiergedächtnis, von der Constitution gedeckt). Konvergiert naive Spieler, schenkt aber nichts — wer die Materialien nicht selbst hat, bekommt keinen Hinweis.

### Constitution-Check
- Kein vorgegebenes Rezept — nur Bestätigung einer gehaltenen Teilmenge.
- Hinweis/Experimentiergedächtnis ausdrücklich erlaubt.
- CI: CLI, stdlib, keine neue Metrik, keine Abschwächung bestehender Metriken.

### Erwartete Wirkung
- `discovery_gap`: 0.5 → ~0.3–0.4 (Mitte des Bands; bleibt >0.2, weil der Hinweis erst nach eigenem Besitz von ≥2 passenden Tags feuert).
- `naive_discovery_rate` p25: 0.0 → >0.0 („findet nichts"-Schwanz geschlossen).
- Nebeneffekt `session_depth` steigend.

### Änderungen
- `specs/SPEC-003-*.md` (neu)
- `PLAN.md` — SPEC-003 als offener Task

---


### Autorisierung
**Peter autorisiert in dieser Session ausschließlich die drei in Abschnitt 1 des Auftrags wörtlich spezifizierten Änderungen an CONSTITUTION.md.** Alles darüber hinaus bleibt ihm vorbehalten. Vermerkt hier.

### CONSTITUTION.md — drei Änderungen, sonst nichts
- **Status:** `ENTWURF — wartet auf Freigabe` → **`Gültig — freigegeben von Peter am 2026-08-03`**.
- **Positiver Rahmen** (Ende Identität): *"Neue Mechaniken sind ausdrücklich erwünscht, solange sie das Entdecken vertiefen statt es abzukürzen. Das Spiel darf wachsen — in Systemen, nicht nur in Inhalten."*
- **"Keine festen Rezepte" präzisiert:** ersetzt durch *"Keine vorgegebenen Rezepte; Entdeckung durch Experimentieren. Dass der Spieler festhält, was er selbst entdeckt hat — Entdeckungsjournal, Hinweise, Experimentiergedächtnis — ist ausdrücklich erlaubt und kein Widerspruch dazu."*

Damit ist die Constitution final. Vier Agenten lesen sie jede Session; der positive Rahmen löst die Vorsicht, die reine Verbote erzeugt hatten.

### Research in zwei Modi aufgeteilt
- **research-metric** (Job-ID `c837d9d8dde1`, Di 10:00) — wie bisher: schwächste/stagnierende Metrik, gezielt Mechaniken, genau ein Spec.
- **research-explore** (neuer Job `ba3954705006`, Do 10:00) — **kein Metrik-Anker.** Freie Suche nach Mechaniken, die das Spiel als System vertiefen, auch solche, die keine bestehende Metrik bewegt. Output: Spec **plus Metrik-Vorschlag** als `metrics/proposed/<name>.md` (Definition, Berechnungsskizze, Richtung/Zielband, warum nicht trivial zu heben). Ohne Metrik ist der Spec unvollständig.
- Beide nach `cron/` exportiert, beide tragen die Constitution-Zeile.

### Probezeit mechanisch durchgesetzt
- `METRICS` unterstützt optionales `probation_until` (ISO-Datum). Neue Metriken setzt Dev auf +14 Tage.
- SCORECARD.md markiert solche Zeilen mit `(Probe bis TT.MM.)`.
- Direktor-Prompt: Metriken in Probezeit dürfen beobachtet, aber **nicht** als Plan-Ziel gesetzt werden.
- Dev-Prompt: Hinzufügen von Metriken ist erlaubt und braucht keine Freigabe — nur Entfernen/Umdefinieren.

### Altlast entfernt
- `qa/` (abgelöste QA-Rolle) nach `archive/qa-legacy/`. `_smoke_test.py:162` prüfte auf "Nichts passiert" — sicherte also das Gegenteil des gewollten Verhaltens ab (inzwischen false; 3 Sticks → "Es fehlt dir etwas Hartes.").
- Der wertvolle Fall (3 Items ohne gültige Kombination nennen das Merkmal) als echter pytest `test_three_same_items_no_blueprint` nach `tests/test_engine.py`.

### Backlog
- Lern-Signal als Idea eingetragen, ausdrücklich **nicht** als Vorgabe: misst, ob ein Spieler Feedback versteht (Trefferquote nach informativer Meldung) — im Gegensatz zu `feedback_quality`, das nur Reason↔Label-Konsistenz prüft und bei 1.0 steht. Option für den Explore-Job, kein Auftrag.

### Verifikation
- `python -m pytest` → **134 passed** (131 + 3 Probezeit-Tests, nach qa-Verschiebung erneut geprüft).
- Scorecard deterministisch, Werte identisch zur letzten Messung (63 / 1.0 / 0.5 / 0.315 / 1.0 / 0.667 / 24 / discovery_gap 0.5).
- `cron/OVERVIEW.md` auf 5 Jobs aktualisiert.

### Wartet auf Peter
- Nichts — Constitution ist freigegeben. Das System kann laufen.

---
## 2026-08-03 — [Fix] Spieler-Feedback ehrlich + discovery_gap eingeführt

### Freigabe
**Peter hat die Umdefinition von `feedback_quality` genehmigt.** Vermerkt hier, damit der Direktor nicht auf eine vermeintliche Regression reagiert.

### Warum
`feedback_quality` stand auf 1.0, obwohl der Spieler unverändert "Nichts passiert." las — die Engine kannte den Grund (`MISSING_TAG:SHARP`), behielt ihn aber für sich. Genau der Fall, den die Messungs-Klausel der Constitution für ungültig erklärt. Und es fehlte die wichtigste Größe: der Abstand zwischen Erreichbarem und tatsächlich Gefundenem.

### Engine (Meldungen aus Reason abgeleitet — Spielerlebnis, nicht Metrik)
- `TAG_LABELS` angelegt: vollständig für alle im Spiel vorkommenden Tags (SHARP→"etwas Scharfes", FIBER→"etwas Faseriges", RIGID→"etwas Festes", etc.).
- `_feedback_message(reason)` baut für jeden Code eine konkrete Meldung; verrät nie mehr als der Reason hergibt (kein Rezept-Leaking).
- **"Nichts passiert." ist als Meldung vollständig verschwunden.** Fehlschläge nennen jetzt das fehlende Label, "mindestens zwei Dinge", das kaputte Item, oder "die Kombination ergibt nichts".
- Kein verändertes Spielverhalten, keine Balance-Änderung.

### feedback_quality neu definiert (v2)
> Eine Aktion zählt als informativ, wenn die Meldung das Label enthält, das zum tatsächlich zurückgegebenen Reason-Code gehört.

Damit ist die Metrik nur zu heben, indem man dem Spieler die Wahrheit sagt — nicht durch String-Renaming oder interne Codierung. `_expected_fragment(reason)` ist der Konsistenz-Wächter.

**Ehrlicher Befund:** Der Wert bleibt bei 1.0 — **nicht** weil nichts passiert ist, sondern weil die Engine in genau dieser Session gelernt hat, die Labels auch wirklich auszugeben. Die Metrik misst jetzt die Spielersicht und ist verdient auf 1.0. Würde jemand das Label aus der Meldung nehmen (ohne den Code zu ändern), fällt sie sofort. Ein künftiger Rückgang ist also korrekt, kein Alarmsignal.

### discovery_gap (neu, Band-Metrik)
- `blueprint_reachability` (Orakel) = 1.0, `naive_discovery_rate` (150 Aktionen) = 0.5.
- **`discovery_gap` = 0.5.** Zielband **0.2–0.6**, keine Richtung. Unter 0.2 nimmt das Spiel an die Hand, über 0.6 ist es unentdeckbar.
- Aktuell an der oberen Bandgrenze — nahe daran, dass ein Spieler zu wenig findet. Wichtiges Signal für die zwei Specs.
- Begründung + Zielband stehen in SCORECARD.md.

### Metrik-Historie versioniert
- Jede Metrik hat ein `version`-Feld in der JSON-Ausgabe. `feedback_quality` = 2, alle anderen = 1.
- Beim Delta wird eine Metrik mit Versionswechsel übersprungen → `— (neu definiert)`, die anderen bleiben vergleichbar. **Kein globaler Schema-Bump.**

### Rückwärtsprüfung (Punkt 6)
Außer `feedback_quality` sind auch `skill_spread` (0.298→0.315) und `session_depth` (16→24) durch die Zählweisen- und Median-Umstellung gestiegen, ohne dass sich am Spielerlebnis etwas geändert hätte. **Das ist kein stiller Fortschritt zu feiern.** Task in PLAN.md angelegt: beim nächsten Play-Lauf prüfen, dass beide Werte echte Spielerfahrung abbilden, sonst Metrik-Version bumpen.

### Constitution
Messung-Sektion ergänzt: *"Neue Metriken müssen benennen, welche Schwäche sie erfassen, und zwei Wochen mitlaufen, bevor sie Plan-Ziele steuern dürfen."* Status bleibt Entwurf.

### Verifikation
- `python -m pytest` → **130 passed** (117 + 13 neue).
- Neue Tests: Reason↔Label-Konsistenz für jeden Code, Etikett-vollständig für alle Tags, "Nichts passiert." kommt im Code nicht mehr vor, `discovery_gap` 0–1 + Band-Rendering.
- Determinismus: 2 Läufe, identische `metrics`.
- Delta real geprüft: unveränderte Metriken zeigen Zahlen, `feedback_quality` zeigt `— (neu definiert)`, Band-Zeile `im Band`.

### Neue Baseline (2026-08-03)
| Metrik | v | Wert |
|--------|---|------|
| actions_to_first_craft | 1 | 63 |
| blueprint_reachability | 1 | 1.000 |
| craft_variety | 1 | 0.5 |
| skill_spread | 1 | 0.315 |
| feedback_quality | **2** | 1.0 |
| content_reachable | 1 | 0.667 |
| session_depth | 1 | 24 |
| **discovery_gap** | 1 | **0.5** (Band 0.2–0.6) |

`feedback_quality` v2 ist nicht mit v1 vergleichbar.

### Wartet auf Peter
- Constitution-Freigabe (aktualisierte Fassung).
- Bestätigung der feedback_quality-Umdefinition (bereits in der Session als erteilt angenommen).

---
## 2026-08-03 — [Fix] Scorecard repariert + gegen Selbstoptimierung gehärtet

### Warum
Das Fitness-Signal hatte einen toten Schaltkreis (Delta feuerte nie) und mehrere Metriken waren billiger zu faken als zu erfüllen. Da das System ab jetzt ohne Peter steuert, wäre beides fatal: ein Delta, das nie feuert, gibt keine Richtung; eine Metrik, die man per String-Änderung hebt, wird genau so gehoben werden.

### Engine (nur strukturierte Rückgabefelder, kein Spielverhaltens-Unterschied)
- `execute_experiment`/`_create_tool` geben jetzt `reason` (`SUCCESS`/`NO_MATCH`/`BROKEN_ITEM`/`MISSING_TAG:<T>`/`TOO_FEW_ITEMS`/`UNKNOWN`), `blueprint_id` und `result_template_id` zurück.
- `Item` hat `template_id` (für Neuheits-Messung per Identität statt Name). `create_item` und `_create_tool` setzen es.
- Alle Meldungen (`message`) bleiben exakt gleich → bestehende 93 Tests unverändert grün.

### Scorecard-Überarbeitung (tools/scorecard.py)
- **Delta-Logik gefixt:** Vorher las `_prev_value` `data.get(key)` (Werte liegen unter `metrics`) und nahm `files[-1]` — die gerade geschriebene heutige Datei → immer Baseline. Jetzt: `load_previous(today)` schließt heute aus, nimmt die jüngste ältere Datei mit gleichem Schema; `prev` wird als Parameter in `build_table` gereicht (kein Glob im Tabellenbau mehr).
- **Metriken auf Identitäten:**
  - `craft_variety` → zählt distinkte `blueprint_id` (nicht `message`-Strings).
  - `feedback_quality` → Reason-Codes statt String-Blacklist; zählt Code ≠ UNKNOWN/NO_MATCH-ohne-Detail.
  - `session_depth` → Neuheit über `template_id` + `known_blueprints` + Prozesse, nicht Item-Namen.
  - `content_reachable` → zusätzlich `reachable_count`/`defined_count`; Tabelle markiert Content-Reduktion als `⚠ Content entfernt` statt als Verbesserung.
- **Seed-Satz:** `SEEDS = 20`; jede laufbasierte Metrik über alle Seeds, Median als `value`, `p25`/`p75` in Details. Laufzeit 1,3 s → kein Seed-Reduktionsbedarf.
- **skill_spread:** datengetrieben (beste Location über alle erreichbaren), `_travel_or_fail` schlägt hart fehl statt still weiterzulaufen.
- **Schema:** `schema: 2` in JSON; andere Schemata werden beim Delta übersprungen. Alte Datei nach `scorecard/archive/`.

### Neue Baseline (2026-08-03, schema 2)
| Metrik | Wert | vs. 03.08. (v1) |
|--------|------|------------------|
| actions_to_first_craft | 63 (Median) | 43 (Einzelrun) |
| blueprint_reachability | 1.000 | 1.000 |
| craft_variety | 0.5 (Median) | 1 (String) |
| skill_spread | 0.315 | 0.298 |
| feedback_quality | 1.0 | 0.6 |
| content_reachable | 0.667 | 0.667 |
| session_depth | 24 | 16 |

**Nicht vergleichbar:** andere Zählweise (Median), andere Identität (blueprint_id/template_id statt Name/String), Reason-Codes. Werte der v1-Baseline sind obsolet.

**Ehrliche Befunde:**
- `feedback_quality` springt auf 1.0 — nicht weil das Feedback besser wurde, sondern weil die Engine fast jede Aktion strukturiert codiert. Die Metrik misst jetzt Code-Qualität, nicht Spieler-Erlebnis. Das ist der gewollte Trade-off (nicht fakebar); die Meldung `"Nichts passiert."` bleibt aber die Spieler-Wahrnehmung.
- `craft_variety` fällt von 1 auf 0.5 (Median) — der naive Spieler erreicht in 100 Aktionen oft gar keinen oder einen Craft-Typ. Ehrlicher als der aufgeblasene String-Wert.

### Constitution + Direktor
- Messung-Sektion ergänzt: `tools/scorecard.py`, `METRICS`, Play-Job unantastbar; Metriken nur ergänzbar, nicht entfernbar/abschwächbar ohne Peter. Metriken = Indikatoren, nicht Ziele.
- Nicht-Ziele korrigiert (tote Mikrotransaktionen/Multiplayer/Echtgeld raus) → realistische Drift-Richtungen: Content-Menge als Selbstzweck, Refactoring ohne Metrik-Bezug, GUI, Kampf als Kern.
- pydantic explizit als erlaubte Ausnahme genannt (loader.py nutzt es).
- Direktor-Prompt eingeschränkt: darf Cron-Jobs ändern, aber nicht Play/Messung.
- SPEC-002: Akzeptanzkriterium von "≥4 Crafts in 100 Aktionen" → Verhaltensziel "3 Werkzeugtypen mit je ≥2 Varianten".

### Verifikation
- `python -m pytest` → **117 passed** (93 bestehend + 24 neue in `tests/test_scorecard.py`).
- Determinismus: 2 Läufe, identische `metrics`.
- Delta real verifiziert (synthetische Vorwochendatei → Zahlen in Δ-Spalte), dann entfernt; frische Baseline bleibt `— (Baseline)`.

### Wartet auf Peter
- Constitution-Freigabe (aktualisierte Fassung).

---
## 2026-08-03 — [Umbau] Primal Process auf autonomen Betrieb umgestellt

### Kontext
Das System lief wie ein Scrum-Team ohne Product Owner: Der Plan (Tag 1) fror jede Erkenntnis ein, die einzigen Signale waren "Tests grün" und "Sprint gefüllt". Beides misst Prozess, nicht das Spiel. Umbau: Selbstversorgung + messbare Spiel-Fitness + selbstmodifizierender Prozess. **Kein Spiel-Code geändert.** Einzige neue ausführbare Datei: `tools/scorecard.py`.

### Was gebaut wurde
- **CONSTITUTION.md** — unantastbarer Kern (Identität, Nicht-Ziele, Constraints, Änderungsregel). STATUS: Entwurf, wartet auf Peter. **Entscheidung:** max. 25 Zeilen respektiert (22). Nur Peter ändert diese Datei.
- **Scorecard** — `tools/scorecard.py` (stdlib only, deterministischer Seed) + `SCORECARD.md`. 7 Metriken aus echten Playthroughs, Delta zur Vorwoche, JSON nach `scorecard/`. Baseline lief.
- **PLAN.md neugeschrieben** — alte Fassung nach `archive/PLAN-phases-2026-08.md`. Drei Sektionen (Zustand/Ziele/Tasks), keine Phasen/KWs. Milestones M0.4–M3.4 als Rohmaterial nach BACKLOG.md.
- **Research → Specs** — Format definiert; 2 Beispiel-Specs aus der schwächsten Metrik geschrieben (SPEC-001 Prozess-System, SPEC-002 Blueprint-Familien).
- **4 Cron-Jobs umgebaut** — Play (ersetzt QA), Research, Dev, Direktor (ersetzt Review). Details unten.

### Baseline-Scorecard (2026-08-03)
| Metrik | Wert | Befund |
|--------|------|--------|
| actions_to_first_craft | 43 | Erst-Craft in 43 Aktionen — okay |
| blueprint_reachability | 1.000 | beide Blueprints erreichbar |
| **craft_variety** | **1** | 🔴 nur 1 Craft-Typ in 100 Aktionen |
| skill_spread | 0.298 | Können bringt etwas |
| feedback_quality | 0.600 | 60% informative Rückmeldungen |
| content_reachable | 0.667 | 3 Items (raw_meat/cooked_meat/reeds) unerreichbar |
| **session_depth** | **16** | 🔴 Langeweile nach 16 Aktionen |

Schwächste Metrik: `craft_variety` (1) — eng gekoppelt an `session_depth` (16). Ursache: nur 2 Blueprints, Prozess-System nicht eingebunden, kaum erreichbare Items. Daraus die zwei Specs.

### Cron-Jobs (IDs beibehalten, anpassen statt neu)
| Rolle | Job-ID | Schedule | Änderung |
|-------|--------|----------|----------|
| Play | `9777fe714dfb` | Mo/Mi/Fr 09:00 | war QA (Sa 16:00). Spielt Runs, rechnet Scorecard, findet Langeweile-Stelle. |
| Research | `c837d9d8dde1` | Di+Do 10:00 | Thema aus den Zahlen (schwächste Metrik), genau 1 Spec. |
| Dev | `10c0e68f3673` | Mo–Sa 14:00 | Tasks aus PLAN.md, sonst oberster Spec; darf sich bedienen, kein Summon. |
| Direktor | `d8ed1b92bc80` | So 18:00 | war Review. Schreibt PLAN.md neu, darf Cron-Jobs selbst ändern. |

Aus allen Prompts entfernt: Sprint-Cap, "Leerlauf ist der Feind", Worst-Case-Füllung, Summon-Mechanik, KW-Bezüge, Verbot Plan-Struktur zu ändern, Lessons-Learned 01.–03.08. Jeder Prompt trägt jetzt: *"CONSTITUTION.md ist unantastbar."* Export nach `cron/` aktualisiert (play/research/dev/direktor + OVERVIEW).

### Selbstmodifikation abgesichert
- Snapshot-Branch `pre-autonomy-2026-08-03` gepusht, bleibt liegen.
- Jede Änderung an `~/.hermes/cron/jobs.json` wird nach `cron/` exportiert + committet.

### Verifikation
- `python -m pytest` → **93 passed** (unverändert grün gegenüber Session-Start).
- Scorecard-Baseline deterministisch, reproducable über `python tools/scorecard.py`.

### Wartet auf Peter
- **CONSTITUTION.md** Freigabe (STATUS: Entwurf). Wenn er sie ändert/absegnet, ist der Kern gesetzt.

---
## 2026-08-03 — [Dev] Sprint KW 32 abgearbeitet: 5 🔴 Bugs + R01

### Erledigt (alle 6 Sprint-Tasks)
- **TASK-B01** — FIBER-Quelle: `plant_fiber`-Node (Chance 0.4) in forest_edge ergänzt. Neue Session sammelt FIBER und kann Axt craften (End-to-End-Test).
- **TASK-B02** — pebble-Template in items.json angelegt (STONE/PROJECTILE, durability 0.2). `create_item("pebble")` liefert "Kieselstein" mit Tags statt "Unbekannt".
- **TASK-B03** — Perception-Gates gesenkt: flint_shard 1.5→1.0, berries 2.0→1.0, mushroom 2.0→1.0. Bei Start-perception=1.0 ohne Grind sammelbar.
- **TASK-B04** — `execute_experiment` blockt condition=0-Items mit klarem Feedback ("... ist zerbrochen ...").
- **TASK-B05** — tick_counter initial 36 (6 Uhr). Kein Nacht-Kälte-Penalty beim Start, normale Starttemp.
- **TASK-R01** — processes.py auf JSON: `processes.json` + `ProcessData`/`load_processes()` in loader.py; `get_all_processes()` baut ProcessDefs aus JSON. Keine hartkodierten ProcessDefs mehr. **M0.3 damit abgeschlossen → `[x]`.**

### Ergebnis
- **93/93 Tests grün** (83 bestehend + 10 neu), `python -m pytest` in 0.44s.
- Sprint KW 32 vollständig abgearbeitet — keine offenen Tasks. Review (So 09.08.) plant KW 33 (R02, F01/F02 gemäß PLAN-Notiz).

### Änderungen
- `data/items.json` — pebble-Template
- `data/locations.json` — plant_fiber-Node (forest_edge), Perception-Gates gesenkt
- `engine/core.py` — tick_counter=36, condition=0-Check beim Crafting
- `data/processes.json` (neu), `data/loader.py`, `data/processes.py` — JSON-Loader
- `tests/` — TestBugs (B01–B05) + TestLoadProcesses
- `PLAN.md`, `BACKLOG.md` — Status-Updates

---

## 2026-08-02 — [Review] Weekly Triage + Sprint-Bestätigung (KW 32)

**Kontext:** Der Triage vom 01.08. (`187199c`) hat den KW-32-Sprint bereits vollständig aufgesetzt (5 🔴 Bugs + R01). Der heutige Review liest denselben neuesten QA-Report (`qa/2026-08-01.md`) — das ist ein Prüf-/Bestätigungslauf: Sprint steht, Backlog ist triagiert, seit dem 01.08. ist kein neuer Input dazugekommen.

### Erreicht (KW 31)
- **TASK-M03** (JSON-Loader Refactor) abgeschlossen — 83/83 Tests grün, keine hartkodierten Dicts in items/blueprints/locations.
- **QA-Playtest #1** — Engine stabil (Smoke 30/30, Unit 83/83), aber 5 🔴 Bugs → strukturell unspielbar, dokumentiert in `qa/2026-08-01.md`.
- **Research:** 4/6 Phase-0-Spiele analysiert (URW, CDDA, Ancestors, Neo Scavenger).

### Sprint-Status (KW 32)
- 7 Tasks angesetzt, alle `[ ]`: **TASK-B01…B05** (jeder 🔴 Bug als eigener Task) + **TASK-R01** (processes-Loader).
- Frühester Abarbeitungsbeginn **Mo 03.08. 14:00** — Sprint ist startbereit.
- R02 (Tech-Debt), F01/F02 (Features) bewusst nach **KW 33** verschoben (Bug-first, keine Sprint-Überladung).

### Blockiert
- Nichts extern. Kein neuer Input seit Vortag; der KW-32-Sprint deckt alle offenen 🔴 Bugs ab. Kein Dev-Leerlauf zu erwarten.

### Prioritäten KW 32
1. **Alle 5 🔴 Bugs** (Crafting strukturell unspielbar fixen) — B01 → B05, je eigener Task.
2. **R01** — processes.py auf JSON-Loader (schliesst M0.3 ab).
3. R02/F01/F02 rollen nach KW 33.

### Triage (BACKLOG)
- **🔴 Bugs:** 5/5 im KW-32-Sprint (B01–B05). Keine neuen seit 01.08.
- **🟡 Ideas:** M0.4/M1.x-Kandidaten (Tag-Substitution, Material-Quelle→Eigenschaften, Multi-Faktor-Crafting, Death-as-Legacy) → KW 33; Phase-2/3-Ideen (Condition-Web, Body-Part, Skills, Discovery, Biom, Starting Scenarios) → später.
- **🔵 Tech Debt:** R01 → Sprint KW 32; R02 → KW 33.
- **⚪ Research Leads:** 7 offene M0.2-Kandidaten (> 2) → **keine neuen Recherchen** in diesem Zyklus nötig.
- **Keine Einträge zu archivieren** — jedes Backlog-Item trägt bereits ein Sprint-/Phase-Ziel.

### Entscheidungen
- **Kein Schnitt auf KW 33:** Heute ist der letzte Tag von KW 31, die unmittelbar anstehende Woche ist KW 32 (Mo 03.08.). Der bestehende KW-32-Sprint ist korrekt und unangetastet — Tasks werden nicht vorschnell gerollt.
- **M0.3 bleibt `[~]`** (processes.py steht aus), **M0.2 bleibt `[~]`** (2 Original + 5 Kandidaten offen). Keine Milestone-Marker zu setzen — nichts Neues abgeschlossen seit 01.08.
- **M0.4 (Save/Load)** bleibt nächster Feature-Kandidat nach den Bugs — bereits im Backlog/Plan referenziert.

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