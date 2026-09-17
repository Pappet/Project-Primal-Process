# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.
> Stand: 2026-09-13, Lesung = Scorecard 11.09. (identisch 09.09.).

## Aktueller Zustand

Alle 12 Metriken ±0 gegen 09.09. — dritte byte-identische Lesung in Folge; die
Wächter halten (reachability 1.0, 11/11 · content 1.0, 18/18 · feedback 1.0),
`discovery_gap` 0.545 sitzt in der Bandmitte (naive_rate 0.455, snare verifiziert
19/20 im simpelsten Profil). Das Spiel ist an einer neuen Stelle warm geworden:
SPEC-015 (Rast) ist mechanisch einwandfrei gelandet (Heil-Kette 10/10 in exakt
5 Rast-Zyklen, `compute_all` 12× byte-identisch, 342 Tests grün) — aber der
Nacht-Bogen tötet auf zwei Arten: die Brennstoff-Ökonomie trägt keine Nacht
(~64 Fuel-Ticks vs. ~5 Höhlen-Stokes), und Rast am satten Feuer überhitzt
tödlich (B11: 19/20 Tode, `body_temp` > 40 ohne Komfort-Stop). Zwei
Probezeiten sind 11.09. abgelaufen (gear_uptime, forage_pressure) und werden
in dieser Lesung entschieden; sharpen_tool bleibt 0/20 (5. Lesung in Folge).

## Was als nächstes besser werden muss

1. **Der Nacht-Bogen muss überlebbar sein — durch die Antwortpfade, nicht durch
   Gnade.** Metriken: `warmth_stability` (0.460 → Band-Mitte; siehe
   Probezeit-Entscheid unten — ohne Reform liest er keine Nacht-Rast, deshalb
   ist der zweite Lesepfad `rest_adoption` nach Probe-Ende 24.09.),
   `recovery_stability` (0.375, Heil-Kette über Rast muss im natürlichen Verlauf
   nutzbar bleiben). Konkret: (a) B11-Komfort-Cutoff landen (kein 19/20-Tod am
   selben Wärme-Counter mehr), (b) Nachlege-Dauer lesbar machen — das Spiel
   muss die Frage „womit halte ich ein Feuer über Nacht?" beantwortbar
   machen. Erwartung: keine Scorecard-Verschiebung außer der dokumentierten
   B11-Öffnung (HITZSCHLAG stirbt im Messfenster nie — Bot rastet nie); der
   Nachweis läuft über Play (Rest-Loop-Tode → 0/20, Nacht-Fenster-Erfolg).

2. **rest_adoption in die Messung nehmen — die neue Zeit-Achse ohne Blende.** ✅
   aufgenommen (Dev 16.09., Nachcommit des abgebrochenen Laufs;
   Direktor-Freigabe 13.09.): `probation_until` 2026-09-24 unverändert,
   Erstlesung auf Tages-HEAD nach T1+T2 = **1.0** (flach p25=p75; über der
   Band-Obergrenze 0.85 — Kalibrierungs-Ware, Band-Lesung nach Probe-Ende;
   JOURNAL 15.09. inkl. Pflicht-Delta-Tabelle: 12 Alt-Metriken
   byte-identisch). Scorecard-Bots rufen `rest()` nie — ohne diese Metrik
   ist SPEC-015 unsichtbar. Nach Probe-Ende (24.09.) darf sie Plan-Ziel
   werden; bis dahin beobachtend.

3. **Die Wächter halten durch jede Nacht-Bogen-Änderung.** Metriken:
   `blueprint_reachability` 1.0 (11/11), `content_reachable` 1.0 (18/18),
   `feedback_quality` 1.0, `discovery_gap` bleibt im Band (0.2–0.6).
   Der Data-Entscheid in T2 berührt `items.json` (ein Tag); der Probe-Vertrag
   der 31.08.-Präzedenz gilt: vollständige `compute_all()`-Delta-Tabelle im
   JOURNAL, Stream-Shift dokumentiert, nicht kompensiert.

## Tasks

> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.
> T1 vor T2 (Work-Contract regelt Reihenfolge und getrennte Commits).

- [ ] **SPEC-016 — Glut: der Feuerort erinnert sich (Ortsbindung als Welt-Gedächtnis)** —
      offen (Research-Explore 17.09., wartet auf Direktor-Triage).
      **Problem:** FIRE_OUT löscht den Feuerort byte-identisch mit Neuland — die Welt hat
      kein Gedächtnis für die Arbeit des Spielers; Ortsbindung existiert strukturell nicht
      (Constitution-Felder „Terrain und Ortsbindung"/„Basisbau" unbesetzt). Der 28.08.-
      Befund (Reparatur nach Kollaps strikt schlechter, 19/20 vs. 12/20) zeigt das Loch:
      der *eine* Ort, an dem der Spieler schon alles beisammen hatte, bewertet als
      Jungfrau-Terrain. `fire_pit` (KINDLING, wird nie verbrannt) ist der stille Beleg
      der Design-Absicht „Feuerstelle als Ort".
      **Mechanik:** URW-Lagerfeuer-Glut + Don't-Starve-Remains + TLD-Fire-Spots — FIRE_OUT
      hinterlässt Glut (`LocationDef.embers`), Re-Zündung am Glut-Ort braucht nur WOOD
      (nicht tinder+stick), Glut verfällt (0.1/Tick, ~60-Ticks-Fenster), unter
      EMBER_REVIVE_MIN ist der Ort wieder Neuland. Mechanik-Kern: ein Zähler, zwei
      Verzweigungen (FIRE_OUT-Setzung in `_advance_time`, Verzweigung in `stoke_fire`),
      drei Konstanten. Kein Data-Touch, keine neuen RNG-Würfe, start_fire-Kette unangetastet.
      **Akzeptanz:** Glut nur aus FIRE_OUT; Revive braucht WOOD + Glut ≥ MIN (tinder
      ausdrücklich nicht nötig — Gegenprobe); Glut-Fenster endlich (~60 Ticks); keine
      neuen Draws (getstate-Assertion); Wächter 1.0/1.0/1.0 + vollständige Delta-Tabelle
      im JOURNAL (Erwartung 13× byte-identisch, Tages-Probe gilt, SPEC-013-Präzedenz);
      pytest grün (+tests/test_embers.py); keine neue Reason-Klasse; Constitution-Check
      in der Spec-Datei. Details: specs/SPEC-016-glut-ortbindung.md.
      Metrik-Proposal: metrics/proposed/fire_home_loyalty.md (Band 0.3–0.8, Bot liest
      die Rückkehr-Achse mit unvollkommener Feuer-Policy — erste Metrik, die eine
      Welt-Eigenschaft statt einer Bot-Policy liest).
      **Erwartete Metrik-Wirkung:** alle 13 bestehenden byte-identisch (Bots berühren
      den Glut-Pfad nie); Nachweis über das Proposal nach Direktor-Freigabe.
      **Priorität: ab T3** (hinter den offenen Probezeit-Entscheiden; Design-Skizze
      vor TDD wie T1-Präzedenz).

- [x] **T1 — B11: Feuer-Komfort-Cutoff (HITZSCHLAG-Falle)** ✅ 14.09. (Dev-Lauf):
      `FIRE_COMFORT_CAP = 38.0` gewired an `fire_warmth > 0` in `_advance_time`
      (engine/core.py). Rest-Loop-Regression: **0/20 Tode** (war 20/20 @Rest#34,
      bt 43.3), bt pendelt 36.7–37.6 im Komfortfenster, Kälte-Seite unberührt
      (Zwei-Fälle-Test verankert), keine neuen RNG-Würfe (getstate-Assertion),
      352 Tests grün (+10 test_fire_comfort_cap.py). Metriken: 11× byte-identisch,
      `warmth_stability` 0.460 → 0.440 (in Band 0.4–0.9) — **dokumentierter,
      nicht kompensierter Stream-Effekt** (das B11-Fix selbst liest durch die
      einzige am-Feuer-lebende Metrik; Delta-Tabelle + Ursachen-Lesung im
      JOURNAL 14.09.). Play-Gegenprobe → Play-Job (Rest-Loop-Tode → 0/20,
      Nacht-Fenster-Erfolg). Details: JOURNAL 14.09., play/2026-09-11.md,
      BACKLOG B11.
      **Priorität: 1.** Play 11.09. verifiziert (Play-Probe + unabhängige
      Dev-Re-Produktion: 19/20 Tode im puren Rest-Loop am 500-fuel-Feuer,
      Rest#33–57, bt_end 40.0–42.5, alle 20 Scorecard-Seeds): FIRE_HEAT=40
      hat keinen oberen Komfort-Stop — effektive Ambient-Temperatur am Feuer
      liegt > 40, `body_temp` asymptotiert darüber, HITZSCHLAG zieht
      −1 hp/Tick ohne Unterbrechung bis zum Tod. „Am Feuer ausharren" ist DIE
      nahegelegte Antwort auf den Nacht-Bogen (SPEC-015) und tötet bei langem
      Ausharren — der Spieler sieht nur die HITZSCHLAG-Zeile, kein
      richtungsgebendes Signal vorher (gleiches Muster wie B10 vor SPEC-014).
      **Antwort (Engine-only, Konstante):** oberer Komfort-Cutoff der
      Feuer-Wärme — am aktiven Feuer wird `effective_ambient` auf
      `FIRE_COMFORT_CAP = 38.0` gecappt:
      `effective_ambient = min(effective_ambient, FIRE_COMFORT_CAP)`, gewired
      an `fire_warmth > 0` (d. h. am Feuer aktiv). Begründung 38.0: unter der
      HITZSCHLAG-Grenze 40.0, über der Kälte-Schwelle 35.0 — bt pendelt am
      Feuer im Komfortfenster statt gegen > 40 zu asymptotieren. OHNE Feuer
      kein Cap (Kälte-Physik unangetastet — exakt diese Zwei-Fälle-Trennung
      testet der „Cap greift nur am Feuer"-Test). Wirkt
      rein über die bestehende `_advance_time`-Wärmezeile (core.py:332-337) —
      kein neuer RNG-Wurf, kein Data-Touch, kein Reason-Code-Eingriff. Die
      UNTERKÜHLUNG-Seite bleibt unberührt (Kälte-Drift unter 35.0 bleibt
      tödlich ehrlich). Bewusst NICHT: zusätzliches Warn-Event (erst lesen,
      ob der Cutoff die Falle trägt — Meldungen sind die SPEC-014-Klasse,
      nicht die erste Wahl gegen eine physikalische Überhitzung).
      **Akzeptanz:** Rest-Loop-Regressionstest (500-fuel-Feuer, 60 Rasten,
      20 Scorecard-Seeds): 0/20 HITZSCHLAG-Tode; `body_temp` pendelt im
      Komfortfenster (kein untoter Zustand — Wärme-Gewinn endet unter der
      40.0-Grenze); Kälte-Seite unberührt (bestehende
      tests/test_cold_hints.py + tests/test_rest.py bleiben grün und
      aussagekräftig: Nacht ohne Feuer friert weiterhin); keine neuen
      RNG-Würfe (getstate-Assertion); vollständige `compute_all()`-Delta-
      Tabelle im JOURNAL — Erwartung alle 12 byte-identisch (Scorecard-Bots
      rasten nicht, SPEC-015-Präzedenz 10.09.); pytest grün; Design-Skizze
      (1 Absatz im JOURNAL) vor TDD; kein Touch an data/*.json,
      EMITTABLE_REASONS, scorecard.py; kein Rezept-Leak (Konstante ohne Text).
      Details: play/2026-09-11.md, BACKLOG B11.

- [x] **T2 — Direktor-Entscheid B10-Nacht-Ökonomie: `stick` → +WOOD (Data-Touch), verworfen: Tier-2-Anschluss-Andeutung** ✅ 15.09.
      (Dev-Lauf, Nachcommit des abgebrochenen Laufs): `stick` trägt
      `WOOD` (data/items.json, ein Tag); 365 Tests grün (+13
      test_stick_fuel.py: Data-Touch auf Template+Instanz-Ebene, stoke mit
      stick (+8/quantity--), Präferenz-Reihenfolge WOOD vor KINDLING,
      fire_pit nie, Zünd-Kette unangetastet, kein Blueprint-Slot matcht
      WOOD); Wächter 1.0 (11/11 bzw. 18/18), feedback_quality 1.0;
      compute_all-Delta exakt `warmth_stability` 0.44→0.72 (im Band 0.4–0.9,
      Stream-Shift dokumentiert, nicht kompensiert — Delta-Tabelle JOURNAL
      15.09.).
      **Priorität: 2 (Dependency: T1 gelandet).** Befund-Cluster (Play
      07.09./09.09./11.09.): die Nacht braucht ~64 Brennstoff-Ticks (14 Rests
      à 4 + ~8 Stokes à 1); ein `start_fire` liefert 24, jeder
      KINDLING-Stoke +8; KINDLING-Quellen sind reeds (hidden_cave-only) und
      tinder (Prozess-Output) — beide tragen die Dauer im natürlichen Verlauf
      nicht; das Feuer stirbt @Rest 5–6, danach ist die Höhle weg und die
      Rast unterm kalten Waldrand = UNTERKÜHLUNG-Drain. Gleichzeitig liegt
      `log_oak` (RIGID+WOOD, forest_edge, CHOPPING/Axt) als quasi-
      unerschöpflicher WOOD-Fuel-Pfad in der Welt — aber der Ast, das
      naheliegendste „Holz", trägt das Tag nicht: die Assoziation
      „Ast = Brennstoff" scheitert an einer stillen Datenlücke, nicht an
      einem Design-Wunsch. **Entscheid (Direktor, 13.09.): GO für den
      Data-Touch** — `stick` bekommt `"WOOD": true` (data/items.json, ein
      Tag, ein String). Spiel-Logik: ein Ast ist Holz; der WOOD-Fuel-Pfad
      über `_find_fuel_item` existiert bereits (stoke_fire mit stick →
      STOKE_FUEL = 8 Ticks, quantity--; sticks sind 12/20 naiv sammelbar);
      die Nacht wird zur planbaren Brennstoff-Beschaffungs-Entscheidung
      („vor der Nacht Sticks sammeln") statt zum Zufalls-Todesurteil. Das
      vertieft das Entdecken (Brennstoff-Ökonomie als learnbares Muster,
      B10-Klasse), es kürzt nichts ab — kein Rezept, kein Leak, die
      Zünd-Kette und tinder/reeds-Feinheit bleibt. **Verworfen:**
      Tier-2-Anschluss-Andeutung an der rope-Discovery (BACKLOG 07.09.) —
      sharpen_tool-Präzedenz: 5 Lesungen in Folge 0/20 (zuletzt 09.09.), die
      Mechanik trägt nicht, bevor der Antwortpfad existiert; Eingriff, ohne
      dass die Grund-Mechanik sichtbar ist, ist Reihenfolge-falsch.
      **Akzeptanz (für den ausführenden Dev-Lauf):** die eine Tag-Änderung in
      data/items.json; Wächter `blueprint_reachability` 1.0 (11/11),
      `content_reachable` 1.0 (18/18 — stick ist schon Template, kein neuer
      Eintrag), `feedback_quality` 1.0; vollständige `compute_all()`-Delta-
      Tabelle im JOURNAL — Stream-Shift dokumentiert, NICHT kompensiert
      (31.08.-Präzedenz Munitions-Ökonomie; Dev-Tages-Probe gilt: tages-
      frische Baseline via `PYTHONPATH=. .venv/bin/python -c "from tools
      import scorecard as sc; ..."` (compute_all() als Inline-Probe, /tmp-
      Write only — NIE tools/scorecard.py als __main__, das ist der Play-Write),
      Diff-Tabelle vor/nach); pytest grün inkl. angepasster
      Fuel-Tests (stoke mit stick, `_find_fuel_item`-Präferenz-Reihenfolge
      — WOOD vor KINDLING, fire_pit nie); Play-Gegenprobe → Play-Job
      (Nacht-Fenster-Erfolgsrate, explorativ, kein harter Gate — kein
      Overfitting am Mess-Bot); Blueprint-Touch-Gefahr explizit prüfen:
      keine Blueprint-Slots matchen bislang WOOD — falls ein Blueprint-Delta
      auftaucht, Go/No-Go neu bewerten (Probelauf vor dem Ship entscheidet).

- [x] **SPEC-015 — Rast: Zeit als investierbare Ressource** ✅ 10.09.
      (Dev-Lauf): gelandet — `rest()`-Verb (REST_TICKS=4, REST_EFFORT=0.4),
      Menü `[r]asten`, alle Systeme durch den bestehenden Tick-Pfad.
      Go/No-Go: alle 12 Metriken byte-identisch (Delta-Tabelle JOURNAL
      10.09.), 342 Tests grün (+22 test_rest.py), CLI-Smoke verifiziert.
      Play-Erstlesung 11.09.: rest_adoption 0.333 (Heil-Kette 10/10 in
      exakt 5 Rast-Zyklen; Nacht-Fenster scheitern an der Brennstoff-Ökonomie
      — → T2; HITZSCHLAG-Falle — → T1).

- [x] **SPEC-014 — Feuer-Wartung lesbar machen** ✅ 08.09.: Kälte-Warnung
      (bt < 36.0, nur ohne aktives Feuer) + Feuer-schwach (fire_fuel < 8.0)
      als Crossing-Meldungen in `_advance_time`; alle 12 Metriken
      byte-identisch, 320 Tests grün (+12). Play-Gegenprobe 09.09.:
      Mechanik hält (722 cold_events/20 Seeds, kein Spam, Fire-Gate) —
      „Mechanik hält, Antwortpfad fehlt" → B10/T2 (Design-Frage
      „warmes Rückzugsziel vs. Feuer" durch T2-GO beantwortet: der
      Brennstoff-Pfad ist die Antwort, kein neuer Text).

- [x] **Ziel-2-Hebel: Wear-Warnung als richtungsgebende Andeutung** ✅
      07.09. gelandet (WEAR_HINT_TEXT, core.py), 08.09. adoptiert (19e1f01).
      Play-Lesung: sharpen_tool weiterhin 0/20 (5. Lesung in Folge, 09.09. —
      Koinzidenz Worn-Tool + Flint fällt im natürlichen Verlauf nie).
      Beobachtungsposten, kein aktives Ziel: die Andeutung ist im Text,
      die Koinzidenz ist ein Design-Loch, kein Text-Bug.

- [x] **SPEC-012 — Faserschlinge** ✅ 07.09.: snare {FIBER, EDIBLE},
      data-only; gap 0.600 → 0.545 (≤ 0.55), naive_rate 0.400 → 0.455,
      17/20 craften ihn; 305 Tests grün (+16). Verifiziert in Play 09.09.
      (19/20 im simpelsten Profil, früh @20).

- [~] *(beobachtend)* **gear_uptime (v1)** — Probezeit 11.09. ABGELAUFEN.
      Lesung 13.09.: 0.994 über Band (0.7–0.95), p25=p75 flach — die Zahl
      misst weiterhin die Unsichtbarkeit von Attrition, nicht ein
      Spiel-Gefühl: der Scorecard-Bot hält nie Instandhaltung, 5 Lesungen
      sharpen_tool 0/20 (Koinzidenz-Loch, xfail verankert). Metrik bleibt
      an, kein Plan-Ziel — solange der Mess-Bot die Gegenmechanik nie
      berührt, liest er nur seine eigene Policy (warmth/recovery-Flachheit,
      gleiche strukturelle Ursache). Erneute Bewertung, wenn der Wear-Pfad
      im natürlichen Verlauf erlebbar wird; bis dahin dokumentiert
      unbewertet. Umdeutung/Band-Anpassung = Peters Freigabe (Metrik-Kern).
- [~] *(beobachtend)* **forage_pressure (v2)** — Probezeit 11.09.
      ABGELAUFEN. Lesung 13.09.: 0.000 unter Band (0.1–0.5), p75 0.03 —
      strukturell: der Scorecard-Bot läuft vor Erschöpfung tot (UNTERKÜHLUNG,
      ~119 Ticks) und erlebt Knappheit nie; Depletion-Regen ist zu schnell
      relativ zur Bot-Lebensdauer. Beobachtungsgröße, kein Plan-Ziel: die
      Band-Unterschreitung ist ein Policy-Artefakt, kein verifiziertes
      Spiel-Signal. Erneute Bewertung, wenn ein Lesepfad die
      Erschöpfungszone erreicht (Menü-Naiv-Profil im Play-Repo wäre der
      erste Schritt dahin). Band/Definition-Anpassung = Peters Freigabe.
- [~] *(beobachtend)* **session_depth (v2)** — Probezeit 08.09. abgelaufen,
      Lesung 06.09.: 52.5, Struktur unverändert (Mess-Bot erreicht die
      Erschöpfung an ~20 gezielten Aktionen; der Bot-Pfad kauft die 52.5
      mit Stream-Crossings, nicht mit neuer Entdeckung). Erschöpfungslesung
      im Play-Report bleibt die Kompass-Nadel (~20 gezielte Aktionen,
      Menü-Profil ~110). Beobachtungsgröße, kein Plan-Ziel.
- [~] *(beobachtend)* **recovery_stability (v1)** — Probe beendet 03.09.,
      Peters Lesung steht aus. 0.375 im Band, p25=p75 (deterministische
      Policy). Mit T1/T2 wird die Heil-Kette über Rast erstmalig im
      natürlichen Verlauf anwendbar — Neu-Lesung danach, nicht vorher.
- [~] *(beobachtend)* **warmth_stability (v1)** — Probe beendet 27.08.,
      Peters Lesung: Beobachtungsgröße. 0.46 im Band, flach (liest
      guided-Stil-Bot, nie Nacht-Rast). Nach T1/T2 (Play-Gegenprobe
      Nacht-Fenster) Neu-Bewertung; bleibt bis dahin ohne Ziel.
- [~] *(beobachtend, neu nach Probe-Ende 24.09.)* **rest_adoption** —
      Erstlesung 0.333 (unter Band 0.4–0.85), p25 0.000/p75 0.500. Die
      Zahl liest die zwei toten Nacht-Antworten (Brennstoff-Dauer → T2,
      HITZSCHLAG → T1), nicht eine tote Rast-Mechanik. Aufnahme in METRICS
      mit `probation_until` 2026-09-24 (Proposal verifiziert,
      metrics/proposed/rest_adoption.md); Plan-Ziel erst nach Probe-Ende.
- [x] *(erledigt, Vorwochen)* SPEC-011, B08, Munitions-Ökonomie,
      Prozess-Hinweise, Feuer-Ökonomie, Messwerkzeug-Fix, SPEC-013
      (verworfen, NO-GO — Stream-Shift-Präzedenz) — Details: JOURNAL
      28.08.–11.09., PLAN-Historie (git).

---

*Scorecard-Lesung: nächster Play-Job (Mo 14.09. 09:00). Plan-Neufassung:
nächster Direktor (So 20.09. 18:00).*
