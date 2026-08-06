# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Play, Direktor).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-08-06 — [Dev] SPEC-004: Ressourcenerschöpfung & Regeneration (Foraging)

### Task
`SPEC-004-resource-depletion.md` — vorratsbasierte Nodes: Ernte reduziert `stock`, Erfolg skaliert `chance * stock/max_stock`, Regeneration über `_advance_time`. Gegen die Langeweile-Stelle (Play 05.08.): Rotation/Rückkehr erzwingen, statt unendlichem Melken desselben Nodes. Metrik-Vorschlag `forage_pressure` als Probezeit-Metrik aufgenommen.

### Mechanik (implementiert)
- **`data/locations.py`/`loader.py` — `ResourceNode` erweitert:** `max_stock` (default 10), `regen_per_tick` (default 0.05), `harvest_cost` (default 1), veränderlicher `stock` + `depleted`-Flag. Fresh pro Engine-Instanz (kein Cross-Session-Bleed, deterministisch pro Seed).
- **`locations.json` — pro-Node-Balance:** Flaggschiffe knapp/langsam (`flint_shard`, `bone`: max_stock 6, regen 0.03), Grundstoffe großzügig (`stick`/`pebble`: 30, regen 0.15). Knappheit gezielt auf den bestehenden flint-Bottleneck gelegt, nicht flächig.
- **`engine/core.py::gather()`:** `eff_chance = chance * (stock/max_stock)`; Vorrat um `harvest_cost` reduziert; erschöpfter Node → neuer Reason `DEPLETED` + `_feedback_message("DEPLETED")` = *"Diese Stelle ist erschöpft. Komm später zurück."* (nie stilles "nichts").
- **`_advance_time()`:** regeneriert alle Nodes über verstrichene Ticks; `depleted` erholt sich erst, wenn genug Zeit eine Ernte-Portion aufgefüllt hat. Andere Orte regenerieren, während man unterwegs ist.
- **Design-Verfeinerung:** `depleted`-Flag nötig, weil ein einzelner Gather-Tick sonst eine homöopathische Regeneration nachschiebt und der Node nie ehrlich "erschöpft" melden würde. Generöse Grundstoffe oscilieren kurz an der Schwelle (gewollt — sollen kein Gate sein), knappe Flaggschiffe bleiben stabil erschöpft (gewollt).

### Metrik — `forage_pressure` (Probe bis 20.08.)
In `METRICS` aufgenommen (Band 0.1–0.5, keine Richtung, `probation_until=2026-08-20`). **Erstwert 0.71 (über Band)** — siehe BACKLOG: Definition `stock < max_stock` ist ein sehr sensibler Schwellenwert; Erstwert deutet auf Grind-Gefühl oder Kalibrierungs-Missmatch. Bewusst im Probezeit-Netz gelassen, statt still nachzujustieren.

### Akzeptanz-Check
- Wiederholtes Sammeln → Erschöpfung mit `DEPLETED`-Meldung, nie stilles "nichts" ✓
- `_advance_time(N)` regeneriert bis `max_stock`; erschöpfter Node wieder erntbar nach Zeit ✓
- Erfolg skaliert mit `stock/max_stock` ✓
- `DEPLETED` hat Label in `_feedback_message` (Label-Vollständigkeit bleibt grün) ✓
- `python -m pytest`: **165 passed** (vorher 158) ✓
- Metrik-Werte gehalten: `session_depth` 24→25, `discovery_gap` 0.375 (im Band), `content_reachable` 1.0, `feedback_quality` 1.0; `forage_pressure` 0.71 (Probe, über Band).

### Constitution-Check
Kein Rezeptbuch geändert; CLI-Text bleibt; stdlib only; keine bestehende Metrik entfernt/umdefiniert — nur neue `forage_pressure` in Probezeit ergänzt (erlaubt, keine Freigabe nötig). Vertieft Entdecken (lebende Welt, Rotations-Entscheidung), kein Content-Selbstzweck.

---

## 2026-08-06 — [Research-Explore] SPEC-004: Ressourcenerschöpfung & Regeneration

### Auftrag
Explorations-Modus — freie Suche nach System-Vertiefung, **kein** Metrik-Anker. Kontext: CONSTITUTION.md, Scorecard 2026-08-05, Play-Report 2026-08-05 gelesen.

### Befund (die System-Schwäche)
Play 05.08. nennt die Langeweile-Stelle schärfer als jede Metrik: nach ~40 Aktionen ist die Entdeckungsmenge (2 Familien + 4 Prozesse + ~12 Templates) geleert, übrig bleibt "sinnloses Sammeln". **Ursache hinter dem Symptom:** `GameEngine.gather()` wirft bei jedem Aufruf gegen eine feste `node.chance` — Nodes sind **unendlich und kostenlos**. Kein Grund für Ortswechsel, Zeit ohne Sammel-Wert, keine Rückkehrmotivation. Terrain/Zeit/Wetter existieren, sind aber fürs Sammeln bedeutungslos. Eine System-Leere, die keine Metrik verlangt, aber `session_depth` strukturell kurz hält.

### Mechanik
**Vorratsbasierte Nodes mit Erschöpfung + zeitbasierter Regeneration** (URW: selbsterhaltende Welt/Rotation; Vintage Story/Zomboid: Depletion + Respawn). Ernte reduziert `stock`; Erfolg skaliert `chance * stock/max_stock`; Regen läuft über `_advance_time` → Ort und Zeit werden zu echten Ressourcen. Erzwingt Rotation + Rückkehr statt unendlichem Melken desselben Nodes. Vertieft Entdecken, **ohne** neuen Content (gegen "Content-Menge als Selbstzweck").

### Metrik-Wirkung (ehrlich)
`session_depth` **steigend** (primärer Effekt, gegen die Langeweile-Stelle) — aber nur wenn Agenten Regen tatsächlich nutzen, sonst Reibung. **Keine** beabsichtigte Änderung an `discovery_gap`/`craft_variety`/`content_reachable`/`feedback_quality` — bewusst eine Mechanik, die keine bestehende Metrik bewegt. Konform zur Constitution: nur **neue** Metrik ergänzt, keine entfernt/abgeschwächt.

### Artefakte
- `specs/SPEC-004-resource-depletion.md` (neu)
- `metrics/proposed/forage_pressure.md` (neu) — Band 0.1–0.5, misst ob Knappheit *gefühlt* wird, nicht trivial zu heben (echte Node-Dynamik über Agent-Sequenzen)
- `PLAN.md` — SPEC-004 als offener Task
- `JOURNAL.md` — dieser Eintrag

### Constitution-Check
Kein Rezeptbuch; CLI-Text bleibt; stdlib only; Metrik-Core unangetastet (nur Ergänzung). Verstoß nicht gefunden.

---

## 2026-08-05 — [Dev] SPEC-002: Blueprint-Familien + Discovery-Feedback

### Task
`SPEC-002-blueprint-families.md` — Craft-Varietät (`craft_variety`=1.0) heben, indem statt 2 Einzel-Blueprints (Axt/Messer) **Tag-Familien-Slots + 3 Werkzeug-Familien mit je 2–3 Varianten** existieren und Fehlschläge kategorisiertes Feedback geben.

### Mechanik
- **Tag-Familien-Layer:** `TAG_FAMILIES` (`SHARP_OR_HARD`, `SHARP_OR_RIGID`, `RIGID_OR_FIBER`) + `_slot_satisfied()` — Slot-Anforderungen können Familien-Namen sein, die mehrere Tags subsumieren. Werte sind EITHER Familie ODER Einzel-Tag.
- **3 Werkzeug-Familien (je eigene Tag-Kombination):**
  - Axt (CHOPPING): `axe`(FLINT) / `axe_bone`(BONE) / `axe_stone`(STONE)
  - Messer (CUTTING): `knife`(FLINT) / `knife_bone`(BONE) / `knife_stone`(STONE)
  - Speer (PIERCE): `spear` (Familie SHARP_OR_RIGID) / `spear_bound` (+RIGID_OR_FIBER)
  - Material-Determinismus: jede Variante verlangt ein anderes Material-Tag → je nach Fund ist die Route eindeutig (flint→Feuerstein-, bone→Knochen-, stone→Stein-Variante).
- **Funktionale Tags datengetrieben:** `tool_tags`-Feld in BlueprintData/ToolBlueprint (statt hartkoddierter `if bp.id ==`).
- **`_no_match_reason` verbessert:** wählt den Blueprint, dem der Spieler am nächsten ist (meiste erfüllte Slots), und nennt genau EIN fehlendes Merkmal. Familien-Slots werden auf einen Mitglieds-Tag aufgelöst. Nie generisches Null-Feedback.

### Daten/Content
- `items.json`: **+`bone`** (BONE+HARD, scharfe Knochen-Werkzeugkante), `flint_shard` + `FLINT`.
- `locations.json`: **`bone`-Node in hidden_cave** (Knochen als Werkstoffquelle).
- `blueprints.json`: 2 → **8 Blueprints** (3 Familien × je 2–3 Varianten).

### Fixes (durch SPEC-002-Inhalte exponiert)
- **Engine-Robustheit (Crash):** `_create_tool`-Verbrauch crashte (`ValueError: list.remove`) bei selektierten Stacks, die im Inventar zusammengeführt wurden oder doppelt referenziert sind — jetzt konsumiert nur, was wirklich im Inventar liegt. (Real erreichbar: Speer aus mehreren Festen / Doppel-Selektion im CLI.)
- **Archiv-Smoke-Test aktualisiert:** `_smoke_test.py` erwartete noch das alte Spiel (`3× Stab = Fehlschlag`, `"Nichts passiert."` in Meldung). Beides ist bewusst obsolet (3 Feste = Holzspeer seit SPEC-002; Null-Feedback ist verbannt). Assertions auf den neuen Zustand gehoben.

### Akzeptanz-Check
- **3 Werkzeug-Typen × je ≥2 Varianten craftbar** (Tests: `TestBlueprintFamilies`) ✓
- Fehlschlag mit bekanntem Ziel-Tag nennt konkreten Grund (`MISSING_TAG:` + Label), nie generisch ✓
- `python -m pytest`: **155 passed** (vorher 147) ✓
- `craft_variety` Median: **1.0 → 3.0** (p25 1→2, p75 2→4) inline gemessen; `content_reachable` 1.0 (13/13, bone erreichbar), `feedback_quality` 1.0 (unverändert).

### Backlog-Triage
- **NEU (Ideen):** Stack-Verschmelzung vs. Mehrfach-Slot-Inventar: gleichnamige Items verschmelzen im Inventar zu einem Stack → Items, die 2× dasselbe Material brauchen, sind nur über distinkte Materialien erreichbar (Speer = reeds+Ast statt 2×Ast). Kein Bug, eine echte Design-Spannung (Mengen-bewusstes Matching wäre der saubere Fix). → BACKLOG 🟡 Ideen.
- **SPEC-003 aussetzen:** aktuelle Scorecard zeigt `discovery_gap`=0.25 (Unterkante), `naive_p25`=0.5 — SPEC-003-Ziel (Gap-unter-0.2 / Schwanz schließen) ist bereits eingetreten; Umsetzung riskt Überführung. An Direktor delegiert (Plan-Neufassung So). NICHT blind implementiert.

## 2026-08-04 — [Dev] SPEC-001: Prozess-System aktiviert

### Task
`SPEC-001-process-system.md` — das seit dem Umbau tote Prozess-System (`data/processes.py`, `processes.json`) in die Engine eingebunden. Quellen-Problem: `reeds`, `raw_meat`, `cooked_meat` waren unerreichbar → `content_reachable`=0.667, und es gab fast keine erkennbaren Craft-Wege.

### Engine
- `GameEngine.execute_process(process_id)`: prüft Inputs (Mengen), Werkzeug-Tags, konsumiert Inputs, `_advance_time(duration, 2.0)`, erzeugt Outputs, trackt `known_processes`. Reasions: `SUCCESS`/`UNKNOWN_PROCESS`/`MISSING_INPUT:<id>`/`MISSING_TOOL:<tag>`. `required_tag_in_env` bewusst weich (SPEC-001: vorerst optional, Locations tragen noch keine Tags).
- `available_processes()` — Prozesse, deren Anforderungen aktuell erfüllt sind (für CLI).
- `_count_template`/`_consume_template`/`_item_name` — Helfer.
- **knife erhält jetzt `CUTTING`** (nur axe hatte `CHOPPING`) → `create_tinder` braucht ein CUTTING-Werkzeug, das damit aus einem frischen Start craftbar ist.
- `Player.known_processes` ergänzt (für `session_depth`, das es bereits ausliest).

### Daten
- `items.json`: **+3 Prozess-Output-Templates** `sharp_stone`/`tinder`/`fire_pit` (vorher lieferte `create_item` nur "Unbekannt"); `reeds` + `KINDLING` (Feuerbohrer-Werkzeug).
- `locations.json`: **`reeds`-Node in hidden_cave** (per Spec), **`raw_meat`-Node in forest_edge** (Jagd mit `PROJECTILE`, z.B. Kieselstein) → beide Items sammelbar.
- `processes.json`: **+`cook_meat`** (`raw_meat` → `cooked_meat`, env-Tag HEAT_SOURCE weich).

### CLI
- `main.py`: Action `[p]rocess` — listet `available_processes()`, Auswahl via Index.

### Constitution-Check
- Tag-Crafting als Kern unangetastet; Prozesse sind Transformationen mit Umgebungs-/Werkzeug-Kontext, kein Rezeptbuch.
- Neue Items (sharp_stone/tinder/fire_pit) sind erreichbare Prozess-Outputs, keine Content-Deko als Selbstzweck.
- **Metrik-Core unangetastet:** `tools/scorecard.py`/`METRICS`/Play-Job NICHT verändert. Siehe Backlog-Eintrag unten.

### Verifikation
- `python -m pytest` → **147 passed** (134 + 13 neue Prozess-Tests in `test_engine.py`; `test_loader.py` auf neue Datenstände aktualisiert).
- Scorecard rechnet: `content_reachable` **0.667 → 1.0** (12/12, inkl. raw_meat/cooked_meat/reeds), `session_depth` 24→26. Alle Metriken ohne Fehler.
- Akzeptanzkriterien: `make_sharp_stone` (2× pebble → sharp_stone) ✓, `create_tinder`/`start_fire` von frischem Start erreichbar ✓ (reeds sammelbar, knife=CUTTING, reeds=KINDLING), `cooked_meat` aus `raw_meat` ✓, `[p]rocess` im CLI ✓.

### Backlog / wartet auf Peter
- **`craft_variety` zählt Prozesse noch nicht.** Der naive Play-Bot ruft nur `execute_experiment`, nie `execute_process` — das neue System bleibt dadurch für diese Metrik unsichtbar. Die Spec verlangt, Prozesse als Craft-Typ zu zählen, aber das ist eine Umdefinition der Metrik (Constitution: braucht Peters Freigabe). NICHT gemacht. → BACKLOG.

---

## 2026-08-05 — [Play] Scorecard + Playtest (cron)

### Scorecard (vs 03.08.)
`content_reachable` 0.667→**1.0** (Ziel ≥0.8 erreicht, 12/12), `craft_variety` 0.5→1.0, `session_depth` 24→26, `actions_to_first_craft` 63→62, `feedback_quality` 1.0, `blueprint_reachability` 1.0, `skill_spread` 0.315→**0.259** (↓). `discovery_gap` 0.5→**0.25** — im Band, aber an der **unteren** Kante; naive_discovery_rate 0.5→0.75, **naive_p25 0.0→0.5**.

### Wichtigster Befund — Langeweile-Stelle (session_depth)
Die komplette Entdeckungsmenge ist **2 Blueprints + 4 Prozesse + ~12 Templates**. Eine geführte Session (TDD-Play) hat ALLES in ~40 Aktionen geleert (knife, axe, tinder, fire, cooked_meat); danach gibt es kein weiteres Ziel — `session_depth`=26 misst es, gefühlt ist es schärfer: das Discovery-Spiel ist nach Minuten fertig, übrig bleibt sinnloses Sammeln. Das ist die Stelle, an der nichts Interessantes mehr passiert.

### Zwei konträre Enden, eine Leerstelle
- **Guided:** entleert den Kuchen in ~40 Aktionen → zu wenig Inhalt.
- **Naive (seed 7, 11):** 0 Blueprints, nur `MISSING_TAG:SHARP`, Langeweile bei Aktion 13/24. **Beide Tools brauchen `HARD`/`SHARP` = nur `flint_shard`** (pebble ist STONE, nicht HARD); flint nur am mountain_peak → einzelner Ort wird Hard-Gate ohne Leitfaden.

### Bugs (→ BACKLOG 🔴)
- **B06 `log_oak`:** Node referenziert Template nicht in items.json → fällen mit frischer Axt gibt "Unbekannt".
- **B07 `clay_lump`:** braucht `SHOVEL` (existiert nirgends) + Template fehlt → doppelt tot.
`content_reachable`=1.0 ist gegen beide **blind** (zählt nur TEMPLATE_DB-Keys) → Metrik-Blindspot (🟡 Backlog, Peters Freigabe für Metrik-Änderung).

### SPEC-003-Konflikt (→ an Direktor)
`discovery_gap` untere Ecke + `naive_p25` 0.5 — genau die Wirkung, die SPEC-003 liefern sollte, ist ohne SPEC-003 eingetreten (durch SPEC-001/Content). Neuerliche Umsetzung von SPEC-003 droht die Gap **unter 0.2** (Überführung) zu drücken. Priorität/Schärfe von SPEC-003 vor Umsetzung neu prüfen. `craft_variety`-Prozess-Umdefinition weiterhin offen (Peters Freigabe).

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