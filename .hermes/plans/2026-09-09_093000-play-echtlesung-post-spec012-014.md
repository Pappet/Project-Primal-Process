# Play-Echtlesung post-SPEC-012/014 — Ausführungsplan (Plan-Mode-Pre-Measurement)

> **Für Hermes:** Play-Job-Ausführung mit subagent-driven-development oder direkt — die
> sanktionierten Writes (Scorecard-Dateien, `play/2026-09-09.md`, JOURNAL, BACKLOG, Commit)
> macht der ausführende Lauf. Dieser Plan ist der Pre-Measurement-Vertrag: alle Zahlen
> unten sind auf Tages-HEAD e271cbf, 320 passed + 1 xfailed, gemessen.

**Goal:** Erste offizielle Scorecard-Lesung nach SPEC-012 (snare, 07.09.) + SPEC-014
(Kälte/Brennstoff-Hinweise, 08.09.) landen; die Play-Akzeptanzen beider Specs gegenprüfen.

**Architecture:** Scorecard-Run (`tools/scorecard.py`) → erwartete Werte stehen hier schon
fest (Determinismus); die eigentliche Erkenntnis liegt in den Runs: snare-Rate in den
naiven Profilen, SPEC-014-Hinweis-Wirkung (deaf vs. reader vs. retreat), guided-Erschöpfung.

**Tech Stack:** `.venv/bin/python`, `tools/scorecard.py`, `play/guided_full.py`, /tmp-Probes
(read-only, vor dem Scorecard-Write nichts ins Repo).

---

## Vorbefund: die Zahlen sind schon bekannt (Pre-Measurement, inline compute_all)

Alle 12 Metriken auf Tages-HEAD — exakt die Dev-Probe-Prognose von 07.09. (SPEC-012
Go/No-Go, Dokumentation: PLAN.md Task SPEC-012 + JOURNAL 07.09.):

| Metrik | Vorwoche (07.09.) | Heute erwartet | Status |
|---|---|---|---|
| actions_to_first_craft | 9.5 | **7.0** | Stream-Shift (dokumentiert), besser |
| blueprint_reachability | 1.0 | **1.0** | Wächter hält (jetzt 11/11) |
| craft_variety | 5.0 | **5.0** | unverändert |
| skill_spread | 0.202 | **0.198** | Stream-Shift, minimal |
| feedback_quality | 1.0 | **1.0** | Wächter hält |
| content_reachable | 1.0 (18/18) | **1.0 (18/18)** | Wächter hält (snare Blueprint-only) |
| session_depth | 63.0 | **52.5** | Stream-Shift (dokumentiert 07.09.), Probe-Ende 08.09. → Direktor |
| discovery_gap | 0.600 | **0.545** | PLAN-Ziel 1 erreicht (≤ 0.55, Band 0.2–0.6) |
| naive_rate / naive_p25 | 0.400 / 0.3 | **0.455 / 0.364** | der eigentliche Gap-Gewinn |
| forage_pressure | 0.0 | **0.0** | beobachtend (Probe bis 11.09.) |
| warmth_stability | 0.46 | **0.46** | unverändert |
| recovery_stability | 0.375 | **0.375** | unverändert |
| gear_uptime | 0.994 | **0.994** | über Band (Probe bis 11.09.) |

Scorecard-Write sollte byte-identisch diese Tabelle liefern. Abweichung = Staleness
(prüfen: `git log` zwischen Messzeitpunkt und e271cbf) → abbrechen und neu lesen.

## Run-Befunde (Pre-Measurement, /tmp-Probes, 20 Scorecard-Seeds)

### 1. snare im Spiel (SPEC-012-Akzeptanz, Play-Seite)

- **Blind-Profil (60 Aktionen, nur 2er):** snare **19/20**, Median @ Aktion 20.
  Der tote Selektionsraum (EDIBLE, FIBER) ist real besetzt — der snare ist für den
  simpelsten Spieler das am frühesten gefundene neue Objekt.
- **Menü-Profil (80 Aktionen):** snare **12/20**, Median @ 19. Tode 18/20 (mein
  Profil isst anders als das Vorwochen-Profil — Bots nicht 1:1 vergleichbar, nur die
  snare-Rate zählt hier).
- **Guided (survival-sound):** snare **16/20**, volle Decke (11 bps) 10/20,
  Erschöpfung median **22** (full-only 15–27) — vs. ~20–21.5 vor snare. Der snare
  schiebt die guided-Decke um ~1–2 Aktionen (slotet mid-chain, Skill-Prognose).
- Session_depth-Metrik-Bot liest den snare implizit (52.5-Lesung).

### 2. SPEC-014 Gegenprobe — der zentrale Befund (Plan-Akzeptanz: "Kälte-Tode < 20/20, explorativ")

Menü-Profil C (200 Aktionen), drei Reaktionspolitiken auf die Hinweise:

| Politik | Tode | Tod median | Detail |
|---|---|---|---|
| deaf (liest Hinweis nicht) | 20/20 | @97.5 | bt 0.9–29.6, Vorwochen-Baseline bestätigt |
| reader (Feuer-Versuch am Ort) | 20/20 | **@76** | 722 cold_events, 166 fire_events |
| retreat (Rückzug zum warmen Ort) | 20/20 | @83 | fires_lit: **2** in 20 Seeds |

**Der Hinweis feuert zuverlässig (722×), ist ehrlich — und rettet niemanden.** Der
grund, warum die Vorwochen-Kälte-Tode nicht unter 20/20 fallen, ist nicht mehr
Unsichtbarkeit (B10 ist damit teilweise adressiert: die Meldung existiert und
beschreibt die Richtung), sondern **Ökonomie + Reihenfolge**: (a) ein naiver Spieler
besitzt `start_fire` fast nie, wenn die erste Kälte-Warnung kommt (Prozess-Discovery
landet median später als der erste Crossing); (b) ohne gelerntes Nachlege-Muster
verlöscht jedes Feuer; (c) der Sammel-Loop am kalten Ort (reader) ist **schlechter**
als Ignorieren — die Meldung schickt den Spieler in den Tod, wenn er sie wörtlich
nimmt und am kalten Ort Brennstoff sucht, statt zum warmen Ort zurückzugehen.

Das ist die Langeweile-/Frust-Stelle dieser Woche: **Die Warnung ist da, aber der
erste legale Antwortpfad (Feuer entzünden) ist für den naiven Spieler im
Kälte-Moment meist noch nicht entdeckt.** Die Meldung benennt "ein Feuer" — nicht
"warm bleiben" oder "zurück zum warmen Ort". Ein retreat-orientierter Text wäre
ehrlicher für Spieler ohne start_fire-Wissen (Design-Frage → Direktor).

### 3. Details für den Play-Report

- Guided-Bot: 13/20 alive, 7 hängen am 400er-Cap (Discovery voll, dann Grind —
  wie gehabt; kein neues Signal).
- rope im Blind-Profil 7/20, cord_spear **0/20** überall — Tier-2-Strang bleibt tot
  (BACKLOG 07.09.-Idee unverändert; snare ändert daran nichts: 2er-Slot, kein 3er).
- `scripts/playtest_driver.py` existiert nicht mehr (Skill-Referenz stale) — nur
  `play/guided_full.py` ist da.

## Ausführungsschritte (sanktionierte Writes, ausführender Lauf)

1. **Staleness-Check:** `git log --oneline -3` == e271cbf-Serie? pytest grün?
   Sonst: Zahlen dieser Tabelle neu lesen, Plan-Expectations anpassen.
2. **Scorecard-Write:** `.venv/bin/python tools/scorecard.py` → erzeugt
   `scorecard/2026-09-09.json` + aktualisiert `SCORECARD.md` (Δ gegen 07.09.).
   Erwartete Deltas: gap 0.600→0.545, atfc 9.5→7.0, session_depth 63.0→52.5,
   skill_spread 0.202→0.198, Rest ±0. Wächter 1.0/1.0/1.0.
3. **Play-Report** `play/2026-09-09.md`: Headline = SPEC-014-Gegenprobe (Hinweis
   ehrlich + reichlich, aber 20/20 Kälte-Tode in ALLEN Politiken; die Meldung
   schickt wörtliche Leser in den kalten Sammel-Loop = schlechter als Ignorieren).
   Zweite Headline: snare 19/20 im Blind-Profil — der Gap-Gewinn ist real im Spiel
   angekommen, nicht nur in der Metrik. guided-Erschöpfung 22 (5. Lesung).
4. **BACKLOG:** (a) B10-Nachtrag/Updgrade-Klasse: "Kälte-Warnung (SPEC-014) feuert
   korrekt, aber ohne gelerntes start_fire führt jede wörtliche Befolgung in den
   Tod (reader 76 < deaf 97.5 Median-Tod); fires_lit 2/20 beim retreat-Spieler" —
   Design-Frage: Hinweis-Text Richtung "warmes Rückzugsziel" vs. "Feuer"? (b) 🔵
   Menü-Profil-Skripte erneut nur in /tmp — das 07.09er-BL-Idea (drittes Standard-
   Profil ins Repo) gilt unverändert weiter.
5. **JOURNAL** `## 2026-09-09 — [Play] …` (prepend-without-clobber: Folgetitel
   `## 2026-09-08 — [Dev] …` vollständig in old_string UND new_string).
6. **Commit:** `git add -A && git commit -m "play: scorecard + playtest (cron)" && git push`
   + Push-Verify (`git status -sb` clean, `git log origin/main..main` leer).
7. **Aufräumen:** /tmp-Probes löschen (`/tmp/probe_snare_profiles.py`,
   `/tmp/probe_cold_reader.py`, `/tmp/probe_cold_retreat.py`,
   `/tmp/premeasure_metrics.json`).

## Constitution-Check

- Kein Metrik-Touch, keine Scorecard-Dateien vor dem offiziellen Write, keine
  Engine-/Data-Änderungen. Probes liefen read-only auf Tages-HEAD.
- Der Design-Vorschlag (Hinweis-Text-Richtung) ist spiel-seitig, keine Rezept-Leak-
  Klasse, kein Reason-Code-Eingriff — → Direktor-Triage, kein Dev-Autosh Ship.

## Risiken / offene Fragen

- Meine Menü-Bots sind Neuimplementierungen (Vorwochen-/tmp-Skripte weg) — die
  Todes-/Erschöpfungs-Medians sind NICHT 1:1 mit 07.09. vergleichbar; nur
  qualitative Vergleiche (snare-Rate, Politiken-Ordnung) ziehen. Der Report muss
  das benennen.
- Die SPEC-014-Akzeptanz ("Kälte-Tode < 20/20") ist als explorativer Zielwert
  markiert — die Probe liefert 20/20 in allen Politiken. Ehrlich als
  "Mechanik hält, Spieler-Antwortpfad fehlt noch" reporten, nicht als Fehlschlag
  der Meldung selbst.
