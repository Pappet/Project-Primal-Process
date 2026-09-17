# SPEC-016 — Glut: der Feuerort erinnert sich (Ortsbindung als Welt-Gedächtnis)

> **STATUS: offen — Research-Proposal (Explore-Cron 17.09.), wartet auf
> Direktor-Triage.** Constitution-Feld: „Terrain und Ortsbindung", „Basisbau",
> „Feuer und Wärme" — ausdrücklich gegrüßte Richtung. Kein Data-Touch, kein
> Metrik-Core-Touch, keine neuen RNG-Würfe.

## Problem

**System-Schwäche: Die Welt hat kein Gedächtnis für die Arbeit des Spielers.**

Jeder Zustand, den der Spieler in der Welt hinterlässt, löscht sich selbst. Das Feuer
ist der einzige persistente Spieler-Eintrag — und es ist binär tot: Nach FIRE_OUT
(`fire_active = False`, `fire_fuel = 0`, core.py:338-340) ist der Feuerort
*byte-identisch* mit einem Ort, an dem nie ein Feuer brannte. Drei verifizierte
Befunde aus dem Repo/Play-Korpus:

1. **Der Versorgungs-Kollaps ist ohne Restwert.** Play/Befund 28.08.
   (BACKLOG 🔵): nach FIRE_OUT am Waldrand scheitert die Reparatur
   systematisch — tinder/reeds/sticks leer, `start_fire` unmöglich, bt-Kollaps,
   HP-Drain („Versorgungsspirale"). Der Dev-Lauf bewies: „nach dem Kollaps
   reparieren" ist strikt schlechter als Prävention (19/20 vs. 12/20 Tode).
   Aber die Lehre fehlt die Hälfte: *am Kollapsort selbst* liegt ein toter
   Feuerplatz — der eine Ort, an dem der Spieler schon alles beisammen hatte —
   und die Engine bewertet ihn als bedeutungsloses Neuland. Ein toter Feuerort
   ist heute ökonomisch identisch mit Jungfrau-terrain.
2. **Ortsbindung existiert strukturell nicht.** Locations unterscheiden sich nur
   in `nodes`/`base_temp`/`exposure`; Reisen ist reines Node-Optimum. Die Höhle
   (exposure 0.1) ist die dokumentierte Kälte-Antwort (BACKLOG 13.08.:
   „Kälte zwingt zur Planung") — aber es gibt keinen mechanischen Grund, an
   *einem* Ort zu bleiben oder zurückzukehren, außer Node-Regen. Die
   Constitution-Felder „Terrain und Ortsbindung" und „Basisbau" sind
   unbesetzt; der kleinste Baustein dafür fehlt.
3. **`fire_pit` ist ein Beleg ohne Funktion.** `start_fire` gibt `fire_pit:1`
   ins Inventar (core.py:1029-1030), trägt KINDLING — und `_find_fuel_item`
   verbrennt ihn ausdrücklich nie (core.py:868-871). Das Item ist ein
   stiller Beleg dafür, dass die Design-Absicht „Feuerstelle als Ort" existierte
   und als Inventar-Quittung landete. Die Welt-Semantik (eine Feuerstelle, die
   bleibt) fehlt hinter dem Item.

## Mechanik

Aus **UnReal World**: Das Lagerfeuer stirbt nie ganz — es hinterlässt eine
*Glut* (embers), die mit etwas gutem Brennstoff wieder entfacht werden kann, und
Wiederaufnahme am gleichen Lager ist drastisch billiger als Neuanfang. Aus
**Don't Starve**: Feuer hinterlässt charred remains; der Ort erzählt, was dort
passiert ist. Aus **The Long Dark** (Fire-Spots/Ruinen): bestimmte Orte tragen
Feuer-Intimität — man kehrt dorthin zurück, weil der Ort *etwas hat*.

Gemeinsamer Kern: **Ein Feuer ist keine Wärme-Zufallsvariable, sondern ein
Zustand am Ort mit Erinnerung.** Die Glut ist die Verkürzung der Rückkehr:
Wer einmal an einem Ort Arbeit in Feuer gesteckt hat, kehrt billiger zurück —
aber die Glut verlischt (Zeit drückt sie unter eine Re-Zünd-Schwelle), also
ist „Glut halten" selbst eine Ökonomie-Achse, keine Gratis-Erinnerung.

Adaptierte Kernidee: FIRE_OUT wandelt das Feuer nicht in Nichts, sondern in
**Glut** (`embers > 0`). Zustand am Ort (`LocationDef`), nicht Item. Mit
Brennstoff am Ort kann der Spieler aus Glut neu zünden — ohne tinder+stick
(Zünd-Kette), nur mit Holz (WOOD) und einem Tick. Fällt die Glut durch Zeit
unter 0, ist der Ort wieder kalt-Neuland. Kein Blueprint, kein Prozess, kein
neues Item — der Mechanik-Kern ist ein Zähler, eine Verzweigung in `stoke_fire`
und eine Konstante.

## Adaption (konkret für PPP)

Dateien: `engine/core.py` (Konstanten, FIRE_OUT-Verzweigung, `stoke_fire`-Glut-Pfad,
`revive_fire`-Pfad), `data/locations.py` (`LocationDef.embers: float = 0.0` —
veränderlicher Zustand wie `fire_fuel`, kein JSON-Touch nötig: Default-Feld),
`tests/test_embers.py`. **Kein Data-Touch** (items/blueprints/processes.json
unangetastet — Wächter `blueprint_reachability`/`content_reachable` strukturell
unangetastet), **kein Metrik-Core-Touch** (`scorecard.py` unangetastet).

1. **Konstanten (`engine/core.py`, nach FIRE_COMFORT_CAP):**
   ```python
   # SPEC-016: Glut — der Feuerort erinnert sich. FIRE_OUT hinterlässt Glut
   # (Ember-Restwert), die mit WOOD (nicht der vollen Zünd-Kette) reaktiviert
   # werden kann, solange sie über der Schwelle liegt. Zeit drückt Glut.
   EMBER_RESIDUE = 6.0        # Glut nach FIRE_OUT (in fuel-Ticks Äquivalent)
   EMBER_DECAY_PER_TICK = 0.1 # Glut verlischt über Zeit (~60 Ticks Fenster)
   EMBER_REVIVE_MIN = 1.0     # unterhalb dieser Glut ist Re-Zündung unmöglich
   ```

2. **Zustand (`data/locations.py`):** `LocationDef.embers: float = 0.0` —
   veränderlicher per-Instanz-Zustand wie `fire_fuel` (kein Cross-Session-Bleed,
   Muster-Präzedenz im Docstring). `data/loader.py` unberührt: das Feld hat
   einen Default, JSON braucht keinen Eintrag — strukturell kein Data-Touch.

3. **FIRE_OUT-Verzweigung (`engine/core.py`, `_advance_time`, bestehender Block
   ~core.py:338-340):**
   ```python
   if loc.fire_fuel <= 0:
       loc.fire_active = False
       loc.embers = EMBER_RESIDUE          # NEU: der Ort behält die Glut
       logs.append("!!! FIRE_OUT: ... !!!")  # bestehende Meldung bleibt
   ```
4. **Glut-Verfall (`_advance_time`, eigene Zeile nach dem Feuer-Block):**
   ```python
   if not loc.fire_active and loc.embers > 0:
       loc.embers = max(0.0, loc.embers - EMBER_DECAY_PER_TICK * ticks)
   ```
   Beim aktiven Feuer zählt keine Glut (`embers` nur als Übergangszustand).
5. **Re-Zündung (`stoke_fire`, Verzweigung am Anfang):** wenn Feuer aus, aber
   `loc.embers >= EMBER_REVIVE_MIN` und ein WOOD-Item im Inventar: verbrauche 1×
   WOOD, setze `fire_active = True`, `fire_fuel = EMBER_RESIDUE` (die Glut macht
   das Holz warm, nicht tinder) — Meldung ehrlich, generisch („Die Glut nimmt das
   Holz an."), kein Rezept-Leak, Zeit läuft über `_advance_time(1)` wie heute.
   Ohne Glut (< MIN) oder ohne WOOD: bestehende NO_FIRE/MISSING_FUEL-Pfade —
   keine neue Reason-Klasse.
6. **`start_fire` (Prozess) unverändert:** tinder+stick bleibt die volle Zünd-
   Kette am kalten Ort. Glut ist die *gelernte* Verkürzung, nicht der Default —
   deshalb entdeckt der Spieler die Wirkung, nicht das Rezept.

7. **Stream-Disziplin:** Glut erzeugt KEINE neuen RNG-Würfe — Verfall ist
   deterministische Arithmetik, Re-Zündung ist Gütercheck + Zustandswechsel.
   Der `stoke_fire`-Verzweigungspunkt liegt VOR jedem bestehenden Draw; die
   Zeit-Kosten laufen über das bestehende `_advance_time(1)` (nur %-12-Wetter-
   Crossings). `random.getstate()`-Assertion im Test verankert es.

## Akzeptanzkriterien

1. **Glut entsteht nur aus FIRE_OUT:** aktives Feuer → 0 Glut; FIRE_OUT →
   `embers == EMBER_RESIDUE`; Verfall senkt deterministisch (0.1/Tick, multi-
   pliziert mit verstrichenen Ticks); bei 0 ist der Ort byte-identisch mit
   nie-befeuerter Location (Null-Zustand ehrlich).
2. **Re-Zündung aus Glut braucht WOOD, nicht die Zünd-Kette:** mit Glut ≥
   EMBER_REVIVE_MIN + 1× WOOD → Feuer brennt (`fire_fuel == EMBER_RESIDUE`),
   Zunder/tinder NICHT nötig (Gegenprobe mit leerem tinder-Konto). Ohne WOOD:
   MISSING_FUEL-Pfad bleibt. Ohne Glut: NO_FIRE-Pfad bleibt (kein Autokast).
3. **Glut-Fenster ist endlich und lesbar:** nach EMBER_RESIDUE /
   EMBER_DECAY_PER_TICK ≈ 60 Ticks (≈ 10 h) ist Re-Zündung unmöglich —
   Wer zurückkehrt, muss sich entscheiden; „Glut halten" mit billigem Holz
   ist eine legitime, kostenpflichtige Strategie (1 WOOD / ~24 Ticks Feuer-
   Äquivalent — teurer als Nachlegen am lebenden Feuer: Glut-Revive gibt
   RESIDUE, kein STOKE_FUEL-Bonus).
4. **Alle Systeme laufen durch den Tick-Pfad:** Glut-Verfall hängt an
   `_advance_time` — Rast, Reisen,gather verdringen die Glut gleichermaßen
   (Nacht-Rast ohne Feuer am Glut-Ort: Glut sinkt, Fenster tickt ehrlich).
5. **Keine neuen RNG-Würfe:** getstate-Assertion in zwei Fenstern (Verfall,
   Re-Zündung), Muster test_fire_comfort_cap.py R4.
6. **Wächter unberührt (strukturell, trotzdem gemessen):** kein Data-Touch —
   `blueprint_reachability` 1.0 (11/11), `content_reachable` 1.0 (18/18),
   `feedback_quality` 1.0; vollständige `compute_all()`-Delta-Tabelle im
   JOURNAL (Erwartung: alle 13 byte-identisch — die Bots zünden nie FIRE_OUT-
   getrieben, Warmth-Bot hält mit stoke-Guard am lebenden Feuer; falls die
   Tages-Probe wider Erwarten abweicht: Tages-Probe gilt, SPEC-013-Präzedenz
   — kein Ship in dieser Form, Negativ-Protokoll im JOURNAL).
7. **pytest grün** inkl. neuer tests/test_embers.py; CLI bleibt Textinterface;
   kein Rezept-Leak (eine neue generische Meldung, TAG_LABELS-Vokabelklasse
   nicht einmal nötig — „Glut" ist Weltzustand, kein Tag).
8. **Constitution:** Tag-basiertes Crafting unangetastet; kein Rezept/Leak;
   stdlib only; kein Startzeit-Regression (Default-Feld, kein Loader-Pfad);
   Nicht-Ziele respektiert (0 Items, 0 Blueprints, 0 Prozesse, kein GUI,
   kein Kampf). Entdecken vertieft: die Glut-Wirkung ist im natürlichen
   Verlauf erlebbar (FIRE_OUT ist real — Play 28.08.), die Verkürzung wird
   entdeckt, nicht geschenkt.

## Erwartete Metrik-Wirkung

**Primär: keine Bewegung in den bestehenden 13 Metriken — bewusst, wie bei
SPEC-015.** Scorecard-Bots berühren den Glut-Pfad nicht: der Warmth-Bot hält
sein Feuer mit stoke-Guard am Leben (FIRE_OUT tritt in seiner Policy nie ein),
die anderen Runner zünden nie. Erwartung: 13× byte-identisch; der Beweis
läuft über das Metrik-Proposal `fire_home_loyalty`
(`metrics/proposed/fire_home_loyalty.md`) — ohne dieses ist der Spec
unvollständig, denn der Ortsbindung-Wert ist in der Bot-Welt unsichtbar.

Sekundär-Kandidaten (beobachtend, keine Versprechen):
- `warmth_stability` (0.72): der Warmth-Bot lebt am Feuer — falls seine Policy
  je ein Feuer verliert, liest sie die Rückkehr-Billigkeit (Revive statt
  Neustart). Erwartet ±0; ein dokumentierter Stream-Shift wäre ehrlich zu
  führen, nicht zu kompensieren (Präzedenz 31.08.).
- `session_depth` (52.5): Glut erzeugt keine neuen Discovery-Einheiten — der
  Stall-Punkt der Bots verschiebt sich nicht. Für echte Spieler verschiebt
  die Rückkehr-Ökonomie die Langeweile-Stelle nicht (das wäre Content-These,
  hier bewusst nicht behauptet).

## Constitution-Check

- Tag-basiertes Crafting unangetastet — Glut ist Weltzustand, kein Crafting-Pfad.
- Kein Rezept, kein Leak: eine generische Meldung, kein Item/Prozess/Tag genannt.
- CLI bleibt; Start unter 1 s (Default-Feld, kein neuer Lade-Pfad); stdlib only.
- Keine Metrik entfernt, umdefiniert oder abgeschwächt; scorecard.py unangetastet.
- Nicht-Ziele: kein Content-Ballon (0/0/0), kein GUI, kein Kampf. Ortsbindung
  als System, nicht als Inhalt — genau die gewollte Wuchsrichtung („das Spiel
  darf wachsen — in Systemen, nicht nur in Inhalten").

## Hinweis an Direktor/Dev

Der Mechanik-Kern ist winzig (ein Zähler, zwei Verzweigungen, drei Konstanten).
Die Wucht liegt in der Achse, die eröffnet wird: **Ortsbindung** — der erste
Grund, an einem Ort zu bleiben oder zurückzukehren, der nicht Node-Regen ist.
Der 28.08.-Befund (Reparatur nach Kollaps strikt schlechter) liest sich mit
Glut anders: Reparatur am *gleichen* Ort wird relativ billiger, das fragile
lokale Optimum bekommt einen Ausweg, der keine Balance-Korrektur braucht.
Fire-Home-Loyalty als Metrik-Proposal schließt die Blende; die Balance-Frei-
heitsgrade (RESIDUE/DECAY/MIN) liegen beim Dev (SPEC-007/013/015-Präzedenz).
