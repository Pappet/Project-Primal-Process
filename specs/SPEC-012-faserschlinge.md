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
  (stick, stick) → spear, (plant_fiber, stick) ab survival 0.4 → rope — Präzedenz bleibt intakt.
  *Korrektur 07.09. (Dev-Lauf): Der Work-Contract-Text behauptete `(reeds, stick) → rope`; die
  Engine liest `(reeds, stick) → spear` (reeds trägt RIGID und spear steht früher im Dict) — das
  galt schon vor SPEC-012 und ist von snare unberührt (kein EDIBLE beteiligt, snare kann diesen
  Craft nie übernehmen). Der echte rope-Fall ist (plant_fiber, stick); beide Schatten sind
  testverankert (tests/test_snare.py, TestSnareShadowing).*
- Funktion (kostenlos, 31.08.-Pfad): `tool_tags: ["PROJECTILE"]` → `find_item_by_tag("PROJECTILE")`
  qualifiziert die Schlinge für den raw_meat-Node (forest_edge, max_stock 5, req_perception 0.0).
  Die 31.08.-Munitions-Semantik (PROJECTILE = verbrauchbar, quantity-- pro Ernteerfolg, Meldung
  „!!! <name> aufgebraucht !!!" via used_tool.name) gilt automatisch: eine Schlinge = ein Fang.
  Das ist die Antwort auf die endliche Pebble-Munition: Faser + Köder sind erneuerbar, Munition nicht.
- NEW_COMPONENT-Reveal feuert beim ersten Bau (engine-default) — kein Grund-Code-Eingriff.

**Akzeptanzkriterien** (jedes verifizierbar):
1. `data/blueprints.json` hat 11 Einträge; `snare` craftet aus (plant_fiber, berries) bei survival 0.0
   (Unit-Test, frische Engine) und aus (reeds, raw_meat) gleichermaßen — EDIBLE-Slot ist material-agnostisch.
2. Shadowing-Tests: (stick, stick) → spear; (plant_fiber, stick) ab survival 0.4 → rope (nicht snare);
   (plant_fiber, berries) → snare BEI ALLEN survival-Werten.
3. Jagd-Verbrauch: erfolgreiche raw_meat-Ernte mit Schlinge → quantity 1→0, Item entfernt,
   Meldung enthält „aufgebraucht" + „Faserschlinge" (generische 31.08.-Meldung mit dynamischem
   Namen, kein Rezept-Leak).
4. `blueprint_reachability` = 1.0 (11/11, tool-aware Zähler — snare ist ungated und trivial erreichbar).
5. `content_reachable` = 1.0 (18/18, snare ist Blueprint-only, kein Template).
6. `discovery_gap` (20-Seed-Probe auf Tages-HEAD 07.09.): 0.600 → 0.545 — **Go/No-Go-Probe bestanden**
   (siehe JOURNAL 07.09.; die Tages-Probe gilt, nicht P4).
7. `python -m pytest` grün — reconciliert: `tests/test_engine.py` (10 → 11),
   `tests/test_loader.py` ×2 (10 → 11); neue Tests: tests/test_snare.py (16 Tests).
8. Vollständige compute_all()-Delta-Tabelle vor/nach im JOURNAL (RNG-Strom-Klasse: der naive
   Strom verschiebt sich auf ~17/20 Seeds — dokumentieren wie SPEC-009/010, nicht kompensieren;
   Direktor-Flag im selben Commit, falls eine andere Band-Metrik kreuzt).
9. Kein Rezept-Leak: Snare-Erfolgs-Meldung folgt dem dynamischen `_create_tool`-Namensschema
   („Hergestellt: <Faser>-Faserschlinge (<Köder>)" + generischer Reveal), Failure-Pfade unverändert.

**Erwartete Metrik-Wirkung** (Primär: `discovery_gap`; Proben 01.09. + Tages-Go/No-Go 07.09.):
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
