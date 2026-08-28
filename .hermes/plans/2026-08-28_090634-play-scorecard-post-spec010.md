# Play-Scorecard-Session 2026-08-28 — erste Lesung nach SPEC-010 + SPEC-006

> **For Hermes:** Ausführung gemäß PLAY-Rolle im `primal-process`-Skill (Workflow-Schritte 1–8, incl. Commit+Push-Verify). Kein subagent-driven-development nötig — das ist ein Mess-Session, kein Code-Bau.

**Goal:** Offizielle Scorecard-Lesung nach dem ersten Content/Mechanik-Batch seit der v2-Re-Baseline (SPEC-010 Kaltstart-Pebble, SPEC-006 NEW_COMPONENT-Reveal, REC-002) — Deltas als Stream-Re-Sequencing einordnen (nicht als Fortschritt/Kollaps), Langeweile-Stelle (guided exhaustion vs. `session_depth`) neu vermessen, Gap-über-Band offiziell bestätigen, Play-Report + BACKLOG + JOURNAL schreiben, committen.

**Approach:** Mess-reine Session. Erst pytest, dann Scorecard, dann Verifikation der erwarteten Werte, dann eigene Runs (naive Probe + guided 20-Seed-Sweep, BEIDE Seed-Ranges), dann Report. Keine Bot-Surgery, kein Spiel-Code, keine Metrik-Berührung (Constitution). Die guided_retreat-Fix-Task (DEV-Plan-Task B) bewusst NICHT in derselben Session landen — sonst ist das Vorher/Nachher der Bots kaputt.

**Tech Stack:** Python 3.11, pytest, `tools/scorecard.py` (Play-Job besitzt die Scorecard-Files — diesmal DÜRFEN sie geschrieben werden), `play/guided_full.py`, deterministische Seeds.

---

## Aktueller Kontext / Annahmen

- **Repo-Zustand bei Plan-Erstellung (28.08. 09:02):** 245 Tests grün (verifiziert), Working Tree sauber außer untracked `.hermes/` (Plan-Files), HEAD `f9e43a1`.
- **Letzte Play-Lesung:** 2026-08-26 — VOR dem Dev-Batch: `session_depth` **64.5** (v2 Re-Baseline), `discovery_gap` **0.6** (Bandkante), `actions_to_first_craft` **34.5**, `craft_variety` **5.0**, `naive_discovery_rate` 0.4 / naive_p25 0.3, `content_reachable` 1.0 (18/18), `blueprint_reachability` 1.0 (10/10), `forage_pressure` 0.707 (v1, Probe zu Ende), warmth 0.46, recovery 0.375.
- **Seitdem gelandet (alle 26.–27.08.):** SPEC-010 (knappbarer `pebble`-Node im Start-Biome), SPEC-006-Kern (Einmal-Reveal `NEW_COMPONENT`, als SUCCESS-Zusatz-Meldung), REC-002 (tool-aware reachability, Zahlen unverändert), SPEC-011-Spec (Research, NICHT implementiert), forage_pressure-v2-Freigabe (Peter 27.08., Umsetzung als DEV-Plan-Task A offen).
- **Erwartete heutige Scorecard (Dev-seitig gemessen 26.08., deterministisch):**
  - `actions_to_first_craft` **9.5** (p25 4, p75 13) — SPEC-010-Akzeptanz `<20, p75<40`
  - `session_depth` **53.5** (Stream-Shift, kein Spiel-Fortschritt)
  - `craft_variety` **4.5**, `naive_discovery_rate` **0.35**
  - `discovery_gap` **0.65** → **über Band (0.6)** — bereits als Direktor-Flag im BACKLOG (26.08.)
  - Rest flach; keine Versions-Bumps im Spiel → **keine "neu definiert"-Deltas** in der Tabelle erwartet.
- **guided_full.py unverändert seit 20.08.** (Retreat-Trigger-Fix = DEV-Plan-Task B, offen). Erwartung: volle 10-BP-Runs im dokumentierten Fragile-Band ~½–⅔ (08-26: 8/20), Todes-Rate ist Messwerkzeug-Artefakt, kein Spiel-Signal.
- **Zwei Seed-Ranges (Skill, 27.08-Pitfall):** Test-Range `20260801–20260820` (historische Bot-Vergleiche, 8/20 etc.) vs. Scorecard-SEEDS `20260803–20260822` (BASE_SEED 20260803). 18/20 Überlappung, NICHT identisch — jede Sweep-Zahl muss ihre Range nennen.

## Abbruchkriterien (vor jedem Write prüfen)

1. `python -m pytest` rot → STOP, Fehlerreport im finalen Response, **kein Commit** (Play-Workflow Schritt 1).
2. Scorecard weicht massiv von den erwarteten Werten ab (z. B. `session_depth` ≠ ~53.5, `content_reachable` < 1.0) → erst untersuchen (`git log 08-26..HEAD`, metric-inline-probe), Report erst nach Klärung schreiben. Nie eine Zahl "reparieren".

---

## Tasks

### Task 1: Session-Start-Checks

**Files:** keine Writes.

1. `cd ~/projects/primal-process && git fetch && git status -sb && git log --oneline origin/main..main`
   - Erwartet: clean, nichts ahead (falls doch ahead: erst rebase + fremde Writes lesen, Play-Workflow).
2. `python -m pytest -q 2>&1 | tail -3`
   - Erwartet: `245 passed`. Rot → Abbruch.

### Task 2: Offizielle Scorecard (der Play-Job BESITZT diesen Write)

Run: `python tools/scorecard.py`
- Schreibt: `scorecard/2026-08-28.json`, `scorecard/latest.json`, aktualisiert `SCORECARD.md` mit Delta zur 08-26-Vorwoche.
- Erwartete Deltas in der Tabelle: `session_depth` 64.5→53.5 ↓, `craft_variety` 5.0→4.5 ↓, `discovery_gap` 0.6→0.65 (über Band), `actions_to_first_craft` 34.5→9.5 ↓↓ (niedriger=besser → aufwärts gerendert), `naive_p25` 0.3→0.25, Rest ±0.
- **Verifikation:** `scorecard/2026-08-28.json` lesen und JEDE Zahl gegen den Abschnitt "Erwartete heutige Scorecard" oben abgleichen. Abweichung → Abbruchkriterium 2.

### Task 3: PLAN.md-Tasks + Akzeptanz-Mapping lesen

**Files:** lesen: `PLAN.md`, `.hermes/plans/2026-08-27_183803-cron-dev-open-tasks.md` (nur Status: Task A–D noch offen?).

Zu beantworten im Report:
- **SPEC-010-Akzeptanz offiziell bestätigt?** `actions_to_first_craft` < 20, p75 < 40, reachability/content_reachable 1.0. Erwartet: JA (9.5/13/1.0/1.0).
- **SPEC-006 numerische Akzeptanz ("session_depth steigend")?** Erwartet: **NEIN** — 53.5 < 64.5. Das ist NICHT das Reveal gescheitert: das Reveal ist eine Meldung am SUCCESS, der v2-Bot parst keine SUCCESS-Texte (folgt nur NEAR_MISS), und der Wert ist ohnehin vom Stream-Shift dominiert. Ehrlich so schreiben: numerisch nicht bestätigt, Mechanik-Verifikation über Task 4b.
- **Gap 0.65 über Band** = bestätigtes Spiel-Signal (naive Tier-2-Invisible) — Verweis auf den bestehenden BACKLOG-Direktor-Flag vom 26.08, kein Duplikat-Eintrag.

### Task 4a: Naive-Probe (frische Seeds, Scorecard-konsistent)

**Files:** keine. Probe schreibt nichts (inline, kein Scorecard-File-Touch).

Run:
```bash
cd ~/projects/primal-process && PYTHONPATH=. python -c "
from tools import scorecard as sc
for s in (20260826, 20260827, 404):
    r = sc._run_session_depth(s)
    print(s, {k: r[k] for k in r if k in ('actions','last_new','n_blueprints','n_procs','tier2_reached','survival')})
"
```
- Falls die Key-Namen abweichen: zuerst `grep -n "def _run_session_depth" -A40 tools/scorecard.py` und die tatsächlich zurückgegebenen Keys verwenden (Signature verifiziert: Zeile 646, `(seed, stall_limit=15, cap=1500)`).
- Erwartet (Konsistenz mit 08-26-Report): v2-Bot öffnet Tier-2 auf starken Seeds, `n_procs` bleibt 0 (Runner ruft nie `execute_process`), stall ~40–70 Aktionen.
- Interpretation für den Report: der offizielle naive Wert 53.5 (Mittel der SEEDS-Range) vs. diese Einzel-Runs — der "echte Zufalls-Michel" (playtest_driver, falls lauffähig) stirbt weiter vor ~18–24 Aktionen; nur der ziel-bewusste v2-Bot überlebt bis zum Stall.

### Task 4b: SPEC-006-Reveal-Sichtbarkeitsprobe (Scratch, kein File-Write)

Run (Scratch, PRINT des Rohwerts, kein Assert im ersten Durchgang):
```bash
cd ~/projects/primal-process && PYTHONPATH=. python -c "
import random; random.seed(7)
from engine.core import GameEngine
g = GameEngine()
for _ in range(15): g.gather()
inv = g.player.inventory.items
print([(i.name, sorted(i.tags)) for i in inv])
# Kombinationen aus dem Inventar probieren, bis ein Blueprint zündet:
from itertools import combinations
for combo in combinations(inv, 2):
    res = g.execute_experiment(list(combo))
    print(repr(res)[:200])
" | head -40
```
- Zu prüfen: der ERSTE erfolgreiche Tool-Bau enthält im Message-Text den generischen Einmal-Hinweis (Teilstring **`"verbinden"`** — NICHT `"zusammengehören"`, das ist der Near-Miss-Text).
- Erwartet: Reveal genau einmal pro neuem Werkzeug-Tag, kein Rezept-/Tag-Leak im Text.
- Fällt die Probe negativ aus → das ist ein echter 🔴 Bug (Reveal nicht Spieler-sichtbar) → Task 6.

### Task 5: Guided-Sweep — die Langeweile-Stelle (Kern-TASK)

**Files:** keine. **Ein Call pro Seed** (Doppel-Call korrumpiert den RNG-Strom — dokumentierter 21.08-Pitfall; `guided_full` seedet intern selbst via `G.__init__`).

Run (Test-Range, historisch vergleichbar):
```bash
cd ~/projects/primal-process && PYTHONPATH=. python -c "
import statistics, play.guided_full as gf
res = {}
for s in range(20260801, 20260821):
    r = gf.guided_full(s)          # GENAU EIN Call pro Seed
    bps = len(r.game.player.known_blueprints)
    procs = len(r.game.player.known_processes)
    res[s] = (r.last_new, r.actions, bps, procs, r.game.player.hp)
    print(s, res[s])
full = [k for k, v in res.items() if v[2] >= 10]
print('VOLLE 10-BP-Runs:', len(full), '/20  (Band ~6-13)')
if full:
    ex = [res[k][0] for k in full]
    print('Exhaustion (full-only): median', statistics.median(ex), 'range', min(ex), '-', max(ex))
"
```
Dann denselben Loop über die Scorecard-Range `range(20260803, 20260823)` — nur wenn die Zahlen für den Report gegen die offiziellen 20 SEEDS gemischt werden; beide Ranges IM Report getrennt benennen.

**Erwartung / Kernfragen für den Report:**
1. Volle Runs im Band (~½–⅔; 08-26: 8/20)? Darunter → Messwerkzeug-Fragilität (Task B offen), NICHT Spiel-Signal. Kein Over-Hardening in dieser Session.
2. **Exhaustion (full-only) bewegt sich?** Erwartet: Decke unverändert ~15–22 gezielte Aktionen. Der Pebble-Node verkürzt die ROUTE zum ersten Craft (9.5 statt 34.5 Aktionen), nicht die Zahl der entdeckbaren Inhalte — der Boredom-Punkt hängt am Content-Cap (10 BP, 9 Prozesse, 10 Templates), nicht an der Anfahrt. Falls die Decke TROTZDEM sinkt (z. B. auf ~12): dokumentieren, ist konsistent (früherer Start → gleicher Content früher geleert), kein Widerspruch.
3. Nach `last_new`: reine Grind-Phase = die Langeweile-Stelle, mit Aktionenzahl benennen.

### Task 6: Play-Report schreiben — `play/2026-08-28.md`

**Files:** Create: `play/2026-08-28.md`.

Struktur (Headline zuerst — der wichtigste Befund ist die Langeweile-Stelle, nicht der Bug):
1. **Headline:** guided exhaustion vs. offizielles `session_depth` 53.5 — Decke unverändert, Content-Cap bleibt die Langeweile-Stelle (Zahl exakt aus Task 5).
2. **Delta-Einordnung:** alle heutigen Bewegungen = SPEC-010-Stream-Re-Sequencing (dokumentierte shared-measurement-stream-Klasse), **weder Fortschritt noch Kollaps**; `session_depth` "fallend" in der Tabelle ist Stream-Arithmetik. SPEC-010-Akzeptanz offiziell bestätigt (Zahlen). SPEC-006 numerisch NICHT bestätigt (Task-3-Begründung).
3. **Gap 0.65 über Band:** offiziell bestätigt, Verweis auf BACKLOG-Direktor-Flag 26.08, spiel-seitige Antwort (NEAR_MISS/Gate-Balance) bleibt Direktor-Sache — keine Metrik-Berührung.
4. **Naive-Probe + Reveal-Probe** (Task 4): Beobachtungen, B08/INJURED nur wenn neu betroffen.
5. **Scorecard-Referenz** (Zahlenzeile, JEDE Zahl gegen `scorecard/2026-08-28.json` verifiziert — Pitfall 26.08: kein Zahlen-Drift).
6. **Fazit für Direktor/Peter** (3–5 Bullets, keine Romane).

**Pflicht:** German-Deliverable in einem `write_file`, dann **Komplett-Re-Read + Patch-Säuberung VOR dem Stagen** (Pitfall 27.08: Sprach-Drift in einshot-deutschen Texten).

### Task 7: BACKLOG — nur wirklich Neue

**Files:** Modify: `BACKLOG.md` (bedingt).
- Erwartet: **keine** neuen Einträge. Gap-über-Band ist bereits geflaggt (26.08) — im Report referenzieren, nicht doppeln.
- Neue 🔴 nur wenn Task 4b/5 einen echten Spiel-Bug zeigt (z. B. Reveal unsichtbar → B09-Nummer fortführen, einzeilig + Fix-Richtung).
- 🔵 falls guided-Vollrate deutlich unter Band fällt UND Task-5-Forensik einen NEUEN (nicht den bekannten Retreat-)Grund zeigt.

### Task 8: JOURNAL — prepend-without-clobber

**Files:** Modify: `JOURNAL.md`.

Format: `## 2026-08-28 — [Play] <Titel>`, Headline = Langeweile-Stelle.

Patch-Muster (Pitfall 08-24 — Header nicht schlucken):
- `old_string` = aktuelle Top-Zeile: `## 2026-08-27 — [Research] SPEC-011 — Werkzeugverschleiß ist kodierte Stille`
- `new_string` = `<neuer Eintrag>\n\n---\n\n## 2026-08-27 — [Research] SPEC-011 — Werkzeugverschleiß ist kodierte Stille`
- Danach Re-Read: **BEIDE** Header müssen überleben.

### Task 9: Commit + Push-Verify

```bash
cd ~/projects/primal-process && git add -A && git commit -m "play: scorecard + playtest (cron)" && git push
git status -sb && git log origin/main..main --oneline
```
- Erwartet: `main...origin/main` clean, kein ahead, leeres Log.
- `git add -A` scoop auch `​.hermes/plans/` (dieser Plan + der 27.08-DEV-Plan) — **gewollt** (Skill: Plan-Files werden vom ausführenden Run committed, nicht löschen/außen vor lassen).
- Falls nichts zu committen (sollte nicht passieren): skip, kein Fehler.

---

## Files (Gesamt)

- Writes (sanctioned): `scorecard/2026-08-28.json`, `scorecard/latest.json`, `SCORECARD.md` (via `tools/scorecard.py` — DIESER Job besitzt sie)
- Create: `play/2026-08-28.md`
- Modify: `JOURNAL.md` (prepend), `BACKLOG.md` (nur bei echtem Neufund)
- Mitcommittiert: `.hermes/plans/*.md` (beide Plan-Files, via `-A`)
- **Nie:** `tools/scorecard.py` selbst, `METRICS`, `CONSTITUTION.md`, Spiel-Code, Bot-Surgery (Retreat-Fix = DEV-Plan-Task B, nächste Session)

## Tests / Validation

- Suite: `python -m pytest -q` → 245 passed vor JEDEM Commit (kein Code-Change geplant — Reihenfolge nur Form).
- Zahlen-Validation: Report-Zahlen 1:1 gegen `scorecard/2026-08-28.json`.
- Push-Validation: `git status -sb` clean + `git log origin/main..main` leer (nicht "gepusht" behaupten — verifizieren).

## Risiken / Tradeoffs / Offene Fragen

- **Scorecard ≠ Dev-Erwartung** → deterministische Seeds machen das unwahrscheinlich; falls doch: erst `git log`-Forensik, dann Report. Nie Werte "glätten".
- **Guided-Vollrate unter Band** → bekannte Messwerkzeug-Fragilität (Retreat-Trigger), kein Spiel-Signal; Fix bewusst NICHT hier (Vorher/Nachher-Purität), sondern über DEV-Plan-Task B.
- **Gap 0.65** → Richtungsspiel-Signal, Antwort ist spiel-seitig (Direktor); eine Metrik-Abschwächung ist verboten (Constitution).
- **forage_pressure** bleibt v1 (0.707-artig) bis DEV-Plan-Task A landet — nicht deuten, nicht tunen; Probezeit-Regel.
- **Offene Frage an die Daten:** verkürzt der Pebble die guided-Route sichtbar (Exhaustion < 15)? Erwartung: nein/kaum — Content-Cap dominiert. Wenn doch: sauber dokumentieren, ist plausibel (früherer Chain-Start), kein Widerspruch zur Decken-These.
- **Offene Frage:** zeigt das Reveal auch dem NAIVEN Spieler Richtung (v2-Bot ignoriert SUCCESS-Texte)? Nicht messbar ohne Bot-Änderung (= Metrik-Kern-Rand) → als Beobachtung für den Direktor notieren, nicht als Task.
