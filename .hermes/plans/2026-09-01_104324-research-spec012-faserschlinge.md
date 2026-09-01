# Research-Spec-Plan: SPEC-012 Faserschlinge — die toten 2-Slot-Selektionsräume besetzen

> **For Hermes:** Plan-Modus-Lauf (Cron Di 01.09. 2026, `plan`-Skill aktiv — der Plan-Modus gewinnt
> gegen das Execute-Mandat des Cron-Prompts, siehe Skill-Abschnitt "Plan-mode runs"). KEIN Commit in
> diesem Turn. Der nächste Research-Run (Metrik-Modus) nimmt diesen Plan als Work-Contract, führt die
> Staleness-Checks + Go/No-Go-Probe aus und schreibt dann genau die hier ausgearbeiteten Artefakte
> (Spec + PLAN.md-Task + JOURNAL-Eintrag) und committet. EIN Spec, EIN Commit.

**Goal:** `discovery_gap` zurück ins Band (0.600 Bandkante → ≤ 0.55) mit genau einem spiel-seitigen
Hebel: ein naiv erreichbarer 2-Slot-Blueprint `snare` (Faserschlinge), der den größten toten
Selektionsraum des Gap-Bots besetzt und an die Munitions-Ökonomie (31.08.) andockt.

**Architecture:** Data-only Spec — `data/blueprints.json` +1 Blueprint, KEINE Engine-/Metrik-Änderung.
Alle Mechanik-Wege existieren bereits (tool_tag-Matching, PROJECTILE-Consumable-Pfad von 31.08.,
NEW_COMPONENT-Reveal, dict-order-Präzedenz). Der harte Teil ist die Messdisziplin: Probe als
Go/No-Go-Gate, vollständige compute_all()-Delta-Tabelle (RNG-Strom-Klasse!), pytest inkl. der
zwei Content-Zähler-Tests.

**Tech Stack:** stdlib + pydantic (data/loader), pytest, Runtime-Probes via `PYTHONPATH=.` `python -c`
(kein Scorecard-File-Write).

**Evidence-Basis (Pre-Messung dieses Plan-Modus-Laufs, alle read-only, Seeds = scorecard.SEEDS 20260803–20260822):**
| Probe | Befund |
|---|---|
| P1 Baseline | naive_rate 0.400, gap 0.600 (Bandkante), Tode 19/20 @ Median Aktion 119, last_new-Median 86.5 |
| P2 Immortal 150 / 400 Aktionen | 150 Aktionen immortal = **identische 0.400** → Gap ist NICHT survival-gebunden; 400 Aktionen immortal → 0.600 (gap 0.400) → Selektions-gebunden, Zeit-trunkiert |
| P2b fiber_wrap (FIBER+FIBER) | gap 0.636 — **VERSCHLECHTERT** (3/20 Hits, Dilution schlägt Hit-Rate). Negativ-Resultat: ein neuer 2-Slot-BP hilft nur, wenn er einen großen toten Pool besetzt |
| P3 BP-Entdeckungsstruktur | knife_stone 16/20, axe_stone 10, rope 9, spear 8 … **cord_spear 0/20**; größte NO_MATCH-Pools: (EDIBLE,FIBER) 12, (EDIBLE,RIGID) 12, (EDIBLE,PROJECTILE) 6 |
| P4 snare (FIBER+EDIBLE) | naive_rate **0.455**, gap **0.545 im Band**, 17/20 craften ihn (Median Aktion 36), Tode unverändert 19/20 |

**Ausgeschlossene Alternativen (bewusst, mit Befund):**
- *Survival-Hinweise (Kälte/Hunger-Richtungs-Meldungen):* bewegen KEINE Metrik — der Gap-Bot liest
  bewusst keine Logzeilen (Mess-Rollen-Trennung, JOURNAL 31.08.), und P1 zeigt: das Discovery-Plateau
  (last_new 86.5) liegt VOR dem Kältetod (Aktion ~119) — der Tod bindet den Gap nicht. Gehört in den
  Free-Exploration-Modus oder zum Direktor, nicht in einen Metrik-Modus-Spec.
- *fiber_wrap als Isolation:* Physik bindet dagegen — body_temp asymptotiert an effective_ambient
  (< 35 °C in allen Biomen), Isolation verzögert nur; P2-C (insulation 0.6!) senkt Tode 19→18 und
  verschlechtert den Gap (Dilution). P2b: 2×FIBER-Slots treffen die Zufalls-Selektion fast nie (3/20).

---

## Ausgangslage / Staleness-Check (Aufgabe 1 des ausführenden Runs)

Vor jedem Schreiben verifizieren, dass die Prämissen noch halten (Lektion SPEC-003/SPEC-006):
1. `git fetch && git log --oneline -5` — nichts Neues gelandet, das den Scorecard-Stand verschiebt.
2. `scorecard/latest.json` + `SCORECARD.md`: `discovery_gap` weiterhin ≥ 0.60 bzw. letzte Play-Lesung
   auf Bandkante (letzte ECHTE Play-Lesung: 26.08.; die 31.08.-Werte sind Dev-Delta-Arithmetik).
   Wichtige Nuance: Diese Proben lasen HEAD (inkl. 31.08.-Landungen) → Baseline gap = 0.600 exakt.
3. PLAN.md: Ziel-1 (Gap zurück ins Band) noch offen, "Gap-Wächter zurücksetzen"-Task noch offen.
4. **Go/No-Go-Probe (Pflicht, siehe unten):** snare-Variante über die 20 Seeds muss gap ≤ 0.6 lesen
   UND `blueprint_reachability` = 1.0 (11/11) halten UND keinen anderen Band-Crossing erzeugen.
   Negativ-Ergebnis → Task ENDET mit BACKLOG-Eintrag + Direktor-Flag (Negative-Result-Protokoll,
   analog 18.08./28.08. Sweep-Gate), kein Spec-Ship gegen die eigene Probe.

## Was der Spec macht (Kurzfassung für die Task-Zeile)

**Mechanik (aus echten Spielen):** Don't Starve — *Berry Bait + Traps*: Nahrung wird Baumaterial;
eine Falle/Köder-Kombination eröffnet Jagd ohne Kampffähigkeit oder Munition. UnReal World:
Schlingenfang ist die klassische low-skill-Jagd; die Schlinge ist selbst Werkzeug, verbrauchbar und
aus Faser + Köder gebaut. Das ist das PPP-Prinzip „Entdecktes wird selbst Zutat" (Little Alchemy),
auf der einfachsten Stufe: die zwei am häufigsten gesammelten Stack-Klassen (Faser + Essbares)
werden zum ersten tier-0-Craft-Paar (vor jedem Survival-Gate).

**Warum GENAU das den Gap bewegt (Probe P3/P4):** Der Gap-Bot (`_run_naive_discovery`, 150 Aktionen,
2–3 zufällige Stack-Selektionen, isst bei energy<150) entdeckt fast nur 2-Slot-Blueprints mit
Multi-Stack-Deckung (knife_stone 16/20, axe_stone 10/20 …). Sein größter toter Experiment-Raum ist
(Essbares, Faser) — ~30 NO_MATCH-Paare über 20 Seeds, die KEIN Blueprint besetzt. Ein snare-Blueprint
{loop: FIBER, bait: EDIBLE} belegt genau diesen Raum: **P4: 17/20 Seeds craften ihn (Median Aktion 36),
naive_rate 0.400 → 0.455, gap 0.600 → 0.545 zurück im Band.** Er ist zugleich Jagd-Werkzeug
(tool_tag `PROJECTILE` → `find_item_by_tag` qualifiziert ihn für den raw_meat-Node an forest_edge,
max_stock 5) — die Antwort auf die 31.08.-Munitions-Ökonomie (die Pebble-Munition ist endlich):
Die Schlinge ist der primitive Weg ohne Munition, geht aber pro Fang verbraucht (31.08.-Pfad:
quantity-- pro Ernteerfolg, Meldung „!!! Faserschlinge aufgebraucht !!!" via used_tool.name — kein
Engine-Touch nötig).

---

## Aufgabenliste für den ausführenden Run (bite-sized, in dieser Reihenfolge)

### Task 1: Staleness-Check + Go/No-Go-Probe (read-only)

**Files:** keine (Probes via `/tmp`, Runtime-Wrapper)

**Schritte:**
1. `git fetch && git log --oneline -5 && git status -sb` — HEAD unverändert vs. fcb4da6 oder neuere
   reine Doc-Commits; sonst diesen Plan gegen den neuen Stand prüfen.
2. Scorecard-Frische prüfen (`ls scorecard/` — falls eine NEUE Play-Lesung (≥ 02.09. — Mi-Job) mit
   gap < 0.6 existiert: **Plan-Prämisse prüfen** — der Spec bleibt gültig (er senkt weiter Richtung
   Bandmitte), aber die Begründung „Bandkante" auf den neuen Stand anpassen).
3. Go/No-Go-Probe mit `/tmp/probe_gap_snare.py` (existiert in /tmp; falls weg: rebuild nach
   Probe-Skizze unten) gegen HEAD:
   - Erwartung (aus P4): naive_rate ≈ 0.455, gap ≈ 0.545, snare 17/20.
   - ZUSÄTZLICH prüfen: `PYTHONPATH=. python -c "from tools import scorecard as sc; print(sc.metric_reachability()['value']); print(sc.metric_content_reachable()['value'])"`
     (mit gepatchten Blueprints wie im Probe-Skript) → reachability 1.0 (11/11), content_reachable 1.0.
4. **No-Go-Kriterien** (eins reicht): gap mit snare > 0.6 · reachability < 1.0 · eine andere Band-Metrik
   kreuzt. → Kein Spec-Ship: Negativ-Befund in BACKLOG (⚪ Research, mit Probe-Tabelle), JOURNAL-Eintrag,
   Direktor-Flag, Commit der Dokumentation. Plan abhaken mit Befund-Zeile.

### Task 2: Spec schreiben — `specs/SPEC-012-faserschlinge.md`

**Files:** Create `specs/SPEC-012-faserschlinge.md`. Volltext siehe unten (copy-paste-fertig, nach dem
Schreiben: Selbst-Lese-Pass auf Sprach-Drift — JOURNAL-Regel vom 27.08., dichtester Prosa-Abschnitt:
Akzeptanzkriterien + Metrik-Wirkung).

```markdown
# SPEC-012 — Faserschlinge: die toten 2-Slot-Selektionsräume besetzen

**Problem** (Metrik: `discovery_gap`, Band 0.2–0.6; Play-Report 26.08. + Scorecard 29.08. +
Dev-Delta 31.08.): Drei Lesungen über Band (0.6 → 0.65 → 0.70) trugen den Gap auf die Bandkante —
naive_discovery_rate 0.4 → 0.35 → 0.3, naive_p25 0.3. Die 31.08.-Landungen (Munitions-Ökonomie,
Prozess-Hinweise, B08) haben die Zahl per Delta-Tabelle zurück auf 0.6 gebracht — aber das ist
Bandkante, nicht Bandmitte, und die letzte ECHTE Play-Lesung (26.08.) lag exakt dort.

Proben vom 01.09. (read-only, 20 Scorecard-Seeds, HEAD fcb4da6):
- Der Gap-Bot stirbt 19/20 an Kälte (Median Aktion 119) — aber sein Discovery-Plateau (last_new
  Median 86.5) liegt VOR dem Tod. Unsterbliche Läufe (immortal) lesen identische 0.400. **Der Gap ist
  selektionsgebunden, nicht survivalgebunden.** „Überlebens-Hinweise" (Direktor-Ziel-1-Rest) können
  ihn daher nicht bewegen — kein Bot reagiert auf Log-Zeilen, und Tod ist nicht die Bindung.
- Der naiv erreichbare Experiment-Raum ist asymmetrisch: knife_stone 16/20 (SPEC-010s Pebble),
  axe_stone 10/20, rope 9/20 (Gate 0.4), spear 8/20 — aber cord_spear 0/20 und die 3-Slot-Blueprints
  sind Selektions-Luck. Der größte TOTE Raum sind (Essbares, Faser)/(Essbares, Rigid)-Paare
  (~30 NO_MATCH-Paare über 20 Seeds): ein naiver Spieler hält permanent Beeren/Fleisch in der Hand,
  aber kein Blueprint der Welt will sie als Zutat.
- Ein Test-Blueprint {FIBER, FIBER} (Fasermantel) wurde gemessen: gap 0.636 — dilution schlägt
  Hit-Rate, weil 2×denselben Fiber-Stack zu treffen unwahrscheinlich ist. Ein neuer BP hilft nur,
  wenn er einen großen toten Multi-Stack-Pool besetzt.

**Mechanik** (Quell-Spiele): Don't Starve — Beerenköder + Fallen: Nahrung als Crafting-Material
eröffnet Jagd ohne Kampfskill; UnReal World — Schlingenfang als klassische low-skill-Jagd: Faser +
Köder wird zum eigenen Fangwerkzeug, das pro Fang verbraucht werden kann. Das ist die simpelste
Form von „Entdecktes wird selbst Zutat" — ohne Tier-2-Gate, ohne Prozess-Kette.

**Adaption** (konkret, data-only, kein Engine-Touch):
- `data/blueprints.json` — EIN neuer Eintrag, am ENDE des Arrays (nach cord_spear, Dict-Order =
  Präzedenz):

```json
{
  "id": "snare",
  "result_name": "Faserschlinge",
  "slots": {"loop": "FIBER", "bait": "EDIBLE"},
  "base_efficiency": 1.0,
  "min_survival_req": 0.0,
  "tool_tags": ["PROJECTILE"]
}
```

- Kein Eintrag in `items.json` (Blueprint-only wie die 10 Werkzeuge — sonst sinkt
  `content_reachable`, 18/18 → 18/19, siehe SPEC-008-Regel).
- Shadowing-Check (engine-true): (FIBER, EDIBLE) wird von keinem früheren Blueprint voll getroffen —
  rope braucht RIGID, spear/knife/axe brauchen FLINT/BONE/STONE/SHARP: Beeren+Pflanzenfaser → snare.
  (stick, stick) → spear, (reeds, stick) ab survival 0.4 → rope — Präzedenz bleibt intakt.
- Funktion (kostenlos, 31.08.-Pfad): `tool_tags: ["PROJECTILE"]` → `find_item_by_tag("PROJECTILE")`
  qualifiziert die Schlinge für den raw_meat-Node (forest_edge, max_stock 5, req_perception 0.0).
  Die 31.08.-Munitions-Semantik (PROJECTILE = verbrauchbar, quantity-- pro Ernteerfolg, Meldung
  „!!! <name> aufgebraucht !!!" via used_tool.name) gilt automatisch: eine Schlinge = ein Fang.
  Das ist die Antwort auf die endliche Pebble-Munition: Faser + Köder sind erneuerbar, Munition nicht.
- NEW_COMPONENT-Reveal feuert beim ersten Bau (engine-default) — kein Grund-Code-Eingriff.

**Akzeptanzkriterien** (jedes verifizierbar):
1. `data/blueprints.json` hat 11 Einträge; `snare` craftet aus (plant_fiber, berries) bei survival 0.0
   (Unit-Test, frische Engine) und aus (reeds, raw_meat) gleichermaßen — EDIBLE-Slot ist material-agnostisch.
2. Shadowing-Tests: (stick, stick) → spear; (reeds, stick) ab survival 0.4 → rope (nicht snare);
   (plant_fiber, berries) → snare BEI ALLEN survival-Werten.
3. Jagd-Verbrauch: erfolgreiche raw_meat-Ernte mit Schlinge → quantity 1→0, Item entfernt,
   Meldung enthält „Faserschlinge aufgebraucht" (generische 31.08.-Meldung, kein Rezept-Leak).
4. `blueprint_reachability` = 1.0 (11/11, tool-aware Zähler — snare ist ungated und trivial erreichbar).
5. `content_reachable` = 1.0 (18/18, snare ist Blueprint-only, kein Template).
6. `discovery_gap` (20-Seed-Probe auf HEAD): ≤ 0.55 — Ziel: Bandmitte statt Bandkante.
   **Go/No-Go:** > 0.6 → nicht shippen (Negativ-Protokoll).
7. `python -m pytest` grün — reconciliert: `tests/test_engine.py:402` (10 → 11),
   `tests/test_loader.py:65` + `:229` (10 → 11); neue Tests 1–3.
8. Vollständige compute_all()-Delta-Tabelle vor/nach im JOURNAL (RNG-Strom-Klasse: der naive
   Strom verschiebt sich auf ~17/20 Seeds — dokumentieren wie SPEC-009/010, nicht kompensieren;
   Direktor-Flag im selben Commit, falls eine andere Band-Metrik kreuzt).
9. Kein Rezept-Leak: Snare-Erfolgs-Meldung folgt dem dynamischen `_create_tool`-Namensschema,
   Failure-Pfade unverändert.

**Erwartete Metrik-Wirkung** (Primär: `discovery_gap`; Proben 01.09., 20 Seeds):
- `discovery_gap` 0.600 → ~0.545 (naive_rate 0.400 → 0.455, 17/20 Seeds craften snare @ Median
  Aktion 36). Tode unverändert (19/20) — kein Survival-Effekt behauptet, keiner gemessen.
- `craft_variety` ≥ 5 hält oder steigt leicht (Ziel-2-Richtung „≥ 5 und darüber").
- `blueprint_reachability`/`content_reachable`/`feedback_quality` unverändert (Wächter-Kriterien 4–5).
- `session_depth` (v2, Probe bis 08.09.): der v2-Bot wird snare ebenfalls bauen → Re-Baseline-Verschiebung.
  Das ist Stream-Shift-Klasse (wie SPEC-010): Lesung dokumentieren, NICHT als Fortschritt feiern,
  Direktor bewertet nach Probe-Ende.
- `warmth_stability`/`recovery_stability`: unberührt (kein Kälte-/Verletzungs-Pfad).
- `gear_uptime`/`forage_pressure` (Probe bis 11.09.): snare ist ein zusätzliches PROJECTILE-Subjekt
  im Jagd-Pfad — Erstlesung der beiden läuft weiter beobachtend, keine Tuning-Anlässe.

**Constitution-Check:** Tag-Crafting-Kern unangetastet, kein Rezeptbuch/Leak, stdlib only,
neuer Content (Blueprint) — erlaubt; keine Metrik entfernt/umdefiniert/abgeschwächt; das Entdecken
wird vertieft (neue Zutatenklasse „Essbares als Material"), nicht abgekürzt. CLI-Text bleibt.
```

### Task 3: PLAN.md — Task ergänzen (offen)

**Files:** Modify `PLAN.md`, Tasks-Sektion, als erste offene Zeile NACH den erledigten [x]-Tasks
(vor „Gap-Wächter zurücksetzen"):

```markdown
- [ ] **SPEC-012 — Faserschlinge: die toten 2-Slot-Selektionsräume besetzen** (Research 01.09.,
      probe-verifiziert). Befund: Der Gap ist selektionsgebunden, nicht survivalgebunden (Proben:
      immortal-Bot identisch 0.400, Tode 19/20 — Discovery-Plateau @86.5 vor Tod @119). Der größte
      tote naive Selektionsraum ist (EDIBLE, FIBER)/(EDIBLE, RIGID) — kein Blueprint besetzt ihn.
      Antwort: `snare` {loop: FIBER, bait: EDIBLE}, ungated, tool_tags [PROJECTILE] → Jagd-Alternative
      zur endlichen Pebble-Munition (31.08.-Pfad, data-only). Probe 01.09.: naive_rate 0.400 → 0.455,
      gap 0.600 → 0.545 (im Band), 17/20 Seeds. Akzeptanz: Go/No-Go-Probe ≤ 0.55 auf HEAD, Wächter
      1.0/1.0/1.0, pytest grün, Delta-Tabelle (RNG-Strom!), session_depth-Shift als Re-Baseline
      dokumentiert (Probe bis 08.09.), kein Rezept-Leak.
```

### Task 4: JOURNAL.md — Eintrag (prepend-without-clobber!)

**Files:** Modify `JOURNAL.md` (Regel 08-24: neuer Eintrag ÜBER dem Top-Header, alter Header bleibt).
Titel: `## 2026-09-03 — [Research] SPEC-012 Faserschlinge — toter Selektionsraum besetzt, Gap zurück im Band (Probe 0.545)`
Inhalt: Probe-Tabelle (P1–P4 + Go/No-Go-Lesung des Tages), Metrik-Auswahl-Skip-Log
(session_depth/gear_uptime/forage_pressure = Probezeit; warmth = Peters Lesung Beobachtungsgröße;
recovery = Probe bis 03.09.; discovery_gap = Ziel 1, verifizierbar seit REC-002), 3 refutierte
Hypothesen (Survival-Hinweise bewegen den Gap-Bot nicht; fiber_wrap dilution-tot; Isolation verlangt
Feuer). Datum im Titel = Tag der AUSFÜHRUNG, nicht 01.09.

### Task 5: Verifizieren + Commit + Push

1. `python -m pytest` — grün (277 aktuell + neue Snare-Tests + die 3 reconcilierten Zähler-Assertions).
2. Selbst-Review-Pass über `specs/SPEC-012-faserschlinge.md` (Sprach-Drift, Regel 27.08).
3. `cd ~/projects/primal-process && git add -A && git commit -m "research: spec 012 faserschlinge (cron)" && git push`
4. Push verifizieren: `git status -sb` (clean, kein ahead) + `git log origin/main..main --oneline` leer.

---

## Files likely to change (beim ausführenden Run)

- Create: `specs/SPEC-012-faserschlinge.md`
- Modify: `data/blueprints.json` (+1 Eintrag, ans Array-Ende) — NUR wenn Task 1 positiv; der
  Research-Run schreibt normalerweise nur Dokumente. Entscheidungshilfe: Ist Dev (Mo/Mi/Fr) der
  Umsetzer, kommt NUR Spec + PLAN-Task + JOURNAL in den Research-Commit; der Dev-Run implementiert
  gegen den Spec (TDD). Ist der ausführende Run selbst bereit, den data-only-Change mitzunehmen,
  darf er Task 1's Probe als Ship-Gate nutzen — Spec schreibt die Datenänderung als Adaption vor.
- Modify: `PLAN.md` (Task-Zeile), `JOURNAL.md` (Eintrag), ggf. `tests/test_engine.py:402`,
  `tests/test_loader.py:65,229` (10 → 11) + neue Snare-Tests NUR beim Implementieren.

## Tests / Verifikation (Implementierungs-Phase, Dev)

- Unit: snare craftet aus (plant_fiber, berries) bei survival 0.0; aus (reeds, raw_meat) ebenfalls.
- Shadowing: (stick, stick)→spear; (reeds, stick) @ survival≥0.4 → rope; snare nie von Präzedenz
  verdrängt, verdrängt selbst nichts.
- Jagd: raw_meat-Ernte mit Schlinge → Ernte-Erfolg + quantity-- → 0 → Item weg + „Faserschlinge
  aufgebraucht". Ohne PROJECTILE-Item im Inventar bleibt es bei der MISSING_TOOL-Meldung
  (SPEC-011-C-Pfad) — die Schlinge ist die werkzeugseitige Antwort, keine Stilllegung des Druckpfads.
- Wächter: reachability 11/11 = 1.0, content_reachable 18/18, feedback_quality 1.0.
- compute_all()-Delta-Tabelle vollständig (Pflicht bei Stream-Shift) im JOURNAL.

## Risiken / Tradeoffs / offene Fragen

1. **Dilution-Schraube:** Jeder zukünftige +BP zählt im Nenner (1/11 ≈ 0.09). Wenn Direktor später
   weitere BPs addiert (z. B. das freigegebene tool-as-ingredient-Layer), muss JEDES neue BP seinen
   Gap-Beitrag per Probe nachweisen — dieser Spec etabliert das Probe-Muster (Runtime-Wrapper,
   /tmp, read-only), nicht das Ergebnis für alle Zeiten.
2. `session_depth` v2 sitzt bis 08.09. in Re-Baseline-Probezeit. Der snare verschiebt die Lesung
   (Stream-Shift). Direktor muss das als Re-Baseline-Shift lesen, nicht als Fortschritt — steht so
   im Spec und im PLAN-Task.
3. Die „Schlinge verbraucht sich pro Fang"-Semantik erbt den 31.08.-Ammo-Pfad (quantity--). Wenn
   Peter/Direktor später eine wiederverwendbare Fallen-Ökonomie wollen, ist das ein eigener Spec —
   heute bewusst NICHT gebaut (YAGNI).
4. EDIBLE als Slot-Wert ist ein neues Muster (Blueprint-Slot auf einem Funktions-Tag statt
   Material-Tag). Alle Slots bisher sind Material-/Familien-Tags. `_slot_satisfied` behandelt das
   korrekt (Einzel-Tag-Lookup), aber der Spec-Text muss das Muster benennen, damit spätere Specs es
   nicht versehentlich brechen.
5. Go/No-Go: Wenn die Go/No-Go-Probe (Task 1) auf dann-HEAD anders liest (z. B. weil inzwischen ein
   Dev-Commit den Strom verschoben hat), gilt die TAGES-Probe, nicht P4's 0.545 — der Plan ist die
   Methode, nicht die Zahl.