# Play-Scorecard-Session 2026-08-31 — erste Play-Lesung nach SPEC-011 (Verschleiß)

> **For Hermes:** Ausführung gemäß PLAY-Rolle im `primal-process`-Skill (Workflow-Schritte 1–8, incl. Commit+Push-Verify). Kein subagent-driven-development — das ist eine Mess-Session, kein Code-Bau.

**Goal:** Offizielle Scorecard-Lesung nach SPEC-011 (Werkzeugverschleiß + `sharpen_tool`, gelandet via Dev-Nachcommit 30.08.). Erwartung: **flach** vs. 29.08 (die 29.08-Scorecard kam bereits aus dem Dev-Nachcommit, seither nur Direktor-Docs). Der Play-Wert dieser Session liegt woanders: SPEC-011 im echten Spiel fühlen (Wear-Pfad, Pebble-Munitions-Ökonomie), die Langeweile-Stelle (guided exhaustion vs. `session_depth`) frisch vermessen, Report + BACKLOG + JOURNAL schreiben, committen.

**Approach:** Mess-reine Session. Dies ist die Fortsetzung eines Plan-Mode-Laufs vom 31.08. 09:10 (gleicher HEAD): pytest, Probes und guided/naive Swings sind dort bereits read-only vorgemessen — die Zahlen stehen unten mit exakten Repro-Kommandos. Der ausführende Run übernimmt die offiziellen Writes (Scorecard, Report, BACKLOG, JOURNAL) und verifiziert die Zahlen gegen die Vorlagen unten.

**Tech Stack:** Python 3.11, pytest, `tools/scorecard.py` (Play-Job besitzt die Scorecard-Files), `play/guided_full.py`, deterministische Seeds, `PYTHONPATH=.`-Inline-Probes.

---

## Aktueller Kontext / Annahmen

- **Repo-Zustand bei Plan-Erstellung (31.08. 09:10, HEAD `8e9a042`):** Working Tree clean, `main...origin/main` ohne ahead. `python -m pytest -q` → **261 passed** (vom Plan-Lauf verifiziert, 28.8 s).
- **Letzte echte Play-Lesung: 2026-08-26** (`play/2026-08-26.md`). Die `scorecard/2026-08-29.json` wurde **nicht** vom Play-Job geschrieben, sondern vom Dev-Nachcommit `05bd98b` (SPEC-011 + Delta-Tabelle im JOURNAL 30.08.). Es gibt keinen Play-Report für 29.08 — heute ist die erste Play-Lesung, die SPEC-011 offiziell sieht.
- **PLAN.md-Stand (Direktor-Neufassung 30.08.):** Ziele 1–3 (Gap zurück ins Band spiel-seitig, Prozesse öffnen, Wächter halten). Offene Tasks: B08 (INJURED-Zweig), Munitions-Ökonomie (Pebble = Consumable), Prozess-Hinweise für naive Spieler, Gap-Wächter-Reset, PLAY-TOOLING Feuer-Ökonomie statt Rückzug-Trigger. Beobachtend: `session_depth` (Probe bis 08.09.), `gear_uptime` (Probe bis 11.09.), `forage_pressure` (Probe bis 11.09.), `recovery_stability` (Probe bis 03.09.).
- **Vermessungsbasis 29.08 (`scorecard/2026-08-29.json`, 20 Seeds 20260803–20260822):** `actions_to_first_craft` 9.5 (p25 4, p75 13), `blueprint_reachability` 1.0 (10/10), `craft_variety` 4.5, `skill_spread` 0.186, `feedback_quality` 1.0 (v3), `content_reachable` 1.0 (18/18, keine dangling refs), `session_depth` 54.5 (p25 40, p75 68, v2), `discovery_gap` **0.70** (drittle Lesung über Band, naive_rate 0.3, naive_p25 0.3), `forage_pressure` 0.0 (v2, unter Band, Re-Baseline), `warmth_stability` 0.46, `recovery_stability` 0.375, `gear_uptime` **0.994** (v1, Erstlesung über Band).
- **Erwartete heutige Scorecard: flach.** Kein Spiel-Code, keine Data-Änderung seit `05bd98b` (seither nur Direktor-Docs: `1e282bd`, `8e9a042`). Deterministische Seeds → alle 13 Metriken ±0 gegen die 29.08-Vorwoche. `gear_uptime` rendert diesmal ±0 statt „— (Baseline)“ (Vorwoche hat die Metrik schon).

## Vorgemessen (Plan-Mode-Lauf 31.08. 09:0x, HEAD `8e9a042`, read-only — Zahlen sind heute reproduzierbar)

### A) Guided-Sweep, Test-Range 20260801–20260820 (1 Call pro Seed)

```
VOLLE 10-BP-Runs: 6 /20   (historisches Band ~6–13; 08-26: 8/20)
Exhaustion (full-only): median 21.5, range 20–44
Prozesse entdeckt (je Run): 3–6 von 10
```
- Repro: `PYTHONPATH=. python -c` mit `play.guided_full`, Loop `range(20260801, 20260821)`, genau EIN `guided_full(s)`-Call pro Seed (RNG-Strom-Disziplin, Pitfall 21.08).
- **6/20 = unteres Band-Ende, kein neues Signal.** Bekannte Messwerkzeug-Fragilität (Feuer-Versorgungsspirale, 28.08-Befund); der Fix ist PLAN-Task „Feuer-Ökonomie“ und gehört NICHT in diese Session.
- **Bot-Rot an SPEC-011/009:** der Bot versucht `treat_cut`/`treat_strain`/`sharpen_tool` nie (max 6/10 Prozesse) — Exhaustion misst die Decke also minimal zu niedrig. Ehrlich im Report benennen, keine Bot-Surgery hier.

### B) Naive-Probe, frische Seeds (`sc._run_session_depth`, gibt int zurück)

```
20260826 → 91, 20260827 → 74, 20260828 → 21, 404 → 48
```
- Offizielles `session_depth` 54.5 vs. **echter guided exhaustion ~21.5**: der naive v2-Bot liest die 2,5-fache Tiefe des echten Discovery-Caps. Die Metrik misst den Stall-Mechanismus (`stall_limit`), nicht die Langeweile-Stelle — diese Diskrepanz ist der Report-Headline.

### C) Pebble-Munitions-Bug live reproduziert (BACKLOG 27.08., PLAN-Task seit 30.08.)

```
Start: 8x Kieselstein als EIN Stack (cond 1.0, PROJECTILE/STONE), forest_edge, 40 gathers
→ nach ~4 Jagd-Erfolgen (gather ~11): "!!! Kieselstein zerbrochen !!!" — KOMPLETTER Stack weg (qty 8→0)
→ danach: Nachwurf vom Boden (pebble-Node knappbar) macht Munition gratis wieder voll (cond 1.0)
```
- Mechanik bestätigt: Wear 0.05/durability pro Erfolg, pebble durability 0.2 → 0.25/Erfolg → 4 Erfolge töten den ganzen Stack still, nur eine „zerbrochen“-Zeile. 
- **Neue Design-Beobachtung (nicht im BACKLOG 27.08.):** die Ökonomie heilt sich selbst — der Pebble liegt direkt daneben, Nachwurf ist gratis. Das Feel ist also nicht „Munition ist teuer“, sondern absurd: ein „Werkzeug“-Stack von 8 Steinen stirbt in einem Stück als Wegwerf-Munition, und dieselbe Aktion, die ihn getötet hat, beschafft sofort Ersatz. Der Bug kostet kaum Spielzeit, aber die Consumable-Fix-Richtung (PLAN-Task) bleibt richtig: genau EIN Projektil pro Schuss, kein Stack-Selbstmord.
- Repro: `PYTHONPATH=. python -c` — `GameEngine()`, `travel('forest_edge')`, `create_item('pebble', 8)` ins Inventar, 40× `gather()`, Stack-Cond/Qty nach jedem 5. Tick printen.

### D) sharpen_tool-Feel (SPEC-011 D)

- `execute_process('sharpen_tool')` ohne `flint_shard` → sauber: `{'success': False, 'message': 'Es fehlt dir Feuersteinsplitter.', 'reason': 'MISSING_INPUT:flint_shard'}` (kein generischer Fallback).
- Warnschwelle `WEAR_WARN_THRESHOLD = 0.25` (feuert einmalig beim Unterschreiten), Bruch bei ≤ 0, `SHARPEN_RESTORE = 0.5` (cap 1.0). Profil: ein Werkzeug mit durability 0.5 verliert 0.1/Erfolg → Warnung nach ~7 Erfolgen, Bruch nach ~10.
- Für den Report-Feel genügt das; ein voller Sharpen-Erfolgs-Path (worn Tool + flint) ist im Report optional: Werkzeug-Cond auf 0.3 setzen, `flint_shard` ins Inventar, `execute_process('sharpen_tool')` → erwartet cond 0.8, success True.

## Abbruchkriterien (vor jedem Write prüfen)

1. `python -m pytest` rot → STOP, Fehlerreport im finalen Response, **kein Commit** (Play-Workflow Schritt 1). Stand heute: 261 passed.
2. Scorecard weicht von „flach vs. 29.08“ ab (irgendeine Metrik ≠ ±0) → erst Forensik (`git log 05bd98b..HEAD --stat`, ob wirklich nur Docs), dann Report. Nie eine Zahl „reparieren“.
3. `git status` zeigt fremde un-committete Writes (z. B. Dev-Lauf crashte wieder vor Commit) → nicht adoptieren (Adoption ist DEV/Direktor-Regel), Scorecard trotzdem messen, Befund im Report notieren.

---

## Tasks

### Task 1: Session-Start-Checks

**Files:** keine Writes.

1. `cd ~/projects/primal-process && git fetch && git status -sb && git log --oneline -5`
   - Erwartet: clean, HEAD ≥ `8e9a042`, nichts ahead. Falls ein neuer Dev-Commit landete: PLAN.md re-lesen, Erwartungen unten anpassen (dann ist die Scorecard evtl. NICHT flach).
2. `python -m pytest -q 2>&1 | tail -3`
   - Erwartet: `261 passed`. Rot → Abbruch.

### Task 2: Offizielle Scorecard (der Play-Job BESITZT diesen Write)

Run: `python tools/scorecard.py`
- Schreibt: `scorecard/2026-08-31.json`, `scorecard/latest.json`, aktualisiert `SCORECARD.md` (Delta gegen Vorwoche = 29.08-File).
- Erwartete Tabelle: **alle 13 Metriken ±0**, Werte exakt wie Vermessungsbasis 29.08 oben. `gear_uptime`-Zeile: ±0 (nicht mehr „— (Baseline)“).
- **Verifikation:** `scorecard/2026-08-31.json` lesen und jede Zahl gegen den Abschnitt „Vermessungsbasis 29.08“ abgleichen. Abweichung → Abbruchkriterium 2.

### Task 3: PLAN.md-Akzeptanz-Mapping (Report-Abschnitt)

Zu beantworten im Report:
- **SPEC-011 offiziell bestätigt?** Teils: `gear_uptime` 0.994 über Band dokumentiert weiterhin, dass Attrition für den naiven Bot unsichtbar ist (Probe bis 11.09., beobachtend, kein Tuning). Das Spielgefühl steckt im Wear-Pfad — Probe C/D unten.
- **Gap 0.70, drittle Lesung über Band:** bereits Direktor-gesetzt als PLAN-Ziel 1 (spiel-seitige Antwort, B08 + Prozess-Hinweise + Überlebens-Hinweise). Im Report referenzieren, kein BACKLOG-Duplikat.
- **`session_depth` 54.5 (Probe bis 08.09.) vs. guided exhaustion ~21.5:** die Metrik-Nadel ist ~2,5× über dem echten Cap — Re-Baseline-Phase, nicht deuten, aber die „ehrliche Kompass-Nadel“ (PLAN) mit der heutigen Zahl belegen.

### Task 4: Probes — nur was der Report noch braucht

**Files:** keine. Alles Inline (`PYTHONPATH=.`), schreibt keine Repo-Files.

- **4a (Pflicht, kurz):** Pebble-Repro wie oben C — 15 gathers genügen, um Stack-Tod + Nachwurf-Maskierung zu zeigen. Zahlen in den Report (Erfolge bis Stack-Tod, Verhalten danach).
- **4b (optional):** Sharpen-Erfolgs-Path wie Abschnitt D.
- **4c (optional, wenn Zeit):** Wear-Warnung live: Werkzeug-Cond via Engine auf 0.26 setzen, einen Erfolg sammeln, „stark abgenutzt“-Zeile prüfen (einmalig, kein Spam).
- Die guided/naive Swings (Abschnitte A/B) sind vorgemessen und deterministisch — neu laufen lassen NUR wenn Task 1 einen neuen Dev-Commit zeigte (dann auch beide Zahlen im Report mit neuem HEAD benennen).

### Task 5: Play-Report schreiben — `play/2026-08-31.md`

**Files:** Create: `play/2026-08-31.md`.

Struktur (Headline zuerst — der wichtigste Befund ist die Langeweile-Stelle, nicht der Bug):
1. **Headline:** Der echte Boredom-Punkt bleibt am Content-Cap: guided exhaustion **median 21.5** (range 20–44, full-only, 6/20 volle Runs, Test-Range 20260801–20260820) — während `session_depth` 54.5 liest. Der komplette entdeckbare Inhalt (10 Blueprints, 10 Prozesse, 18 Templates) ist in ~21 gezielten Aktionen leer; danach Grind. **Und die Decke ist real etwas höher als gemessen: der guided Bot versucht 4 der 10 Prozesse nie** (treat_cut, treat_strain, sharpen_tool, …) — Messwerkzeug-Rot, dokumentiert, kein Spiel-Signal.
2. **Delta-Einordnung:** flache Scorecard = erwartetes Verhalten (keine Engine-Änderung seit 05bd98b). SPEC-011 war in der 29.08-Lesung schon drin — heute ist die erste *Play*-Lesung dazu, nicht eine neue Messung.
3. **SPEC-011 im Spielgefühl:** Wear ist graduell lesbar (Warnung bei 0.25, Bruch mit Zeile, sharpen heilt +0.5 für flint), **aber für den naiven Bot/naiven Spieler fast unsichtbar** (gear_uptime 0.994). Der einschneidendste Wear-Moment ist der Pebble-Stack-Selbstmord (Probe C) — und der ist als Ökonomie falsch (Consumable-Fix, PLAN-Task), nicht als Schwierigkeit.
4. **Naive-Probe** (Abschnitt B) + Gap 0.70 Kontext (PLAN-Ziel 1).
5. **Scorecard-Referenz:** eine Zahlenzeile, jede Zahl gegen `scorecard/2026-08-31.json` verifiziert (Pitfall 26.08: kein Zahlen-Drift).
6. **Fazit für Direktor/Peter** (3–5 Bullets): u. a. dass Prozess-Hinweise (PLAN-Ziel 2) auch `sharpen_tool`/`treat_*` abdecken sollten — die neuesten Prozesse sind für Spieler UND Messbot unsichtbar.

**Pflicht:** deutsches Deliverable in einem `write_file`, dann **Komplett-Re-Read + Patch-Säuberung VOR dem Stagen** (Pitfall 27.08: Sprach-Drift in One-Shot-Texten).

### Task 6: BACKLOG — nur wirklich Neue

**Files:** Modify: `BACKLOG.md` (erwartet: **gar nicht**).
- Gap 0.70: geflaggt (Direktor 30.08., PLAN-Ziel 1) — referenzieren, nicht doppeln.
- Pebble-Munition: BACKLOG 27.08. + PLAN-Task existiert — die neue Nachwurf-Maskierungs-Beobachtung gehört in den Report (Abschnitt 3), NICHT als neuer Eintrag.
- Neues 🔴 nur wenn Task 4 einen echten NEUEN Spiel-Bug zeigt (nächste freie Nummer fortführen, einzeilig + Fix-Richtung).
- Bot-Rot (4/10 Prozesse nie versucht): bereits als generisches Pitfall dokumentiert (14.08.) — kein neuer Eintrag; Feuer-Ökonomie-Fix bleibt PLAN-Task.

### Task 7: JOURNAL — prepend-without-clobber

**Files:** Modify: `JOURNAL.md`.

Format: `## 2026-08-31 — [Play] <Titel>`, Headline = Langeweile-Stelle (21.5 vs. 54.5).

Patch-Muster (Pitfall 08-24 — Header nicht schlucken):
- `old_string` = aktuelle Top-Zeile: `## 2026-08-30 — [Direktor] Plan-Neufassung: Gap 0.70 ist das Signal, Prozesse öffnen, Wächter halten`
- `new_string` = `<neuer Eintrag>\n\n---\n\n` + genau diese Zeile wieder.
- Danach Re-Read: **BEIDE** Header müssen überleben.

### Task 8: Commit + Push-Verify

```bash
cd ~/projects/primal-process && git add -A && git commit -m "play: scorecard + playtest (cron)" && git push
git status -sb && git log origin/main..main --oneline
```
- Erwartet: `main...origin/main` clean, kein ahead, leeres Log.
- `git add -A` scoop auch `.hermes/plans/` (dieser Plan + der 28.08-Play-Plan) — **gewollt** (Skill: Plan-Files werden vom ausführenden Run committed).
- Falls nichts zu committen (sollte nicht passieren): skip, kein Fehler.

---

## Files (Gesamt)

- Writes (sanctioned): `scorecard/2026-08-31.json`, `scorecard/latest.json`, `SCORECARD.md` (via `tools/scorecard.py` — DIESER Job besitzt sie)
- Create: `play/2026-08-31.md`
- Modify: `JOURNAL.md` (prepend), `BACKLOG.md` (nur bei echtem Neufund — erwartet: nein)
- Mitcommittiert: `.hermes/plans/*.md` (beide Play-Plan-Files, via `-A`)
- **Nie:** `tools/scorecard.py` selbst, `METRICS`, `CONSTITUTION.md`, Spiel-Code, Bot-Surgery (Feuer-Ökonomie = PLAN-Task, eigene Session)

## Tests / Validation

- Suite: `python -m pytest -q` → 261 passed vor JEDEM Commit (kein Code-Change geplant — Reihenfolge nur Form).
- Zahlen-Validation: Report-Zahlen 1:1 gegen `scorecard/2026-08-31.json` + die vorgemessenen Abschnitte A–D.
- Push-Validation: `git status -sb` clean + `git log origin/main..main` leer (nicht „gepusht“ behaupten — verifizieren).

## Risiken / Tradeoffs / Offene Fragen

- **Scorecard ≠ flach** → nur plausible Ursache ist ein neuer Commit zwischen Plan und Ausführung → Task-1-Check abdecken, sonst Forensik vor Report. Nie Werte glätten.
- **6/20 volle Runs** = unteres Band-Ende der dokumentierten Messwerkzeug-Fragilität — NICHT als Spiel-Signal deuten, NICHT in dieser Session am Bot schrauben (Feuer-Ökonomie-Task sauber trennen, Vorher/Nachher-Purität).
- **Exhaustion 21.5 mit 6 Stützpunkten** — kleine Basis; range 20–44 mit einem Ausreißer (Seed 20260802, 44). Median trotzdem die ehrliche Nadel; im Report n als 6 volle Runs benennen.
- **Pebble-Fix verschiebt Metriken evtl.** (Munitions-Ökonomie ändert Gather-Sequenz der Bots) — Dev-Task hat deshalb Delta-Tabellen-Pflicht; hier nichts vorwegnehmen.
- **Offene Frage an die Daten (für Direktor):** macht der Prozess-Hinweis-Hebel (PLAN-Ziel 2) die Prozesse auch für den NAIVEN v2-Bot sichtbar, oder braucht es eine Bot-Erweiterung (= Metrik-Kern-Rand, needs-Peter)? Als Beobachtung notieren, nicht als Task.
