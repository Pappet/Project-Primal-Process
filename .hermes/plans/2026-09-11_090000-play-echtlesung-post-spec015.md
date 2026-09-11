# Play-Session-Plan 2026-09-11 — Play-Lesung post-SPEC-015 (Rast): Erstlesung `rest_adoption` + Nacht-Bogen

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.
> Erzeugt aus dem Play-Cron-Lauf 2026-09-11 (Plan-Mode). Pre-Measurement komplett
> ausgeführt, alle Zahlen auf Tages-HEAD c56e6ff, 342 passed + 1 xfailed (36 s).
> **Der Plan-Run hat KEINE Writes gemacht** — alle Writes (Scorecard-Dateien,
> Play-Report, BACKLOG, JOURNAL, Commit) trägt der executing Play-Run nach.
> Die Messung hier ist fertig und deterministisch; der executing run kann sie
> 1:1 übernehmen und muss nur noch die Writes ausführen.

**Goal:** Erste offizielle Play-Lesung von SPEC-015 (`rest()`-Verb, 10.09. gelandet):
`rest_adoption`-Gegenprobe (explorativ), Nacht-Bogen isoliert, Heil-Kette über Rast,
Boredom-Punkt nach dem neuen Content. Befunde in `play/2026-09-11.md`, Bugs → BACKLOG,
JOURNAL-Entry, Commit+Push.

**Architecture:** Read-only Pre-Measurement (pytest + Scorecard-Probe + Engine-Probes
via `/tmp`-Skripte, kein Repo-Write), dann die sanctioned Writes durch den executing
run. Alle Probes sind bereits gelaufen; die Ergebnisse stehen unten in der
Erwartungs-Tabelle und werden vom executing run nur noch gegen Tages-HEAD re-verifiziert.

**Tech Stack:** pytest (repo `.venv` 3.11), `tools/scorecard.py` (schreibt), stdlib-only Engine.

---

## Kontext (aus PLAN.md / Scorecard 09.09. / Play 09.09.)

- SPEC-015 gelandet 10.09. (2ae395f + c56e6ff): `rest()`-Verb (`_advance_time(4, 0.4)`),
  Menü `[r]asten`, Go/No-Go alle 12 Metriken byte-identisch, 342 Tests grün.
  **Offene Akzeptanz: Play-Gegenprobe (`rest_adoption`, explorativ) → dieser Job.**
- Letzte echte Play-Lesung: 09.09. (e271cbf) — discovery_gap 0.545 (im Band, PLAN-Ziel-1
  erreicht), snare 19/20 blind / 12/20 menü / 16/20 guided, guided-Decke median 22
  (15–27, full-only 10/20), cord_spear 0/20, session_depth 52.5.
- PLAN.md: alle Tasks `[x]`, nur beobachtende `[~]`-Posten (session_depth 52.5,
  gear_uptime 0.994, forage_pressure 0.0 — alle in Probezeit oder beobachtend).
- Direktor (So 13.09. 18:00) steht bevor — dieser Report speist die Lesung.

---

## Befund-Kern (aus den Pre-Measurement-Probes, deterministisch)

### R1 — `rest_adoption` Erstlesung: **0.333 (p25 0.000, p75 0.500, n=20), unter Band 0.4–0.85**

Bot-Policy (v5, guided-Grundierung aus `play.guided_full._warmup`, HORIZON 500,
20 Scorecard-Seeds 20260803–20260822):

- Trigger 1: behandelte Verletzung → Rast-Fenster bis Heilung (Cap 40 Ticks, Hitz-Guard bt<39.5)
- Trigger 2: Nacht mit aktivem Feuer → Rast durch die Nacht (stoke bei fuel<15,
  Einmal-Versorgung via `_ensure_fire_supply` beim Fenster-Öffnen)
- Tag: Kälte-Guard (bt<34 → Waldrand/Feuer), sonst sammeln

Ergebnisse:

| seed | sc/w | hp_end | tick |
|---|---|---|---|
| 20260803 | 0/2 | 40 (alive) | 325 |
| 20260804 | 1/3 | −2 | 454 |
| 20260805 | 1/2 | −0 | 416 |
| 20260806 | 1/2 | 41 | 335 |
| 20260807 | 1/3 | −2 | 465 |
| 20260808 | 0/3 | −1 | 474 |
| 20260809 | 1/2 | −2 | 419 |
| 20260810 | 1/2 | 28 | 326 |
| 20260811 | 0/2 | −6 | 335 |
| 20260812 | 0/2 | −3 | 321 |
| 20260813 | 1/2 | −2 | 336 |
| 20260814 | 0/2 | −2 | 327 |
| 20260815 | 1/3 | −9 | 451 |
| 20260816 | 0/2 | −2 | 335 |
| 20260817 | 1/2 | −1 | 321 |
| 20260818 | 1/2 | 20 | 373 |
| 20260819 | 0/2 | 27 | 355 |
| 20260820 | 0/2 | 40 | 364 |
| 20260821 | 1/2 | −0 | 327 |
| 20260822 | 0/1 | 40 | 235 |

**Median 0.333 — unter Band (Spec: "Rast kommt nicht an").**

### Der Warumbefund ist präziser als die Zahl: drei Ebenen

1. **Nacht-Fenster scheitern fast immer an der Brennstoff-Ökonomie, nicht an Rast.**
   Der bot rastet nur mit aktivem Feuer (`_resting_warm()`). Die Nacht (54 Ticks ≈
   14 Rests à 4 Fuel + ~8 Stokes à 1 Tick-Burn) braucht ~64 Brennstoff-Ticks. Ein
   start_fire liefert 24, jeder KINDLING-Stoke +8; die Höhlen-Reserve (reeds) hält
   nach dem Warmup nur ~5 Stokes. Ohne VORheriges Sammeln stirbt das Feuer @Rest 5–6
   in der Nacht — und danach ist die Höhle weg (reeds nur dort), die Rast unterm
   kalten Waldrand (nachts effektiv −10+0=5°C eff.) = Unterkühlung-Drain @−1hp/4t.
   Genau die "Mechanik hält, Antwortpfad fehlt"-Klasse: Rast EXISTIERT und funktioniert
   mechanisch einwandfrei (Q3: 10/10 Heilungen in exakt 5 Rests), aber im natürlichen
   Verlauf stirbt der Spieler NACHTS neben dem Feuer, weil 4-Ticks-Rast-Budget und
   KINDLING-Vorrat gegen die 54-Tick-Nacht nicht reichen.
2. **HITZSCHLAG-Kante (neuer Befund, B11-Kandidat):** Rast am Feuer treibt `body_temp`
   über 40.0°C → HITZSCHLAG @−1 hp/Tick. Ohne Unterbrechung rastet der Bot im Feuer
   zu Tode (43 Rests @bt 40.7–43, hp 100→0 bei SATTEM Inventar, warm, Feuer an).
   Ein echter Spieler, der "am Feuer bis zum Morgen ausharren" als Antwort auf den
   Nacht-Bogen lernt, stirbt an der Überhitzung, die er nicht sieht (nur die
   HITZSCHLAG-Zeile). **Das ist ein ehrliches Spiel-Signal, kein Bot-Artefakt**:
   der einzige Wärme-Counter (FIRE_HEAT=40) hat keinen oberen Komfort-Stop.
3. **Heil-Kette über Rast funktioniert einwandfrei** (Q3): behandelte cut 1.0 am
   Feuer heilt in exakt 5 Rast-Zyklen (20 Ticks) in 10/10 Seeds — exakt die
   SPEC-015-Probe ("19–20 Ticks bis verheilt" gilt: severity 1.0 − 0.05·20 = 0).
   Der PFAD existiert; was fehlt, ist die Brennstoff-Dauer für die Nachtachse.

### Scorecard-Erwartung (executing run re-verifiziert gegen Tages-HEAD)

Vor-Scorecard 09.09.: atfc 7.0, reachability 1.0 (11/11), variety 5.0,
skill_spread 0.198, feedback 1.0, content 1.0 (18/18), session_depth 52.5,
gap 0.545, forage 0.0, warmth 0.46, recovery 0.375, gear 0.994.

**Erwartung: alle 12 byte-identisch** (Scorecard-Bots rufen `rest()` nie; Dev hat
das am 10.09. bereits Tages-Probe bestätigt — Determinismus-Vertrag). Der executing
run läuft `tools/scorecard.py` und diffed gegen `scorecard/2026-09-09.json`.

---

## Schritt-für-Schritt (executing run)

### Task 1: Pre-Write-Verifikation (read-only)

- [ ] `cd ~/projects/primal-process && source .venv/bin/activate && python -m pytest -q`
      → Expect: `342 passed, 1 xfailed`. Falls rot: STOP, Fehlerreport, kein Commit.
- [ ] `git log --oneline -1` → Expect `c56e6ff` oder Nachfolger mit nur Play/Dev-Titel.

### Task 2: Scorecard-Echtlesung (der Play-Job's Schreibrecht)

- [ ] `.venv/bin/python tools/scorecard.py` (schreibt `scorecard/2026-09-11.json` +
      `SCORECARD.md`, Δ gegen 09.09.)
- [ ] Diff `scorecard/2026-09-11.json` gegen `scorecard/2026-09-09.json`
      → Expect: byte-identische 12 Werte (Determinismus-Vertrag). Bei Abweichung:
      Stream-Shift-Anatomie (SPEC-009-Klasse), keine Kompensation, Delta-Tabelle
      ins JOURNAL — Tages-Probe gilt.

### Task 3: Play-Report schreiben

`play/2026-09-11.md` — Lead mit dem wichtigsten Befund (Langeweile/Spiel-Signal),
Struktur wie 09.09.: Headline 1 = rest_adoption Erstlesung + Nacht-Bogen-Anatomie
(Brennstoff-Dauer + HITZSCHLAG-Falle), Headline 2 = snare-Bestätigung optional
nicht erneut messen (kein neuer Content seit 09.09.), Werkzeug-Status, Übergabe.

### Task 4: BACKLOG + JOURNAL

- 🔴 **B11 (neu, verifiziert):** Rast am Feuer treibt `body_temp` über 40.0 →
  HITZSCHLAG-Drain @−1hp/Tick ohne Komfort-Obergrenze; "am Feuer ausharren" (die
  nahegelegte Nacht-Antwort) tötet bei langem Ausharren. Fix-Richtung: oberer
  Komfort-Cutoff der Feuer-Wärme (z.B. eff. Ambient cap ~38°C) oder Gleichgewicht
  statt Asymptot-Überhitzung — spiel-seitig, Konstante, kein Metrik-Touch.
- 🟡 (Nachtrag B10): Nacht-Rast braucht ~64 Brennstoff-Ticks; KINDLING-Quellen
  (reeds Höhle-only, tinder via Prozess) tragen das nicht im natürlichen Verlauf —
  Design-Frage an Direktor: Nachlege-Zyklus lesbarer machen (z.B.WOOD-Tag auf
  stick ergänzen wäre Data-Touch → Direktor-Entscheid).
- JOURNAL prepend (Format `## 2026-09-11 — [Play] <title>`, Folgetitel-Regel).

### Task 5: Commit + Push-Verify

```bash
cd ~/projects/primal-process && git add -A && git commit -m "play: scorecard + playtest (cron)" && git push
git status -sb   # Expect: main...origin/main (clean)
git log origin/main..main --oneline   # Expect: leer
```

---

## Files likely to change

- `scorecard/2026-09-11.json` (neu, via scorecard.py)
- `scorecard/latest.json`, `SCORECARD.md` (Delta-Tabelle)
- `play/2026-09-11.md` (neu)
- `BACKLOG.md` (🔴 B11 + B10-Nachtrag)
- `JOURNAL.md` (prepend)

## Tests / Validation

- pytest grün VOR Writes (342 + 1 xfail), nach Writes erneut full-suite.
- Scorecard-Diff: 12 Werte byte-identisch gegen `2026-09-09.json`.
- Probes: alle `/tmp`-Skripte read-only, deterministisch (Doppel-Lauf byte-identisch),
  nach Writes gelöscht.

## Risks / Offene Fragen

- **rest_adoption-Bot-Policy ist Probezeit-Ware:** die 0.333-Erstlesung ist
  Policy-abhängig (guided-Grundierung, stoke<15, 1x-Versorgung). Ein
  fuel-effizienterer Bot (mehrfacher `_ensure_fire_supply`) liest höher — das ist
  gewollte Kalibrierung, kein Tuning (Spec: "Kalibrierung während der Probezeit ist
  erlaubt", offene Frage 3: Fenster 40 Ticks willkürlich). Die Zahl wird als
  **Erstlesung mit dokumentierter Policy** geliefert, nicht als Band-Urteil.
- **HITZSCHLAG-Befund braucht Dev-Bestätigung, ob er als 🔴 Bug oder Balancing-Note
  läuft:** Mechanik-asymptote (fire warmth 40 → bt asymptotiert gegen 55°C eff.) vs.
  Komfort-Band 35–40. Der executing run legt ihn als B11 mit Fix-Richtung ab.
- Kein Spiel-Code, keine Metrik-, kein CONSTITUTION-Kontakt in dieser Session
  (alles read-only + Play-eigene Writes).
