# B10/B11 Nacht-Bogen: T1 (Komfort-Cutoff) + T2 (stick → WOOD) — Dev-Work-Contract

> Direktor 2026-09-13 18:00, Lesung = Scorecard 11.09. (alle 12 ±0, Wächter 1.0/1.0/1.0, gap 0.545).
> Grenze: CONSTITUTION.md. Play-Job und Messung (`tools/scorecard.py`, `METRICS`,
> Scorecard-Dateien) sind unantastbar — Dev führt KEINEN Scorecard-Write aus;
> tages-frische Baseline via `python tools/scorecard.py --dry-run`-equivalent
> (Scorecard-Tools nur LESEN/berechnen, Writes nach /tmp).
> pytest nur mit Repo-.venv: `source ~/projects/primal-process/.venv/bin/activate` VOR python.

## Abhängigkeits-Regel

**T1 zuerst, vollständig landen, committen — dann T2 anfassen.** T1 ist
Engine-only, T2 ist Data-Touch; nie mischen. Nach T1-Landung: tages-frische
Baseline NEU ziehen (T1 kann theoretisch Wärme-Pfade verschieben —
Delta-Tabelle von T1 sagt dir, ob; Erwartung: identisch).

## Task 1 — B11: Feuer-Komfort-Cutoff (HITZSCHLAG-Falle)

**Befund** (play/2026-09-11.md, doppelt verifiziert — Play-Probe + Dev-Re-Produktion):
`FIRE_HEAT = 40.0` (engine/core.py:42) hat keinen oberen Komfort-Stop. Am aktiven
Feuer ist `effective_ambient = ambient + 40` (core.py:332); `temp_loss =
(bt − effective_ambient) * 0.01 * exposure * (1 − min(0.9, insulation))`
(core.py:335). Für bt < effective_ambient ist temp_loss NEGATIV → bt steigt
asymptotisch gegen effective_ambient. Ist eff. Ambient > 40.0 (z. B. Wald-Tag
~21 + 40 = 61, aber auch kalte Nacht, wenn Feuer + Isolation genügen), pendelt
bt über die 40.0-Grenze → `elif bt > 40.0: hp −= 1.0` (core.py:355-357,
HITZSCHLAG). Re-Produktion: 19/20 Tode im puren Rest-Loop am 500-fuel-Feuer
(Rest#33–57, bt_end 40.0–42.5, 20 Scorecard-Seeds). „Am Feuer ausharren" ist die
nahegelegte Antwort auf den Nacht-Bogen (SPEC-015) und tötet. Der Spieler sieht
vorher KEIN richtungsgebendes Signal — nur die HITZSCHLAG-Zeile.

**Antwort (Engine-only, Konstante):** oberer Komfort-Cutoff der Feuer-Wärme.
`effective_ambient` NICHT über einen Komfort-Sockel hinaus treiben, wenn Feuer
aktiv ist:

```python
FIRE_COMFORT_CAP = 38.0   # engine/core.py, Konstantenblock nach START_FIRE_FUEL
# core.py:332, wenn Feuer aktiv (loc.fire_active and loc.fire_fuel > 0):
effective_ambient = min(effective_ambient, FIRE_COMFORT_CAP)
```

- Begründung 38.0: unter der HITZSCHLAG-Grenze 40.0, über der Kälte-Schwelle
  35.0 — bt pendelt am Feuer im Komfortfenster statt gegen 61 zu asymptotieren.
  Das Feuer ist damit „gemütlich, nicht tödlich" — das exponierte Wetter draußen
  bleibt unverändert unbequem (Cap greift NUR am Feuer; mountain_peak-Extremkälte
  ohne Feuer bleibt tödlich ehrlich).
- WICHTIG, exakt lesen: der Cap greift nur im Feuer-Fall. `effective_ambient`
  bei `fire_warmth == 0` bleibt unangetastet (kein Cap ohne Feuer — sonst
  verschiebst du die gesamte Kälte-Physik).
- Wiring: fire_warmth bleibt für die Isolation/Insulation-Formel wie sie ist —
  NUR die temp_loss-Zeile liest den gecappten Wert. Falls du merkst, dass der
  Cap sauberer an `fire_warmth` selbst hängt (fire_warmth = min(...)), entscheide
  im Design-Schritt und begründe in der Skizze — beide Formen sind akzeptabel,
  Hauptsache: ohne Feuer null Verhaltenänderung.
- Bewusst NICHT: zusätzliches Warn-Event (Meldungs-Klasse ist die SPEC-014-
  Antwort — hier ist die Wurzel physikalisch, der Cutoff ist die ehrliche
  Antwort); keine Änderung an FIRE_HEAT, START_FIRE_FUEL, STOKE_FUEL,
  UNTERKÜHLUNG-Schwelle, exposure, insulation.

**TDD-Reihenfolge:**
1. Design-Skizze (1 Absatz, JOURNAL) — VOR dem ersten Test.
2. Failing tests zuerst (neu: `tests/test_fire_comfort.py`):
   - Rest-Loop-Regression: 500-fuel-Feuer (forest_edge), 60× `rest()`,
     alle 20 Scorecard-Seeds (20260803..20260822) → 0/20 Tode, hp > 0.
   - bt pendelt im Komfortfenster: nach 40 Rast-Ticks am Feuer bt < 40.0
     (kein HITZSCHLAG-Tick je eintritt), bt > 35.0 bleibt (Wärme wirkt).
   - Cap greift nur am Feuer: gleicher Seed ohne Feuer (fire_active=False)
     → bt-Verlauf byte-identisch zur alten Formel (getstate-Vergleich /
     feste Seed, Werte per Snapshot).
   - Keine neuen RNG-Würfe: `random.getstate()` vor/nach `rest()`-Sequenz
     mit feuerlosem Crossing-freiem Setup unverändert; mit Feuer: nur die
     bekannten %-12-Wetter-Crossings.
   - Kälte-Seite unberührt: alle bestehenden tests/test_cold_hints.py +
     tests/test_rest.py bleiben unverändert grün (Nacht ohne Feuer friert
     weiterhin; UNTERKÜHLUNG-Guard-Logik unangetastet).
3. Rot laufen lassen (`pytest tests/test_fire_comfort.py -v`) — Rest-Loop-Test
   muss mit den 19/20-Toden rot sein (das ist die Re-Produktion als Test).
4. Implementieren: Konstante + eine Zeile Cap in core.py (Zeile ~332-Umgebung).
5. Grün laufen lassen. Dann ganze Suite.
6. Delta-Tabelle `compute_all()` vor/nach (Tages-Baseline, /tmp-Write only):
   Erwartung alle 12 byte-identisch — Scorecard-Bots rufen rest() nie
   (SPEC-015-Präzedenz 10.09.). Bei Abweichung: vollständige Tabelle führen,
   Stream-Shift-Klasse benennen, Go/No-Go danach.
7. JOURNAL-Eintrag + Commit (eigener Commit, NUR T1-Files).
8. CLI-Smoke: [r]asten am Feuer, Log-Zeilen ehrlich (kein HITZSCHLAG mehr im
   Loop, Feuer brennt sichtbar ab).

**Akzeptanz T1:** 0/20 Rest-Loop-Tode; bt-Fenster 35–40 am Feuer; kein
Verhalten ohne Feuer (Test); pytest grün; Delta-Tabelle im JOURNAL
(byte-identisch oder dokumentiert); kein Data-Touch, kein Reason-Code-Eingriff,
kein Rezept-Leak (Konstante ohne Text); Constitution-Check im JOURNAL.

## Task 2 — B10: `stick` → WOOD (Direktor-Entscheid, Data-Touch)

**Befund** (BACKLOG B10 + B10-Nachtrag, play/2026-09-07/09/11.md): die Nacht
braucht ~64 Brennstoff-Ticks (14 Rests à 4 + ~8 Stokes à 1). Ein `start_fire`
liefert 24 (START_FIRE_FUEL), jeder KINDLING-Stoke +8 (STOKE_FUEL). KINDLING-
Quellen: reeds (hidden_cave-only) und tinder (Prozess-Output) — die Höhlen-
Reserve hält ~5 Stokes nach Warmup, dann ist die Quelle weg. Folge: Feuer
stirbt @Rest 5–6 in der Nacht → Rast unterm kalten Waldrand = UNTERKÜHLUNG.
Gleichzeitig: `log_oak` trägt WOOD (quasi-unerschöpflich, braucht Axt +
CHOPPING — im natürlichen Verlauf spät), der überall verfügbare `stick` NICHT.
Der WOOD-Fuel-Pfad existiert in der Engine (`_find_fuel_item`, core.py:843-853:
WOOD bevorzugt, KINDLING zweiter, fire_pit nie) — aber das naheliegendste
„Holz" ist still ausgeschlossen. Kein Design-Wunsch, eine Datenlücke.

**Entscheid des Direktors (13.09.): GO für den Data-Touch.** Ein Ast IST Holz.
Die Änderung:

```json
// data/items.json, "stick" — EIN Tag ergänzen:
"tags": { "RIGID": true, "WOOD": true }
```

(snippet: `.hermes/plans/2026-09-13_180400-direktor-snare-stick-wood-snippet.json`)
Spiel-Wirkung: stoke_fire bevorzugt über `_find_fuel_item` ab sofort sticks
(quantity--, +8 Fuel-Ticks pro Stick); die Nacht wird zur planbaren
Brennstoff-Beschaffung („vor der Nacht Sticks sammeln" — sticks sind 12/20 naiv
sammelbar); die Zünd-Kette (tinder/reeds) und alle Blueprint-Slots bleiben
unberührt — kein Blueprint matcht bislang WOOD (verifiziert 13.09.,
grep blueprints.json: 0 Treffer). Das vertieft das Entdecken: die
Brennstoff-Ökonomie wird als learnbares Muster lesbar (B10-Klasse), statt
Zufalls-Todesurteil. Kein Rezept, kein Leak, kein Text.

**Verworfen (gleiches Befund-Cluster):** Tier-2-Anschluss-Andeutung an der
rope-Discovery (BACKLOG 07.09., cord_spear 0/20) — sharpen_tool-Präzedenz:
6 Lesungen 0/20; eine Andeutung an einer Mechanik, deren Grundpfad tot ist,
ist Reihenfolge-falsch. Bleibt im Backlog-Ideen-Pool.

**TDD-Reihenfolge:**
1. Tages-frische Baseline ziehen (NACH T1-Landung, /tmp only).
2. Design-Skizze (1 Absatz, JOURNAL) — inkl. Blueprint-/Prozess-Blast-Radius:
   grep WOOD in data/blueprints.json + data/processes.json (Erwartung: nur
   start_fire-`tools`-Kontext? NEIN — verifiziert: processes.json KINDLING-Treffer
   ist ein `tools`-Slot, WOOD 0 Treffer in Blueprints. Falls du doch ein Delta
   findest: Stop, Go/No-Go neu bewerten, Direktor-Zeile im JOURNAL).
3. Failing tests zuerst (`tests/test_fuel_wood.py` oder in bestehende Fuel-Tests):
   - stoke_fire mit stick im Inventar (kein log_oak): fuel +8, stick quantity--,
     Erfolgsmeldung ehrlich.
   - `_find_fuel_item`-Präferenz: WOOD (stick) vor KINDLING (reeds/tinder);
     fire_pit wird NIE als Brennstoff gewählt (bestehender Guard, Test verankern).
   - start_fire-Pfad unberührt: tinder-Kette bleibt Zünd-Voraussetzung
     (bestehende Tests bleiben grün).
   - Blueprint-Regression: snare/rope/spear etc. craften unverändert
     (kein Blueprint-Slot liest WOOD — Regressionstest gegen Datenlücke).
4. Rot laufen lassen. Dann die EINE Tag-Änderung in data/items.json.
5. Grün laufen lassen. Dann ganze Suite.
6. Delta-Tabelle `compute_all()` vor/nach: Stream-Shift ERWARTET und
   dokumentiert (Data-Touch ändert Item-Sortierung/Sequenz-Kontext —
   31.08.-Präzedenz Munitions-Ökonomie: dokumentieren, nicht kompensieren).
   Besonders lesen: blueprint_reachability (1.0, 11/11), content_reachable
   (1.0, 18/18), discovery_gap (im Band 0.2–0.6). Weicht ein Wächter ab →
   NO-GO, revert, Direktor-Triage zurück.
7. JOURNAL-Eintrag + Commit (eigener Commit, NUR T2-Files).
8. Play-Gegenprobe → Play-Job (nicht Dev): Nacht-Fenster-Erfolgsrate mit
   stick-Fuel, explorativ, kein harter Gate (kein Overfitting am Mess-Bot).

**Akzeptanz T2:** ein Tag in data/items.json; Wächter 1.0/1.0/1.0; gap im Band;
Delta-Tabelle im JOURNAL (Stream-Shift dokumentiert, nicht kompensiert);
pytest grün; Fuel-Tests verankert; Blueprint-/Prozess-Blast-Radius im JOURNAL
benannt (verifiziert leer); Constitution-Check im JOURNAL; Play-Gegenprobe
ausständig (Play-Job).

## Quellen

- play/2026-09-11.md (B11 + B10-Nachtrag, rest_adoption-Erstlesung 0.333)
- play/2026-09-09.md (B10-Verifikation: reader/deaf/retreat, 0/20 start_fire bekannt)
- play/2026-09-07.md (B10-Erstmeldung: 20/20 Kälte-Tode im Menü-Profil)
- BACKLOG 🔴 B10/B11, 🟡 07.09. (Tier-2-Andeutung — verworfen)
- JOURNAL 10.09./11.09. (SPEC-015-Landung, Stream-Disziplin-Präzedenz)
- engine/core.py:42/332-357 (Wärme-Physik), core.py:843-877 (_find_fuel_item/stoke)
