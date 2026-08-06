# SPEC-004 — Ressourcenerschöpfung & zeitbasierte Regeneration (Foraging)

STATUS: offen · angelegt 2026-08-06 · Quelle: Play-Report 2026-08-05 (Explorations-Modus, kein Metrik-Anker)

## Problem
**Befund (Play 2026-08-05, der schärfste):** Das Spiel hat eine Langeweile-Stelle. Die komplette Entdeckungsmenge (2 Blueprint-Familien + 4 Prozesse + ~12 Templates) ist in ~40 Aktionen geleert; danach gibt es kein weiteres Ziel, nur "sinnloses Sammeln". Geführt erreichen Spieler alles und langweilen sich, naive scheitern am Ressourcen-Flaschenhals und langweilen sich ebenfalls.

**Systemische Ursache hinter dem Symptom:** Das Sammeln ist *unendlich und gratis* — `GameEngine.gather()` rollt für jeden Node bei jedem Aufruf gegen eine feste `node.chance`, nie abnehmend. Ein Node wirft ewig ab, egal wie oft man ihn leert. Daraus folgt: (a) es gibt **keinen Grund für Ortswechsel** — jeder Ort ist jederzeit gleichwertig voll; (b) **Zeit hat keinen Sammel-Wert** — Fortschritt ist reine Aktionenzahl, nicht Planung; (c) es gibt **keine Wiederkehrmotivation** — kein Grund, später an einen bekannten Ort zurückzukehren. Terrain (`locations`), Zeit (`tick_counter`/`_advance_time`) und Wetter existieren, sind aber für das Sammeln bedeutungslos. Das macht `session_depth` strukturell kurz, nicht wegen fehlender Inhalte, sondern weil das Foraging-System keine Entscheidungen kennt.

Das ist eine **System**-Schwäche: keine Metrik verlangt hier Arbeit, aber das Spiel als System hat eine flache, unendliche Ressourcensammel-Ebene ohne Kosten, Wahl oder Zeit-Bindung.

## Mechanik
Aus *UnReal World* (selbsterhaltende Welt: was du erntest, wächst nicht sofort nach — man rotiert und pflanzt/überlässt Flächen) und *Vintage Story* / *Project Zomboid* (Ressourcen-Nodes erschöpfen sich und respawnen über Zeit). Adaptiert als **vorratsbasierte Nodes mit Erschöpfung + zeitbasierter Regeneration**:

- Jeder `ResourceNode` hat einen **Vorrat** (`stock`, startet = `max_stock`). Eine erfolgreiche Ernte **reduziert** den Vorrat.
- Die **Erfolgswahrscheinlichkeit skaliert mit dem Vorratsanteil**: `eff_chance = node.chance * (stock / max_stock)`. Volle Stelle = normale Chance, geleerte Stelle = nichts mehr.
- Vorrat **regeneriert über verstrichene Spielzeit** (`_advance_time`), nicht über Aktionen — wer eine Stelle leerernt und woanders hingeht oder wartet, findet sie später wieder fülliger. Ort und Zeit werden so zu echten Ressourcen.
- Eine geleerte Stelle bleibt **bis zur Erholung** leer und sagt das dem Spieler ehrlich ("Diese Stelle ist erschöpft."), statt still "nichts" zu liefern.

Kern-Effekt: Das System erzwingt **Rotation und Rückkehr** statt unendlichem Glauben an denselben Node — eine Kosten-/Wahl-Dimension, die das Foraging bisher komplett entbehrt. Es vertieft Entdecken (eine lebende, reagierende Welt), ohne einen einzigen neuen Content-Item zu brauchen — gegen das Nicht-Ziel "Content-Menge als Selbstzweck".

## Adaption (konkret für PPP)
Dateien: `data/locations.py` (`ResourceNode`), `data/locations.json` (per-Node-Werte), `engine/core.py` (`gather()`, `_advance_time()`, `_feedback_message`), `tests/test_engine.py`.

1. **`data/locations.py` — `ResourceNode` erweitern:** neue Felder `max_stock: float = 10.0` und `regen_per_tick: float = 0.05`, plus veränderlicher Zustand `stock: float` (im `__init__` auf `max_stock` initialisiert; `_node_from_data` reicht sie durch). Standardwerte so, dass Bestandsinhalt ohne JSON-Zwang funktioniert; explizite Balancen kommen ins JSON.

2. **`data/locations.json` — pro-Node-Balance:** Werte ergänzen. Prinzip: **Flaggschiff-Ressourcen (flint_shard, bone) knapp und langsam** (`max_stock` klein, `regen_per_tick` niedrig — ein Ort soll nicht Dauerlieferant sein), **Grundstoffe (stick, pebble, plant_fiber) großzügig** (`max_stock` hoch, `regen` schnell — nicht jedes Stöckchen wird zum Gate). Damit wird Knappheit gezielt **auf die Konflikte gelegt**, die das Spiel schon hat (der `flint`-Bottleneck aus Play 05.08.), statt flächig zu nerven.

3. **`engine/core.py` — `gather()`:** Vor dem Würfeln `eff_chance = node.chance * (stock / max_stock)`; Roll; bei Erfolg zusätzlich `_advance_time`-Bedarf, Vorrat reduzieren um eine Ernte-Portion (`node.harvest_cost`, default 1.0, gedeckelt bei 0). Ist `stock <= 0`, überspringt der Node die Ernte und loggt eine eigene Meldung mit neuem Reason `DEPLETED` (damit `feedback_quality` die Reason↔Label-Konsistenz auf diesem Zweig trägt).

4. **`engine/core.py` — Regeneration:** In `_advance_time` (nach `_update_weather`) über alle `self.locations.*.nodes` iterieren: `node.stock = min(node.max_stock, node.stock + regen_per_tick * ticks)`. Dadurch regenerieren sich auch **andere** Orte während man unterwegs handelt — Zeitspanne zwischen zwei Besuchen bestimmt den Füllstand.

5. **`_feedback_message`:** neuer Zweig `DEPLETED` → *"Diese Stelle ist erschöpft."* (ggf. ergänzt "Komm später zurück."). Kein Rezept-Leak, kein Ortspunkt verraten.

6. **Engine-Zustand bleibt pro-Instanz** (Engine erzeugt frische `LocationDef`-Objekte je `GameEngine`) — kein Cross-Session-Bleed, deterministisch pro Seed, im Sinne des scorecard-Frameworks.

7. **Constitution-Check:** kein vorgegebenes Rezept; CLI-Text bleibt; stdlib only; entfernt/abschwächt **keine** bestehende Metrik (siehe Metrik-Wirkung) — nur eine **neue** Metrik vorgeschlagen. Vertieft Entdecken (lebende Welt, Rotations-Entscheidung), keine Content-Deko.

## Akzeptanzkriterien
- Wiederholtes Sammeln am selben Node führt zur Erschöpfung: ab `stock <= 0` liefert der Node nichts mehr, mit Reason `DEPLETED` und Meldung "Diese Stelle ist erschöpft." (nie stilles "nichts").
- Regeneration: `_advance_time` mit N Ticks erhöht `stock` jedes Nodes bis `max_stock`; ein erschöpfter Node wird nach genügend Zeit wieder erntbar.
- Erfolgswahrscheinlichkeit skaliert mit `stock/max_stock` (voller Vorrat = `chance`, leerer = 0).
- Über-Ernten **eines** Ortes über eine Session hinweg hungert ihn aus (kann man nicht denselben Node unendlich melken) — gibt es einen anderen, volleren Ort, lohnt der Wechsel.
- `feedback_quality`-Konsistenz: `DEPLETED` hat ein Label in `_feedback_message`, der Label-Vollständigkeits-Test bleibt grün.
- `python -m pytest` bleibt grün (neue Tests: Erschöpfung auf wiederholtes Gather, Regeneration stellt wieder her, Chance-Skalierung, `DEPLETED`-Reason↔Label, Determinismus über Seed-Läufe).

## Erwartete Metrik-Wirkung
- `session_depth`: **steigend** (primärer, gewollter Effekt) — Rückkehr-Trips und Warten auf Regeneration verlängern den Horizont, bis "nichts Interessantes mehr passiert". Das ist die direkte Antwort auf die Langeweile-Stelle. Skepsis ehrlich: der Effekt tritt nur ein, wenn der naïf/angeführte Agent Regeneration tatsächlich nutzt — sonst ist es nur zusätzliche Reibung. (Zu beobachten, nicht versprochen.)
- `discovery_gap`, `craft_variety`, `content_reachable`, `feedback_quality`: **keine beabsichtigte Änderung.** Erschöpfung hilft naiven Spielern nicht, Blueprints zu finden, und fügt keine Craft-Typen/Items hinzu. Das ist gewollt — SPEC-004 ist bewusst eine der Mechaniken, die **keine** bestehende Metrik bewegt, sondern das System als Ganzes vertieft (Nachhaltigkeit/Zeit-Horizont statt Fitnesszahl).
- `skill_spread`: indirekt möglich (überlebensfähig ist, wer Knappheit rotiert) — kein Zielband, nur Beobachtung.

## Metrik-Vorschlag
`metrics/proposed/forage_pressure.md` — neue Messung, zeigt ob Knappheit tatsächlich *gefühlt* wird (Entscheidungsdruck), nicht trivial zu heben. Ohne sie ist der Spec nicht verifizierbar, daher dort dokumentiert.
