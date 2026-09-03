# Research-Spec-Plan: SPEC-013 Jahreszeiten & Wetterfronten — die flache Zeitachse beenden

> **For Hermes:** Plan-Modus-Lauf (Cron Do 03.09. 2026, `plan`-Skill aktiv — der Plan-Modus gewinnt
> gegen das Execute-Mandat des Cron-Prompts, Präzedenz: Plan-Mode-Lauf 01.09. zu SPEC-012). KEIN
> Commit in diesem Turn, keine Spec-Datei, kein PLAN.md/JOURNAL-Touch. Der nächste Research-Run
> (Metrik-Modus) nimmt diesen Plan als Work-Contract, führt die Staleness-Checks + Go/No-Go-Probe
> aus und schreibt dann genau die hier ausgearbeiteten Artefakte (Spec + Metrik-Proposal +
> PLAN.md-Task + JOURNAL-Eintrag) und committet. EIN Spec, EIN Metrik-Proposal, EIN Commit.

**Goal:** Eine System-Mechanik ohne bestehenden Metrik-Anker: aus dem memoryless-Wetter
(uniform `random.choice` alle 12 Ticks) und dem fehlenden Kalender wird eine Welt mit
Fronten-Trägheit, Jahreszeiten-Zyklus und Vorwarnung — Vorbereitung wird erstmals möglich,
statt akuter Wartung. Beweis über das neue Metrik-Proposal `storm_readiness`, nicht über
Bewegung einer bestehenden Metrik.

**Architecture:** Engine-only Spec — `engine/core.py` (Wetter-Markov-Kette über EIGENEN
`weather_rng`-Strom, Kalender/Saison-Offset in `_get_ambient_temp`, Konstantenblock), `main.py`
(Statuszeile + Prognose-Hinweis), Tests. KEIN Data-Touch (kein items/blueprints/processes/locations),
KEIN Metrik-Core-Touch. Stream-Isolation nach `injuries_rng`-Präzedenz (SPEC-009, BACKLOG 20.08.)
soll alle 12 Metrikwerte byte-identisch halten — Delta-Tabelle trotzdem Pflicht (Regel).

**Tech Stack:** stdlib (`random.Random`-Instanz für weather_rng), pytest, Runtime-Probes via
`PYTHONPATH=.` `python -c` in /tmp (kein Scorecard-File-Write).

---

## Evidence-Basis (Pre-Messung dieses Plan-Modus-Laufs, alle read-only)

| Befund | Quelle |
|---|---|
| Wetter: `self.weather_types` = 4 Zustände (CLEAR/RAIN/STORM/SNOW), `_update_weather` alle 12 Ticks: `random.choice(list(keys))` — uniform, memoryless, KEINE Trägheit, KEINE Fronten | `engine/core.py:209-235` |
| Nacht-Mod existiert (−10°C, `hour = tick_counter % 144 / 6`), aber **kein Tageszähler, keine Saison** — nichts liest die Tageszahl | `engine/core.py:237-244` |
| Spieler-Sichtbarkeit: Statuszeile zeigt nur `Wetter: {current_weather}` als Label — keine Prognose, keine Vorbereitungsmöglichkeit | `main.py:22` |
| Play 01.09.: Tode 12/20 sind die Feuer-Versorgungsspirale (STORM → Feuer ohne Nachschub → FIRE_OUT → bt-Kollaps); Feuer-Ökonomie-Task senkte nur die Symptome (13→12), der strukturelle Grund bleibt: **Wetter kann niemand vorhersehen** | `play/2026-09-02.md` |
| Play 01.09. Kernbefund: Boredom-Punkt ~20 gezielte Aktionen (dritte Lesung: 21.5 → 20 → 20) — „die Welt hat keine Bögen, nur Ticks"; Prozess-Hinweise hoben session_depth (Metrik), nicht die Erschöpfung (Spielgefühl) | `play/2026-09-02.md` Headline |
| Play 14.08.: Kälte ist „Wartungsloop, kein Entdeckungsziel" — Nachlegen alle ~8 Ticks ohne Planungshorizont | `BACKLOG.md` (Ideas) |
| RNG-Strom-Regel: neue Mechanik mit eigenen Würfen braucht EIGENEN Strom, sonst verschieben sich alle Mess-Bots (SPEC-009-Vorfall, guided cook 17/20→8/20) | `BACKLOG.md` 20.08. (Dev) |
| `injuries_rng`-Präzedenz: eigener Kanal aus aktuellem Zustand geseedet → Baseline-Metriken byte-identisch | `engine/core.py:218` (Kommentar) |
| warmth_stability 0.46, p25=p75=0.46 — „Metrik unterscheidet kaum zwischen Seeds", Streuungs-Defizit dokumentiert | `BACKLOG.md` 13.08., Scorecard 02.09. |
| Konstanten-Block existiert (FIRE_HEAT=40.0, START_FIRE_FUEL=24.0, WEAR_*, INJ_*, REST_EXPOSURE=0.15) — dort kommen die Saison-/Front-Konstanten hin | `engine/core.py:41-97` |
| Scorecard-HORIZON = 500 Ticks, Standard-Seeds 20260803+0..19 — Saison-Zyklus (7 Tage = 1008 Ticks) liegt außerhalb des Messfensters; Teilsaison-Effekte (erste 3.5 Tage) innerhalb | `tools/scorecard.py:35-38` |
| Wetter-Ticks pro Mess-Run: HORIZON 500 → ~41 Wetter-Losungen pro Run — Stream-Shift-Risiko real, wenn Weather-Würfe im gemeinsamen Stream bleiben würden | eigene Rechnung |

**Warum GENAU diese Mechanik (Feldbezug, kein Metrik-Zwang):** Constitution nennt „Zeit und
Jahreszeiten, Wetter" ausdrücklich als offenes Feld. Die Play-Reports liefern den System-Befund:
jede Antwort der letzten Wochen (Feuer-Ökonomie, Prozess-Hinweise, Hint-Layer) behandelt
Symptome einer Welt ohne Zeitbogen — Vorbereitung ist strukturell unmöglich, weil Vorwarnung
nicht existiert, und Erinnerung/Saison-Rhythmus existieren nicht. Das ist die selbe
System-Schwäche-Klasse wie SPEC-004 (unendliche Nodes) und SPEC-007 (tote Thermodynamik):
kodiert aber flach, vertieft Entdecken wenn verdrahtet, keine Content-Ballons.

**Nummern-Disziplin:** SPEC-012 (Faserschlinge) ist vom 01.09.-Plan-Mode-Lauf reserviert, aber nie
gelandet (kein `specs/SPEC-012*.md` im Repo) — der ausführende Run muss prüfen, ob SPEC-012
inzwischen existiert. Falls ja: diese Nummer auf SPEC-014 schieben, sonst SPEC-013 verwenden.

---

## Ausgangslage / Staleness-Check (Aufgabe 1 des ausführenden Runs)

Vor jedem Schreiben verifizieren (Lektion SPEC-003/006/012):
1. `git fetch && git log --oneline -5 && git status -sb` — nichts Neues gelandet, das den
   Engine-Stand verschiebt (Head bei Planung: 06bcebe, Gap-Wächter-Reset).
2. `ls specs/` — SPEC-012 noch nicht gelandet? (Nummern-Entscheid oben.)
3. `scorecard/latest.json` + `SCORECARD.md` (02.09.): discovery_gap 0.6 im Band, Probezeiten
   laufen (session_depth bis 08.09., gear_uptime/forage_pressure bis 11.09., recovery bis 03.09.).
   SPEC-013 ist bewusst **kein** Gap-/Band-Hebel — Probezeiten sind kein Blocker, aber die
   Delta-Tabelle muss sie ehren.
4. PLAN.md (02.09.-Fassung): Taskliste leer (alle [x]) — der neue Task ist die erste offene Zeile.
5. **Go/No-Go-Probe (Pflicht, siehe Task 1):** Markov-Wetter mit `weather_rng`-Isolation muss
   `compute_all()` byte-identisch lesen. Kein byte-identisch → kein Spec-Ship in dieser Form
   (Negativ-Protokoll: BACKLOG-Eintrag + Direktor-Flag + JOURNAL, kein Spec gegen die eigene Probe).

## Was der Spec macht (Kurzfassung für die Task-Zeile)

**Mechanik (aus echten Spielen):** Don't Starve — Jahreszeiten als Weltzustand: der Tages-Zähler
macht den Wandel vorhersagbar, erfahrene Spieler bereiten sich VOR der Kälte vor statt im
Moment zu reagieren. Project Zomboid / Stardew Valley — Wetter-Fronten mit Trägheit und
Ankündigung: „Regen zieht auf" erlaubt Planung über den Tag hinaus. Kern: Wetter bekommt einen
Zustandsraum mit Richtung (Fronten), Zeit bekommt einen Kalender (Tageszahl → Saison), und der
Spieler sieht beides im CLI.

---

## Aufgabenliste für den ausführenden Run (bite-sized, in dieser Reihenfolge)

### Task 1: Staleness-Check + Go/No-Go-Probe (read-only)

**Files:** keine (Probes via `/tmp`, Runtime-Wrapper)

**Schritte:**
1. Staleness-Check wie oben (5 Schritte).
2. **Go/No-Go-Probe auf HEAD** — Stream-Isolation verifizieren:
   ```python
   # /tmp/probe_weather_isolation.py — mit gepatchtem core.py (in /tmp-Kopie oder Arbeitstree,
   # NICHT committen): weather_rng = random.Random(); weather_rng.setstate(random.getstate())
   # (exakt das injuries_rng-Muster, core.py:225-226); _update_weather würfelt aus
   # weather_rng statt random.choice. Nur die Front-Wahl, keine weiteren Würfe.
   # Dann: from tools import scorecard as sc; alle 12 Metriken von sc.compute_all()
   # gegen scorecard/2026-09-02.json vergleichen.
   ```
   Erwartung: alle 12 Werte byte-identisch (der gemeinsame `random`-Strom der Mess-Bots bleibt
   unberührt, weil Weather-Würfe aus `weather_rng` kommen).
3. **No-Go-Kriterien** (eins reicht): ein einziger Metrikwert weicht ab · pytest-Regression im
   Arbeitstree. → Kein Spec-Ship in dieser Form: Negativ-Befund in BACKLOG (⚪ Research, mit
   Probe-Tabelle), JOURNAL-Eintrag, Direktor-Flag, Commit der Dokumentation. Plan abhaken mit
   Befund-Zeile.

### Task 2: Spec schreiben — `specs/SPEC-013-jahreszeiten-wetterfronten.md`

**Files:** Create `specs/SPEC-013-jahreszeiten-wetterfronten.md`. Volltext siehe unten
(copy-paste-fertig; nach dem Schreiben Selbst-Lese-Pass auf Sprach-Drift — JOURNAL-Regel 27.08.).
Anti-Deadlock: Spec-File in MEHREREN kleinen write/patch-Schritten aufbauen (je < ~2k Tokens),
nie der komplette Inhalt in einem Call.

### Task 3: Metrik-Proposal schreiben — `metrics/proposed/storm_readiness.md`

**Files:** Create `metrics/proposed/storm_readiness.md`. Volltext siehe unten (copy-paste-fertig,
gleiche Anti-Deadlock-Regel). Ohne dieses File ist der Spec laut Cron-Regel unvollständig.

### Task 4: PLAN.md — Task ergänzen (offen)

**Files:** Modify `PLAN.md`, Tasks-Sektion, als erste offene Zeile (nach dem letzten [x]-Task,
„Gap-Wächter zurücksetzen", vor den [~]-Beobachtungszeilen):

```markdown
- [ ] **SPEC-013 — Jahreszeiten & Wetterfronten: die flache Zeitachse beenden** (Research 03.09.,
      plan-mode-vorbereitet). Befund: Wetter ist memoryless (uniform random.choice alle 12 Ticks,
      keine Trägheit, keine Fronten); es gibt keinen Tageszähler, keine Saison, keine Vorwarnung —
      Vorbereitung ist strukturell unmöglich. Play-Befunde: Tode = Feuer-Versorgungsspirale im
      STORM (Play 01.09.), Kälte ist „Wartungsloop ohne Entdeckungsziel" (Play 14.08.), Boredom-Punkt
      ~20 Aktionen drittlesung stabil — die Welt hat keine Bögen, nur Ticks. Antwort (Engine-only,
      kein Data-Touch): Markov-Wetterfronten über EIGENEN weather_rng-Strom (injuries_rng-Präzedenz),
      Saison-Offset aus Tageszahl in _get_ambient_temp, Wetter-Vorhersage-Log bei Frontwechsel,
      Statuszeile mit Tag/Saison. Neue Metrik: `storm_readiness` (metrics/proposed/) — misst, ob
      Vorbereitung vor Wetter-Fronten im Spiel ankommt. Erwartete bestehende Metrik-Wirkung: KEINE
      (bewusst System-Tiefe, stream-isoliert); warmth_stability-Streuung ist der indirekte
      Beobachtungs-Kandidat. Akzeptanz: compute_all() byte-identisch (Go/No-Go), Wächter 1.0/1.0/1.0,
      pytest grün, Delta-Tabelle im JOURNAL (auch bei Null-Delta), kein Rezept-Leak, CLI bleibt.
```

### Task 5: JOURNAL.md — Eintrag (prepend-without-clobber!)

**Files:** Modify `JOURNAL.md` (Regel 08-24: neuer Eintrag ÜBER dem Top-Header `## 2026-09-02 —
[Dev] Gap-Wächter...`, der alte Header bleibt). Titel:
`## 2026-09-03 — [Research] SPEC-013 Jahreszeiten & Wetterfronten — Plan-Mode-Vorbereitung (stream-isoliert, Probe offen)`
Inhalt: Evidence-Tabelle dieses Plans (kompakt), Go/No-Go-Ergebnis (oder No-Go-Protokoll),
Skip-Log der Metrik-Auswahl (session_depth/gear_uptime/forage_pressure = Probezeit; warmth =
Peters Lesung Beobachtungsgröße; recovery = Probe-Ende 03.09.; discovery_gap = 0.6 im Band,
SPEC-013 ist bewusst KEIN Gap-Hebel), Datum im Titel = Tag der AUSFÜHRUNG.

### Task 6: Verifizieren + Commit + Push

1. `python -m pytest` — grün (285 aktuell; neue Weather-Tests kommen erst mit der
   Implementierung durch Dev — der Research-Run schreibt nur Docs).
2. Selbst-Review-Pass über beide neuen Files (Sprach-Drift, Regel 27.08).
3. `cd ~/projects/primal-process && git add -A && git commit -m "research: explore spec 013 jahreszeiten-wetterfronten + metric-proposal (cron)" && git push`
4. Push verifizieren: `git status -sb` (clean, kein ahead).

---

## Spec-Volltext (Task 2, copy-paste-fertig)

```markdown
# SPEC-013 — Jahreszeiten & Wetterfronten: die flache Zeitachse beenden

**Problem** (System-Schwäche, kein Metrik-Anker — Constitution-Feld „Zeit und Jahreszeiten,
Wetter"): Das Wetter ist **memoryless** — `_update_weather` würfelt alle 12 Ticks uniform aus
4 Zuständen (`engine/core.py:232-235`). Keine Trägheit, keine Fronten, keine Richtung: STORM
kann vier Losungen hintereinander kommen oder nie; nichts kündigt sich an. Dazu fehlt der
Kalender: Nacht existiert (`_get_ambient_temp`, −10°C), aber kein Tag-Zähler, keine Saison,
nichts im Spiel liest die Tageszahl. Die Statuszeile (`main.py:22`) zeigt nur das aktuelle
Wetter-Label — **Vorbereitung ist strukturell unmöglich**, weil Vorwarnung nicht existiert.

System-Befunde aus den Play-Reports: Die 12/20-Baseline-Tode sind die Feuer-Versorgungsspirale
im STORM (Play 01.09.) — niemand kann einen Sturm vorhersehen, also versorgt niemand vorher.
Kälte ist „Wartungsloop, kein Entdeckungsziel" (Play 14.08.) — Nachlegen alle ~8 Ticks ohne
Planungshorizont. Der Boredom-Punkt (~20 gezielte Aktionen, dritte Lesung stabil) liest sich
als „die Welt hat keine Bögen, nur Ticks". Jede bisherige Antwort (Feuer-Ökonomie, Hint-Layer)
behandelt Symptome; die Zeitachse selbst ist flach.

**Mechanik** (Quell-Spiele): Don't Starve — Jahreszeiten als vorhersagbarer Weltzustand:
der Kalender macht den Wandel lesbar, Spieler bereiten sich VOR der Kälte (Vorräte, Kleidung,
Basis) statt im Moment zu reagieren. Project Zomboid / Stardew Valley — Wetter-Fronten mit
Trägheit und Ankündigung („Regen zieht auf"): Fronten halten, kündigen sich an, haben Saison-
Gewichtung. Kern-Effekt: Aus akuter Wartung wird Planung — Zeit bekommt Richtung, Vorbereitung
wird zur Entdeckungs-Ebene (Welche Vorräte? Welcher Ort? Welches Werkzeug?).

**Adaption** (konkret für PPP, Engine-only — kein Data-Touch, kein Metrik-Core-Touch):
Dateien: `engine/core.py`, `main.py`, `tests/test_engine.py`.

1. **Konstanten (`engine/core.py`, Konstantenblock 41-97):**
   ```python
   # SPEC-013: Wetter-Fronten & Jahreszeiten
   DAY_TICKS = 144             # existiert implizit (hour-Formel), jetzt benannt
   SEASON_LENGTH_DAYS = 7      # 1008 Ticks pro Saison
   SEASONS = ("spring", "summer", "autumn", "winter")
   SPRING_TEMP_OFFSET = 0.0    # Start-Saison ist offset-frei (siehe Design-Statement)
   SUMMER_TEMP_OFFSET = 6.0
   AUTUMN_TEMP_OFFSET = -3.0
   WINTER_TEMP_OFFSET = -8.0
   WEATHER_FRONT_MIN = 2       # Front hält mindestens 2 Losungen (24 Ticks = 4h)
   WEATHER_FRONT_MAX = 5
   FRONT_LEAD_LOSSES = 1       # Vorlauf: 1 Losung (12 Ticks ≈ 2h) zwischen Ankündigung und Wirkung
   ```
   Detail-Werte (Offsätze, Front-Dauern, Übergangsgewichte) sind Dev-Balance — der Spec legt das
   System fest (Präzedenz SPEC-007: „Detail-Balance liegt beim Dev während der Umsetzung").

2. **Front-Zustand + eigener RNG-Strom (`GameEngine.__init__`):**
   ```python
   # SPEC-013: Wetter-RNG (EIGENE Strom-Klasse analog injuries_rng, SPEC-009-Präzedenz):
   # Front-Würfe dürfen die Ressourcen-Sequenz der Mess-Bots NICHT verschieben.
   self.weather_rng = random.Random()
   self.weather_rng.setstate(random.getstate())
   self._front_remaining = 0        # verbleibende Losungen der aktuellen Front
   self._pending_forecast = None    # (nachstes_wetter,) — announced, noch nicht wirksam
   ```

3. **Markov-Fronten statt Uniform-Wurf (`_update_weather`):**
   Pro Saison eine Übergangs-Gewichtung (Herbst: RAIN häufig, Winter: SNOW/STORM häufig,
   Sommer: CLEAR dominant — Gewichte als Dict-of-Dicts in `__init__`). Ablauf je Losung:
   a) `_front_remaining > 0` → Front hält, nichts ändert sich (Trägheit).
   b) `_pending_forecast` gesetzt → wird jetzt wirksam (`current_weather = forecast`),
      `_pending_forecast` geräumt, neue Front-Dauer würfeln.
   c) sonst: Nachfolger aus Saison-Matrix würfeln; wenn ≠ aktuell: als Vorwarnung annoncieren
      (Log-Zeile im selben `_advance_time`-Zyklus, generisch: „Der Wind dreht — Regen zieht auf.")
      und `_pending_forecast` setzen; Wirkung tritt erst nach `FRONT_LEAD_LOSSES` ein.
   **Design-Statement (ehrlich, kein Metrik-Schutz-Trick):** Start ist Tag 0 (Frühling, Offset 0);
   mit `SEASON_LENGTH_DAYS = 7` bleiben alle Scorecard-Horizonte (HORIZON 500) im offset-freien
   Frühling. Der Saison-Bogen gehört der Langzeit-Session, nicht dem Mess-Bot — das ist Kalender-
   Semantik (Spiel startet im Frühjahr), kein Band-Tuning.

4. **Kalender (`_get_ambient_temp` + Helfer):**
   ```python
   def _current_season(self) -> str:
       day = self.tick_counter // DAY_TICKS
       return SEASONS[(day // SEASON_LENGTH_DAYS) % len(SEASONS)]
   ```
   `_get_ambient_temp` addiert den Saison-Offset zur bestehenden Formel
   (`loc.base_temp + weather_mod + night_mod + season_offset`). Nacht-Mod bleibt unangetastet.

5. **Vorwarnung im Log (`_advance_time`):** die Ankündigung aus 3c) landet in der bestehenden
   `logs`-Liste (kein neuer Experiment-Reason, EMITTABLE_REASONS unangetastet — Wetter-Ankündigungen
   sind Weltzustand, kein Experiment-Feedback; `feedback_quality` bleibt unberührt, weil der Metrik-
   Pfad Experimente zählt).

6. **Statuszeile (`main.py:22`):** `--- Tag {d} ({Saison}) | Wetter: {W} ---` — Tag/Saison sind
   Weltzustand, keine Rezept-Info; keine zusätzliche Prognose-UI (YAGNI: die Log-Vorwarnung ist der
   Planungshorizont, ein Kalender-UI wäre Content ohne Befund).

7. **Tests (`tests/test_engine.py`):**
   - Front-Trägheit: nach Frontbeginn bleibt das Wetter ≥ `WEATHER_FRONT_MIN` Losungen konstant.
   - Vorlauf-Semantik: Ankündigung erscheint `FRONT_LEAD_LOSSES` Losungen VOR der Wirkung;
     `temp_mod`/`exposure_mod` des Nachfolgers greifen erst mit Wirkung (Kontroll-Lauf: ambient
     im Ankündigungs-Tick noch auf Altwert).
   - Strom-Isolation: fester Seed-Lauf — globaler `random`-Zustand nach N `_advance_time`-Calls
     identisch zu einem Lauf ohne Wetter-Aktivität (weather_rng konsumiert den Hauptstrom nicht).
   - Saison-Progression: Tag 0/7/14/21 → spring/summer/autumn/winter; Winter-Offset −8 liest sich
     in `_get_ambient_temp` (gleicher Ort, gleiches Wetter, gleiche Tageszeit).
   - Reconciliation: bestehender Wetter-Test (`test_engine.py:459-466`) bleibt grün: tick 5
     (`5 % 12 != 0`) löst keinen Update aus → CLEAR hält; tick 12 löst die erste Markov-Losung aus,
     aber die Assertion prüft nur `current_weather in weather_types` — jeder Front-Zustand erfüllt
     das. Init `_front_remaining = 0` erlaubt Wechsel/Ankündigung schon bei der ersten Losung;
     das ist gewollt (Tag-0-Wetter ist erst nach dem ersten Update "gewürfelt").
   - Determinismus: zwei Engines aus identischem Seed-Zustand spielen identische Wetter-Sequenz.

**Akzeptanzkriterien** (jedes verifizierbar):
1. Wetter wechselt nicht mehr uniform-tickweise: Fronten halten ≥ `WEATHER_FRONT_MIN` Losungen;
   zwei gleiche Wetter hintereinander sind die Norm, kein Zufall.
2. Vorwarnung existiert und hat Vorlauf: belastende Übergänge (→ RAIN/STORM/SNOW) werden genau
   `FRONT_LEAD_LOSSES` Losungen vorher als Log-Zeile annonciert, generisch, ohne Rezept-/Ort-Leak.
3. Kalender existiert: Tag + Saison sind ableitbar, in der Statuszeile sichtbar; Winter ist bei
   sonst gleichen Bedingungen 8°C kälter als Neutral.
4. **`compute_all()` byte-identisch gegen `scorecard/2026-09-02.json`** (Go/No-Go, alle 12 Werte) —
   die weather_rng-Isolation trägt; Delta-Tabelle trotzdem vollständig im JOURNAL (Regel).
5. `blueprint_reachability`/`content_reachable`/`feedback_quality` = 1.0 (Wächter; kein Data-Touch
   impliziert das, aber gemessen wird trotzdem).
6. `python -m pytest` grün inkl. neuer Tests (Liste oben); bestehender Wetter-Test reconciliert.
7. CLI bleibt Textinterface (Statuszeile erweitert, nicht ersetzt); kein Rezept-Leak.

**Erwartete Metrik-Wirkung** (Primär: **keine bestehende Metrik** — bewusst, wie SPEC-004/007):
- `compute_all()` byte-identisch (Kriterium 4) — alle 12 Werte unverändert. Das ist die ehrliche
  Behauptung: kein Mess-Bot liest Vorwarnungen, alle Policies bleiben stur — die System-Wirkung
  (Vorbereitung) liegt außerhalb der Bot-Welt. Deshalb existiert das Metrik-Proposal unten.
- `warmth_stability` (0.46, flach, p25=p75): Sekundär-Kandidat nach Peters Freigabe — Saisons
  bündeln Kälte saisonal statt uniform, was das dokumentierte Streuungs-Defizit (BACKLOG 13.08.)
  adressieren KÖNNTE. Aber ehrlich: im Messfenster (500 Ticks, Frühling, offset-frei) bleibt sie
  unverändert; die Streuungs-Wirkung entsteht erst, wenn ein (freigegebener) Runner Saisons läuft.
- `session_depth`/`gear_uptime`/`forage_pressure` (Probezeiten bis 08.09./11.09.): unberührt,
  byte-identisch. `discovery_gap` (0.6, Bandkante): unberührt — kein Content, kein Selektions-Hebel.

**Constitution-Check:** Tag-Crafting unangetastet, kein Rezeptbuch/Leak (Wetter-Ankündigung ist
Weltzustand, keine Kombinatorik-Info), CLI bleibt, stdlib only (`random.Random`), keine Metrik
entfernt/umdefiniert/abgeschwächt — METRICS/Metrik-Core unangetastet, neues METRICS-Entry nur nach
Peters Freigabe (deshalb Proposal-File, kein Scorecard-Code). Vertieft Entdecken: Vorbereitung
wird zur neuen Entscheidungsschicht (Vorwarnung lesen → Ressourcen mobilisieren → vor Wirkung
antworten); nichts wird abgekürzt.
```

---

## Metrik-Proposal-Volltext (Task 3, copy-paste-fertig)

```markdown
# Proposed Metric: `storm_readiness`

> Research-Proposal, 2026-09-03 (zu SPEC-013 „Jahreszeiten & Wetterfronten").
> Falls angenommen (Direktor/Dev nach Constitution: Metriken dürfen **ergänzt** werden):
> Eintrag in `METRICS` mit `"probation_until"` = +14 Tage; Band-Spekulation während der
> Probezeit ist beobachtend, kein Plan-Ziel.

## Name

`storm_readiness` (v1)

## Was sie erfasst

Ob die neue Vorwarnung-Ebene tatsächlich **ankommt**: Reagiert ein Akteur, der
Wetter-Ankündigungen liest, im Vorlauf-Fenster mit Vorbereitung (Brennstoff-Reserve,
aktives Feuer) — und hält die Vorbereitung bis zum Front-Eintritt? Sie misst die
**Vorbereitungs-Achse vor dem Einschlag**, nicht das Wärme-Outcome selbst.

Gegenstück: `warmth_stability` misst das Outcome (warm überstanden), aber NICHT, ob der
Weg dorthin über Vorwarnung + Planung lief. Ohne diese Metrik wäre SPEC-013 unsichtbar:
die Scorecard-Bots lesen keine Logzeilen, die Mechanik würde von keiner bestehenden Zahl
berührt — genau die Blende, die das Cron-Mandat („jeder Spec braucht einen Metrik-Vorschlag")
schließt.

## Definition (Präzision)

Front-Event: jeder annoncierte belastende Übergang (→ RAIN, STORM, SNOW) mit Vorlauf-Fenster
(`FRONT_LEAD_LOSSES × 12` Ticks zwischen Ankündigungs-Logzeile und Wirksamkeit).

Outcome zum Wirksam-Tick des Events:
```python
prepared = (loc.fire_active and loc.fire_fuel >= WEATHER_FRONT_MIN * 12) \
           or player.inventory.get_total_insulation() >= 0.3
```
(Beide Pfade sind legitime Antworten — Feuer hüten oder Isolation tragen; der Feuer-Pfad ist
der primitive Standard, die Isolation der Aufwertungs-Pfad aus SPEC-007.)

```
storm_readiness(seed) = (# Front-Events mit prepared=true) / (# Front-Events)
Wert                  = Median über Standard-Seedsatz (n=20), Policy wie v2-Bots
```

Events ohne Vorlauf-Fenster (Front hält und läuft aus ohne Nachfolger) zählen nicht.

## Berechnungsskizze (Determinismus-Konventionen wie scorecard.py)

Policy-Bot (lesend, seedfest): Standard-Sammel-Loop; nach jeder `_advance_time`-Rückgabe die
Logzeilen parsen (Ankündigungsmuster). Bei Ankündigung: bis zum Wirksam-Tick Brennstoff-Loop
(gather KINDLING/WOOD-Quelle, `stoke_fire`) — sofern Feuer/Quelle erreichbar; sonst weiter,
Event zählt als unprepared. Eigenes RNG: keiner — der Bot konsumiert den Engine-Stream
deterministisch wie die v2-Runner; KEINE neuen globalen Würfe.

```python
def run_storm_readiness(seed):
    random.seed(seed)
    e = GameEngine()
    events = prepared = 0
    pending = None  # (effective_tick,)
    while e.tick_counter < HORIZON:
        logs = e.gather() or []
        pending = _scan_announcement(logs, e) or pending   # Ankündigung erkannt?
        if pending and e.tick_counter >= pending:
            events += 1
            loc = e.current_location
            if (loc.fire_active and loc.fire_fuel >= WEATHER_FRONT_MIN * 12) \
               or e.player.inventory.get_total_insulation() >= 0.3:
                prepared += 1
            pending = None
        if e.player.energy < 150:
            _eat_best(e)
        _respond_or_gather(e, pending)   # bei pending: Brennstoff-Loop, sonst gather
    return prepared / events if events else None
```

Median über Standard-Seeds; Ausgabe analog warmth/recovery (value + p25/p75 + n_runs + Bandlage).
Keine Events (frühling-stabile Fronten über den ganzen Horizont) → None, wie andere Band-Metriken.

## Richtung/Band

**Band [0.3, 0.8], keine Richtung** (Bandmetrik).

- **Unter 0.3:** Vorbereitung kommt nicht an — Vorlauf zu kurz, Brennstoff unerreichbar
  (SPEC-004-Regen-Limits), Ankündigung unlesbar. Mechanik existiert, aber nutzlos.
- **Über 0.8:** Vorbereitung trivial — Vorlauf zu lang oder Brennstoff gratis; keine
  Entscheidungs-Spannung mehr, reine Routine.
- **Zielband:** Vorbereitung lohnt und kostet — der Vorlauf-Fenster-Entscheid (sammeln vs.
  etwas anderes) ist real. Kalibriert gegen den lesenden Bot, der VORBEREITET, aber nicht
  perfekt plant (keine Vorratsoptimierung über mehrere Fronten).

## Warum nicht trivial hebbar

1. Heben heißt: die ganze Kette muss funktionieren — Ankündigung im Log sichtbar, Vorlauf
   lang genug, Brennstoff im Fenster erreichbar (regen-limierte Nodes, SPEC-004), Feuer
   gebaut und gefüttert (SPEC-007). Jede schwache Stelle drückt die Zahl.
2. spam-gather hebt sie nicht: Outcome zählt den Zustand ZUM Wirksam-Tick — wer vorher
   Brennstoff sammelt, aber das Feuer nicht am Stück hält (FIRE_OUT), verliert das Event.
3. **Keine Avoidance-Lücke** (bekanntes gear_uptime-Loch): Wetter ist global — kein
   Location-Wechsel entzieht sich der Front. Der einzige Ausweg ist echte Vorbereitung.
4. Metric-Tuning ist verfassungs-blockiert; Spiel-seitig "lösen" (Brennstoff fluten) würde
   zwar heben, aber das ist der gewollte Lernpfad — die Band-Obergrenze (0.8) fängt die
   Gratis-Variante ab.
```

---

## Files likely to change (beim ausführenden Run)

- Create: `specs/SPEC-013-jahreszeiten-wetterfronten.md` (Task 2)
- Create: `metrics/proposed/storm_readiness.md` (Task 3)
- Modify: `PLAN.md` (Task 4 — eine offene Task-Zeile)
- Modify: `JOURNAL.md` (Task 5 — Eintrag prepend-without-clobber)
- KEIN Touch: `engine/`, `data/`, `tools/scorecard.py`, `main.py`, `tests/` — alles das ist
  Dev-Arbeit gegen den Spec. Der Research-Run committet nur Dokumente.
- Falls No-Go: stattdessen BACKLOG.md (Negativ-Befund) + JOURNAL.md.

## Tests / Verifikation (Implementierungs-Phase, Dev — aus dem Spec)

- Unit: Front-Trägheit (≥ MIN Losungen konstant), Vorlauf-Semantik (Ankündigung vor Wirkung,
  alte temp/exposure-Mods bis zum Wirksam-Tick), Strom-Isolation (globaler random-Zustand
  unverändert), Saison-Progression (Tag 0/7/14/21), Winter-Offset −8 in `_get_ambient_temp`,
  Determinismus (gleicher Seed → gleiche Wetter-Sequenz).
- Go/No-Go (bereits Task 1 des ausführenden Runs): `compute_all()` byte-identisch.
- Wächter: reachability/content/feedback 1.0/1.0/1.0.
- pytest vollständig grün; bestehender Wetter-Test (`test_engine.py:459-466`) reconciliert.

## Risiken / Tradeoffs / offene Fragen

1. **Wetter-Semantik-Shift ist Spielinhalt:** Fronten machen STORM seltener-pro-Event aber
   länger — die Kälte-Druck-Struktur ändert sich für ECHTE Spieler (nicht für Mess-Bots, die
   byte-identisch bleiben). Das ist gewollt (Wartungsloop → Planung), aber der Direktor sollte
   es als Spielgefühl-Änderung lesen, nicht als Neutrale-Refactor. Play-Job wird das in der
   nächsten echten Session sehen.
2. **Saison-Bogen liegt außerhalb des Messfensters:** HORIZON 500 < 1008-Tick-Saison. Die
   Saison-Mechanik ist für Mess-Bots dead code — nur Vorwarnung/Fronten sind im Fenster sichtbar.
   Ehrlich benannt im Spec (Design-Statement); falls Peter später Saisons im Scorecard-Fenster
   will, ist das ein Metrik-Core-Eingriff (nur mit Freigabe).
3. **weather_rng-Seed-Basis:** `setstate(random.getstate())` kopiert den Zustand am
   `__init__`-Zeitpunkt — bei scorecard-Seeding (`random.seed(seed)` vor `GameEngine()`) ist
   das deterministisch pro Seed. Gleiches Muster wie injuries_rng, aber die Wechselwirkung
   (injuries_rng UND weather_rng konsumieren beide Kopien desselben Ausgangszustands) muss im
   Go/No-Go-Probe-Test explizit gelesen werden — zwei Streams vom selben Snapshot sind
   unabhängig, aber ihre Draws fallen nicht deterministisch ineinander. Kein Fehler, nur
   Dokumentation wert.
4. **Ankündigungs-Logzeile als Vertrag:** `storm_readiness` parst Logzeilen. Wenn Dev das
   Ankündigungs-Format später ändert, bricht die Metrik still — deshalb steht das Muster
   im Spec (generischer Satz, „Der Wind dreht …"), und die Metrik-Definition verweist darauf.
   Langfristig sauberer wäre ein Maschinenfeld (z. B. `e.forecast`), das der Spec bewusst als
   öffentliches Attribut mitliefert (`_pending_forecast` ist bereits lesbar) — die Skizze nutzt
   Log-Parse primär, Engine-Attribut als Fallback.
5. **Go/No-Go-Regel gilt tagesaktuell:** Liest die Probe auf dann-HEAD anders (z. B. nach einem
   Dev-Commit zwischen Planung und Ausführung), gilt die Tages-Probe, nicht dieser Plan-Text —
   der Plan ist die Methode, nicht das Ergebnis (Präzedenz 01.09.-Plan, Risiko 5).

## Remember (für den ausführenden Run)

```
Staleness-Check zuerst (Nummern-Disziplin SPEC-012/013!)
Go/No-Go: compute_all() byte-identisch — sonst No-Go-Protokoll
EIN Spec, EIN Metrik-Proposal, EIN PLAN-Task, EIN JOURNAL-Eintrag, EIN Commit
Anti-Deadlock: Files in kleinen Schritten bauen (< ~2k Tokens pro Call)
JOURNAL prepend-without-clobber, Datum = Ausführungstag
```


