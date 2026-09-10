# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.
> Stand: 2026-09-06, Lesung = Scorecard 04.09. (identisch 02.09.).

## Aktueller Zustand

Die Wächter halten alle: `blueprint_reachability` 1.0, `content_reachable` 1.0 (18/18),
`feedback_quality` 1.0, `discovery_gap` 0.600 (zwei Play-Lesungen bestätigt, Wächter-Tests
auf ≤ 0.60 verschärft, 06bcebe) — aber am Wert sitzt die obere Bandkante, getragen von
Hint-Layern, nicht von neuer Entdeckungstiefe. Die Erschöpfungslesung (echter
Boredom-Punkt) bleibt dritte Lesung in Folge bei ~20 gezielten Aktionen; `session_depth` 63.0
ist v2-Re-Baseline in Probezeit (bis 08.09.), nicht Spielgefühl. Gear_uptime 0.994
(über Band, Probe bis 11.09.) ist zusammen mit sharpen_tool 0/20 inzwischen ein
verifiziertes Spiel-Signal, kein Mess-Bug mehr: die SPEC-011-Gegenmechanik ist für
Spieler praktisch unentdeckbar. Alle Landungen vom 31.08.–04.09. (B08, Munition,
Prozess-Hinweise, Feuer-Ökonomie, Messwerkzeug-Fix) sind stabil; 289 Tests grün.

## Was als nächstes besser werden muss

1. **Discovery-Gap von der Bandkante in die Bandmitte — mit neuem Content, nicht mit
   mehr Hint-Layer.** Metrik: `discovery_gap` (0.600 → ≤ 0.55; Band 0.2–0.6 unverändert).
   Befund Research 01.09. (Probe P1–P4): der Gap ist selektionsgebunden, nicht
   survivalgebunden — der größte tote naive Selektionsraum ist (EDIBLE, FIBER)/
   (EDIBLE, RIGID), kein Blueprint besetzt ihn. Ein `snare`-Blueprint {FIBER, EDIBLE}
   las 0.600 → 0.545 (17/20 Seeds, naive_rate 0.4 → 0.455), probe-verifiziert.
   Keine Band-Schrauben, kein Tuning an der Messung — die neue Zutatenklasse
   „Essbares als Material" vertieft das Entdecken (Constitution).

2. **Die Gegenmechanik von SPEC-011 für Spieler erreichbar machen.** Spiel-Signal
   (kein Plan-Ziel, Metrik in Probezeit bis 11.09.): sharpen_tool ist 0/20 — die
   Koinzidenz Worn-Tool + Flint fällt im natürlichen Verlauf nie zusammen (BACKLOG
   🔵 02.09./04.09., ⚪ 04.09.). Antwort spiel-seitig, gleiche Klasse wie 13.08.
   („Extrem-Kälte hat keine richtungsgebende Andeutung"): die Wear-Warnung muss eine
   generische, richtungsgebende Andeutung tragen (z. B. dass sich Werkzeug mit
   hartem Stein nachschärfen ließe) — kein Rezept-Leak, kein Reason-Code-Eingriff,
   feedback_quality-Kern unangetastet. Ziel: die Gegenmechanik wird im natürlichen
   Verlauf wenigstens einmal erlebbar (Play-Lesung), nicht 0/20.

3. **Kein neuer Content verschiebt die Wächter.** Metriken: `blueprint_reachability`
   = 1.0 (dann 11/11), `content_reachable` = 1.0 (18/18), `feedback_quality` = 1.0.
   Der snare greift in Blueprints ein und das Ziel-2-Signal in die Engine — bei jedem
   Eingriff: Probe vor dem Ship (Go/No-Go), vollständige compute_all()-Delta-Tabelle
   im JOURNAL, RNG-Strom-Klasse benennen. Stream-Shift wird dokumentiert, nicht
   kompensiert (Präzedenz Munitions-Ökonomie 31.08.).

## Tasks

> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.

- [x] **SPEC-012 — Faserschlinge: die toten 2-Slot-Selektionsräume besetzen**
      ✅ 07.09. (Dev-Lauf): Go/No-Go auf Tages-HEAD **GO** — gap 0.600 → **0.545** (≤ 0.55),
      naive_rate 0.400 → 0.455, snare 17/20, Tode unverändert 19/20, reachability 1.0 (11/11),
      content_reachable 1.0 (18/18), feedback_quality 1.0; alle übrigen 8 Metriken byte-identisch
      (4 Stream-Shifts dokumentiert: atfc 9.5→7.0, session_depth 63.0→52.5, skill_spread 0.202→0.198,
      gap = Ziel); 305 Tests grün (+16 snare-Tests, Zähler 10→11 reconciliert). Delta-Tabelle:
      JOURNAL 07.09. Eine Korrektur gegen den Work-Contract: engine-true liest (reeds, stick) →
      **spear** (nicht rope — galt schon vor SPEC-012, von snare unberührt); der echte rope-Fall
      ist (plant_fiber, stick). Beide Schatten testverankert (tests/test_snare.py).
      (Research-Plan 01.09., probe-verifiziert; Work-Contract:
      `.hermes/plans/2026-09-01_104324-research-spec012-faserschlinge.md`).
      Befund: Der Gap ist selektionsgebunden, nicht survivalgebunden (Proben:
      immortal-Bot identisch 0.400, Tode 19/20, Discovery-Plateau @86.5 vor Tod @119).
      Der größte tote naive Selektionsraum ist (EDIBLE, FIBER)/(EDIBLE, RIGID) —
      kein Blueprint besetzt ihn. Antwort: `snare` {loop: FIBER, bait: EDIBLE},
      ungated, tool_tags [PROJECTILE] → Jagd-Alternative zur endlichen Pebble-Munition
      (31.08.-Pfad, data-only: `data/blueprints.json` +1 Eintrag am Array-Ende,
      kein Engine-Touch). Probe 01.09.: naive_rate 0.400 → 0.455, gap 0.600 → 0.545
      (im Band), 17/20 Seeds craften ihn (Median Aktion 36).
      **Akzeptanz:** Staleness-Check (nichts Neues, das die Prämissen verschiebt);
      Go/No-Go-Probe auf Tages-HEAD ≤ 0.55 (Tages-Probe gilt, nicht P4 — Plan-Regel);
      `blueprint_reachability` 1.0 (11/11) und `content_reachable` 1.0 (18/18 — snare
      ist Blueprint-only, KEIN items.json-Eintrag, sonst content_reachable-Regression
      wie SPEC-008); Shadowing-Tests ((stick, stick)→spear; (reeds, stick) ab
      survival 0.4→rope; snare nie verdrängt); Jagd-Verbrauch: raw_meat-Ernte mit
      Schlinge → quantity-- pro Erfolg + Meldung, kein Stack-Wear (31.08.-Pfad);
      EDIBLE-Slot material-agnostisch ((plant_fiber, berries) und (reeds, raw_meat)
      craften beide); pytest grün (inkl. Zähler-Reconciliation test_engine/test_loader
      10 → 11); vollständige Delta-Tabelle im JOURNAL (Stream-Shift dokumentiert,
      nicht kompensiert); session_depth-Lesung als Re-Baseline-Shift markieren
      (Probe bis 08.09. — Wert beobachtend, kein Tuning); kein Rezept-Leak.

- [x] **SPEC-014 — Feuer-Wartung lesbar machen: Kälte- und Brennstoff-Signale**
      ✅ 08.09. (Dev-Lauf): gelandet — COLD_WARN_THRESHOLD 36.0 / FIRE_LOW_FUEL 8.0,
      Crossing-basiert in `_advance_time` (Kälte nur ohne aktives Feuer + Guard ≥ 35.0
      gegen UNTERKÜHLUNG-Doppel; Feuer-schwach nur bei fuel > 0 — im FIRE_OUT-Tick
      keine Lüge). Konstanten, keine neuen Würfe: **alle 12 Metriken byte-identisch**
      (Delta-Tabelle JOURNAL 08.09.), feedback_quality 1.0, EMITTABLE_REASONS
      unangetastet, kein Touch an data/*.json, PROCESS_HINT_CATEGORY, scorecard.py.
      320 Tests grün (+12 test_cold_hints.py: Crossing/No-Spam/Fire-Gate/Rearm/Leak/
      Konstanten-Vertrag). Design-Skizze: JOURNAL 08.09. Play-Gegenprobe (Profil-C-
      Kälte-Tode < 20/20, [w]-Nutzung) → Play-Job (Akzeptanz 8, explorativ).
      (B10, 20/20 Kälte-Tode im Menü-Profil 07.09.; Spec von Research 08.09.,
      self-reviewed). Befund: stoke_fire ist als
      Wartungs-Verb unsichtbar — kein Prozess, keine Hinweis-Kategorie, kein
      Knowledge-Eintrag; der Spieler stirbt neben sammelbarem Brennstoff, weil er kein
      Muster für „Feuer braucht dauerhaftes Nachlegen" lernen kann. Antwort spiel-seitig,
      exakt die Ziel-2-Klasse (Wear-Andeutung): Crossing-basierte, generische
      richtungsgebende Meldungen in `_advance_time` — Kälte-Warnung (bt < 36.0, kein
      aktives Feuer) und Feuer-schwach (fire_fuel < 8.0 bei aktivem Feuer). Konstanten,
      keine RNG-Würfe, kein Leak (nur die bekannte TAG_LABELS-Vokabelklasse), kein
      Reason-Code-Eingriff, kein Daten-Touch. Bewusst NICHT: stoke_fire als
      Pseudo-Prozess (Schema kann WOOD/KINDLING-„irgendein Item" nicht ausdrücken).
      **Akzeptanz:** Crossing-Tests (einmal pro Durchgang, kein Spam, Fire-Gate);
      Leak-frei-Regressionstests; compute_all()-Delta-Tabelle: alle 12 Metriken
      byte-identisch (keine neuen Würfe — Bots reagieren nicht auf Log-Zeilen);
      feedback_quality 1.0 unverändert, EMITTABLE_REASONS unangetastet; pytest grün;
      Play-Gegenprobe danach: Profil-C-Kälte-Tode < 20/20 (Zielwert explorativ, kein
      harter Gate — kein Overfitting am Profil-Bot); Design-Skizze (1 Absatz im
      JOURNAL) vor TDD; kein Touch an data/*.json, PROCESS_HINT_CATEGORY,
      scorecard.py.

- [x] **Ziel-2-Hebel: Wear-Warnung als richtungsgebende Andeutung** — ✅ gelandet
      07.09. (WEAR_HINT_TEXT an der Crossing-Warnung, core.py:419-425), committet mit
      Research-Adoption 08.09. (19e1f01; 2 flaky Tests deterministisch gefixt, 308 grün,
      JOURNAL-Nachtrag 08.09.). Play-Lesung (Koinzidenz Worn-Tool+Flint ≥ 1× im
      guided-Verlauf) → Play-Job. Keine Freigabe nötig, aber Mechanik-Design sauber halten. Befund (Play 04.09., verifiziert):
      sharpen_tool 0/20 — Spieler erleben die Wear-Warnung (Crossing 0.25) ohne Flint
      im Inventar und halten Flint ohne Wear; der Instandhalten-Hinweis (31.08.)
      feuert erst, wenn das Werkzeug schon unter der Warnschwelle ist. Antwort
      spiel-seitig: die Wear-Warnung (SPEC-011-B) bekommt eine generische
      richtungsgebende Andeutung, dass sich Werkzeug mit hartem Material nachschärfen
      ließe — kein Item-/Prozess-Name, kein Rezept-Leak, kein neuer Reason-Code,
      keine neuen RNG-Würfe (Konstante, nicht Wurf). Erst Design-Skizze (1 Absatz
      im JOURNAL), dann TDD.
      **Akzeptanz:** Warn-Text trägt die Andeutung ohne Leak (Text-Regressionstest);
      `feedback_quality` unverändert 1.0 (Warnung ist kein Experiment-Pfad);
      `compute_all()`-Delta-Tabelle im JOURNAL (alle 12 identisch — es gibt keinen
      Grund, dass sich irgendetwas an den Bot-Sequenzen verschiebt); pytest grün;
      Play-Lesung danach: die Koinzidenz Worn-Tool+Flint wird im natürlichen
      guided-Verlauf ≥ 1× erlebbar (Sweep-Dokumentation; Zielwert explorativ, kein
      harter Gate-Wert — kein Overfitting am Mess-Bot).

- [ ] **SPEC-015 — Rast: Zeit als investierbare Ressource** (Research 10.09., explorativ,
      probe-verifiziert). Befund: Die Welt tickt, aber der Spieler kann Ticken nicht gewähren —
      es gibt kein Verb, das Zeit ohne Arbeit verstreichen lässt (CLI main.py:26 hat kein Rast);
      die SPEC-009-Heil-Kette (`treated + _resting_warm()`) wird im natürlichen Verlauf nie
      als Entscheidung erfüllt (Probe: 0/10 naive Bots behandeln jemals; guided heilt
      "nebenbei" nach 19 gathers), die Nacht (~41% der Ticks, bt 37→19.99 nach einem Tag
      Waldrand) ist unbeantwortbar, die Energie-Decke (~240 Ticks optimal) bestraft jede
      Zeiteinheit mit Arbeits-Kosten (gather = Effort 2.0 + Draws + Wear + Verletzungsrisiko).
      Antwort (Engine-only, kein Data-Touch): `rest()`-Verb in engine/core.py —
      `_advance_time(REST_TICKS=4, effort 0.4)`, keine neuen RNG-Würfe (nur bestehende
      %-12-Crossings), Menü `[r]asten` in main.py; alle Systeme (Feuer, SPEC-014-Warnungen,
      Heilung, Node-Regen, Wetter) laufen durch den bestehenden Tick-Pfad. Kein Sleep-Skip,
      kein Energie-Regen, kein Auto-Heal (Abgrenzungen im Spec). Neue Metrik:
      `rest_adoption` (metrics/proposed/) — Rast-Fenster mit Outcome (Heilung vollendet /
      Nacht warm überstanden). Erwartete bestehende Metrik-Wirkung: KEINE (Scorecard-Bots
      rufen rest() nie; Go/No-Go: compute_all() byte-identisch gegen 2026-09-09 — Tages-Probe
      gilt, SPEC-013-Präzedenz bei Abweichung). Akzeptanz: rest-Ticks/Effort-Vertrag,
      Heil-Kette über Rast (am Feuer ja, ohne Feuer nein), FIRE_OUT/UNTERKÜHLUNG während
      Rast ehrlich, keine-Draws-Assertion, Wächter 1.0/1.0/1.0, pytest grün, Delta-Tabelle
      im JOURNAL (auch bei Null-Delta), kein Rezept-Leak, CLI bleibt.
- [~] *(beobachtend, Probe bis 08.09.)* **session_depth** (v2) — 63.0 Re-Baseline
      (Prozess-Hinweise lassen den v2-Bot tiefer laufen), Metrik-Nadel ~3.2× über dem
      echten Discovery-Cap (~20 gezielte Aktionen). Erstes Ziel-Handling beim
      nächsten Direktor nach Probe-Ende; echte Erschöpfungsllesung bleibt die
      Kompass-Nadel, nicht die Metrik.
- [~] *(beobachtend, Probe bis 11.09.)* **gear_uptime** (v1) — 0.994 über Band,
      Erstlesung = dokumentierte Unsichtbarkeit von Attrition. Wird erst nach
      Ziel-2-Hebel + snare erneut gelesen; Bewertung nach Probe-Ende, nicht vorher.
- [~] *(beobachtend, Probe bis 11.09.)* **forage_pressure** (v2) — 0.0 unter Band,
      Re-Baseline der Neudefinition. Band-Entscheid nach Probezeit, nicht vorher.
- [~] *(beobachtend)* **recovery_stability** (v1) — Probe 03.09. beendet, Peters
      Lesung steht aus. 0.375 im Band, p25=p75 (deterministische Policy) — Dev-Notiz
      20.08.: Streuung oder Band-Bewertung nach Probezeit prüfen. Beobachtungsgröße,
      kein Plan-Ziel.
- [~] *(beobachtend)* **warmth_stability** (v1) — Probe 27.08. beendet, Peters
      Lesung: Beobachtungsgröße. 0.46 im Band, flach.
- [x] *(erledigt, Vorwoche)* SPEC-011, B08, Munitions-Ökonomie, Ziel-2-Hebel
      (Prozess-Hinweise), Gap-Wächter-Reset, Feuer-Ökonomie, Play-Messwerkzeug-Fix
      (Re-Entrancy-Guard + 2b-Gate, 1c/1d zurückgerollt) — Details: JOURNAL
      30.08.–04.09., PLAN vom 30.08. (git-Historie).

---

*Naechste Scorecard-Kontrolle: naechster Play-Job (Mo 07.09. 09:00). Plan-Neufassung:
naechster Direktor (So 13.09. 18:00).*
