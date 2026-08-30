# SPEC-003 — Partieller Match: Erkennung von „Beinahe-Treffern" (Discovery)

STATUS: erledigt (Dev 17.08., NEAR_MISS; Tier-2-Volldeckung 26.08.) · angelegt 2026-08-04 · Quelle: Scorecard 2026-08-03 (Band-Metrik `discovery_gap`)

## Problem
**Metrik:** `discovery_gap` = 0.5 (Band 0.2–0.6, obere Kante). Zerlegt: `blueprint_reachability` = 1.0 (Orakel erreicht alles), `naive_discovery_rate` = 0.5, **`naive_p25` = 0.0, `naive_p75` = 1.0**.
**Befund:** Die Lücke ist an der oberen Bandkante — nahe daran, unentdeckbar zu sein (ab 0.6). Der Median verdeckt die eigentliche Schwäche: In der unteren Hälfte der Naiv-Läufe (p25) **findet ein Spieler in 150 Aktionen gar keinen Blueprint** (0.0), während das Orakel 100 % erreicht. Ein naiver Spieler kombiniert zufällig und bekommt bei Fehlschlag zwar den fehlenden Tag-Typ genannt (seit feedback v2), aber nie bestätigt, dass seine *vorhandene* Teilkombination überhaupt auf dem richtigen Weg ist. Er hat keine Idee, ob er „kalt" oder „warm" ist, und gibt auf. SPEC-001/002 adressieren Vielfalt und Content, aber keine dieser Mechaniken senkt die Entdeckungslücke selbst.

## Mechanik
Aus *Don't Starve* (Prototypen-Maschine: Rohstoffe, die man in die Hand nimmt, offenbaren, was daraus werden kann) + *Ancestors* (neuronales Entdeckungssystem: wiederholte/nahe Versuche verstärken das Wissen). Adaptiert als **partielle Match-Erkennung**: Statt ein Rezept zu verraten, erkennt die Engine, wenn eine Fehlschlag-Kombination **mindestens zwei der gesuchten Slots** eines noch unbekannten Blueprints bereits enthält, und bestätigt dem Spieler nur, dass diese Teilmenge *zusammengehört*. Das konvergiert naive Spieler, ohne etwas zu schenken — wer die richtigen Materialien nicht selbst besitzt, bekommt keinen Hinweis.

Kontrast zu SPEC-002: SPEC-002 nennt bei *bekanntem* Ziel-Tag den fehlenden Tag-Typ. SPEC-003 gibt bei *unbekanntem* Blueprint ein reines Ja/nein-Signal auf die gehaltene Teilmenge — es bestätigt den Weg, verrät aber weder das fehlende Item noch das Rezept.

## Adaption (konkret für PPP)
Dateien: `engine/core.py` (`execute_experiment`/`_no_match_reason`), `engine/components.py` (`Player.known_blueprints` + neues `near_misses: Set[str]`), `tests/test_engine.py`.

1. In `_no_match_reason` / `execute_experiment` (core.py, Zeilen ~182–232): Vor der generischen `NO_MATCH`-Antwort prüfen — für jeden nicht bekannten Blueprint (`bp_id not in player.known_blueprints`):
   - Anzahl der Slots zählen, deren Tag in der gewählten Kombination enthalten ist (`overlap`).
   - Wenn `overlap >= 2` und `overlap < len(bp.slots)`: Blueprint als „Beinahe-Treffer" werten.
2. Neues Feld `Player.near_misses: Set[str]` (components.py): Merkt sich Blueprint-IDs, die der Spieler schon einmal ≥2/3 getroffen hat (Experimentiergedächtnis — von der Constitution ausdrücklich erlaubt).
3. Meldung nur, wenn der Treffer neu ist (`bp_id not in player.near_misses`), und als **generischer Bestätigungstext**, der kein Rezept leaket — z. B.: *„Einige dieser Dinge scheinen zusammenzugehören, aber es fehlt noch etwas."* Danach wird `near_misses.add(bp_id)`; weitere Versuche derselben Richtung bleiben stumm bis zum echten Craft (keine Dauer-Belehrung).
4. `_feedback_message` (core.py ~35): wird dadurch nicht verändert — der Beinahe-Treffer-Text ist ein eigener Reason (`NEAR_MISS:<bp_id>`), damit `feedback_quality` die Konsistenz-Messung trägt.
5. Kein Rezept-Leaking: Es wird nie genannt, *welcher* Tag fehlt — nur, dass die gehaltene Teilmenge plausibel ist. Wer HARD+RIGID ohne FIBER hat, hört nur „gehört zusammen", nicht „es fehlt etwas Faseriges".
6. Konstitution: kein vorgegebenes Rezept; reiner Hinweis/Experimentgedächtnis (erlaubt); CLI-Text bleibt; stdlib only.

## Akzeptanzkriterien
- Fehlschlag mit 2 von 3 Slots eines unbekannten Blueprints → Reason `NEAR_MISS:<bp_id>`, Meldung „gehören zusammen / es fehlt noch etwas", OHNE den fehlenden Tag zu nennen.
- Volltreffer (alle Slots) bleibt unverändert `SUCCESS` + Blueprint-Discovery.
- Redundanz: derselbe Beinahe-Treffer wird nur **einmal** gemeldet (danach still bis zum echten Craft).
- `naive_discovery_rate` in einem kontrollierten Run: p25 > 0.0 (kein „findet nichts"-Schwanz mehr bei identischem Seed-Satz).
- `python -m pytest` bleibt grün (neue Tests für NEAR_MISS-Trigger, Einmaligkeit, kein-Rezept-Leaken).

## Erwartete Metrik-Wirkung
- `discovery_gap`: 0.5 → **~0.3–0.4** (Mitte des Bands 0.2–0.6). Steigt die naive Rate von 0.5 auf ~0.6–0.7, sinkt die Lücke entsprechend. Bleibt **im Band**: unter 0.2 fällt sie nicht, weil der Hinweis erst nach eigenständigem Besitz von ≥2 passenden Materialien feuert — keine Hand-Führung ab Start.
- `naive_discovery_rate` p25: 0.0 → > 0.0 (der „findet nichts"-Schwanz wird gezielt geschlossen).
- `session_depth`: Nebeneffekt steigend (Spieler experimentiert länger weiter, statt bei kaltem Gefühl aufzugeben).
