# SPEC-006 — Zweite Entdeckungsschicht: Werkzeug als Zutat (Session-Tiefe)

STATUS: offen · angelegt 2026-08-11 · Quelle: Scorecard 2026-08-10 + Play-Report 2026-08-10 (Metrik `session_depth`)

## Problem
**Metrik:** `session_depth` = 25, stagnierend über drei Messungen (24 → 26 → 25 → 25). Richtung „höher = besser“.
**Befund (präzise, Play 2026-08-10):** Ein survival-sicherer Guided-Runner leert **alle 8 Blueprints + alle 4 Prozesse + alle 15 Item-Templates in ~25–37 Aktionen** (Seeds @28, @24, @37). Unter optimalem Spiel ist die Zahl nicht höher als im naiven Median — das Discovery-Spiel ist nach ~einer halben Stunde fertig, danach existiert **kein Blueprint, kein Prozess, kein Template**, das eine neue Entdeckung verspricht. `_run_session_depth` stoppt nach `stall_limit=15` Aktionen ohne Neuheit (`_novelty_set` = Templates ∪ known_blueprints ∪ known_processes) — und der Stall-Trigger feuert genau dort, wo die flache, endliche Entdeckungsmenge erschöpft ist.

**Warum das eine System-Schwäche ist, kein Content-Mangel:** Alle 8 Blueprints sind von Start an vollständig verfügbar (`min_survival_req=0.0`, nur Rohstoff-Slots aus `FLINT/BONE/STONE/RIGID/FIBER`). Das Discovery-Ziel ist **flach**: Es gibt genau eine Schicht, und die ist klein. Ein entdecktes Werkzeug ist eine Sackgasse — es fügt dem Item-Tag-Raum zwar Tags hinzu (`CHOPPING/CUTTING/PIERCE/SHOVEL` aus `tool_tags`), aber kein Blueprint schließt ein *Werkzeug* als Komponente ein. Discovery erzeugt also in PPP **keine weitere Discovery** — im Gegensatz zu kombinatorischen Entdeckungsspielen, wo jedes Entdeckte selbst wieder Ausgangspunkt neuer Kombinationen ist.

## Mechanik
Aus **Little Alchemy / Alchemy-Klassikern** (jedes entdeckte Element wird selbst zur Zutat — Entdeckung zeugt Entdeckung, der Raum ist selbstverstärkend) und **Don't Starve / Prototyper** (Wissen wird durch *Besitz* einer Komponente freigeschaltet: wer sie hält/gebaut hat, kann erkennen, wofür sie taugt).

Adaptiert als **zweite Entdeckungsschicht**: Ein **craftetes Werkzeug wird zur Zutat eines höherstufigen Blueprints**. Slot-Werte können ein `tool_tag` verlangen (z.B. `CUTTING`, `CHOPPING`, `PIERCE`), das nur ein gebautes Werkzeug trägt — `_slot_satisfied` matcht das bereits über Einzel-Tags, die Engine braucht also keinen neuen Slot-Mechanismus. Dadurch:

1. **Discovery wird gestuft statt flach.** Die Tier-2-Blueprints sind von Start an nicht craftbar, weil die Werkzeug-Tags erst nach dem Bau des Werkzeugs existieren. Der Bau eines Werkzeugs öffnet damit einen **neuen Satz** an Kombinationszielen, die vorher nicht erreichbar waren — Entdeckung verlagert sich in eine zweite Schicht, statt nur mehr vom Gleichen anzuhängen.
2. **Ein Einmal-Reveal hält den Spieler über die alte Erschöpfungsstelle.** Wird ein Werkzeug erstmals gebaut, registriert das Experimentiergedächtnis den neuen `tool_tag` als **bekannte Komponente** und gibt — genau einmal pro neuem Werkzeug-Tag — einen generischen Hinweis: *„Das könnte sich noch mit etwas anderem verbinden lassen.“* Das ist der Don't-Starve-Prototyper-Effekt (Besitz gibt Richtung) und zugleich Little-Achemy-Kaskade. Key: Das signalisiert ein **neues** Discovery-Ziel, das erst nach dem Werkzeugbau existiert — der naive/stallende Runner hat damit etwas zu jagen, statt nach 25 Aktionen still zu laufen.

## Adaption (konkret für PPP)
Dateien: `data/blueprints.json` (Tier-2-Satz), `engine/components.py` (`Player.known_components`), `engine/core.py` (`_create_tool`/`_feedback_message`), `tests/test_engine.py`.

1. **`engine/components.py` — `Player`:** neues Feld `known_components: Set[str]` (Experimentiergedächtnis; von der Constitution ausdrücklich erlaubt). Registriert die `tool_tags`-Namen aller je gebauten Werkzeuge.
2. **`engine/core.py::_create_tool`:** Nach erfolgreichem Bau — für jedes `t in bp.tool_tags`: wenn `t not in player.known_components`, füge hinzu und setze ein einmaliges Reveal-Flag (Reason-String `NEW_COMPONENT:<t>`). Dadurch wird der Hinweis **pro Tag genau einmal** gegeben (kein Dauer-Belehren), analog der SPEC-003-Einmaligkeit.
3. **`engine/core.py::_feedback_message`:** neuer Zweig `NEW_COMPONENT:` → *„Das könnte sich noch mit etwas anderem verbinden lassen.“* (generisch, kein Rezept-Leak — nennt weder Item noch Ziel-Blueprint noch fehlenden Tag). Kommentar nicht vergessen → `feedback_quality`-Konsistenz-Test (Reason↔Label-Vollständigkeit) bleibt grün.
4. **`data/blueprints.json` — kleiner Tier-2-Satz (System-Beweis, nicht Content-Ballon):** 3 stufenweise Blueprints, deren Slots ein `tool_tag` als *einen* Slot verlangen und die bestehende Rohstoff-/Prozess-Kette (knap → knife/fire → cook) nach vorne führen — konkrete Vorschläge:
   - `rope` („Faserseil“): `{cut: "CUTTING", fiber: "FIBER"}` → Ergebnis mit `RIGID_OR_FIBER`-Tauglichkeit (erweiterte Bindungsoption).
   - `spear_cord` („Schnurgebundener Speer“, Stufe über `spear_bound`): `{tip: "SHARP_OR_RIGID", shaft: "RIGID", bind: "CUTTING"}` → nutzt das Messer als Bindewerkzeug-Zutat.
   - `shelter_dry` („Windschutz“): `{frame: "RIGID", cover: "FIBER", build: "CHOPPING"}` → baut auf Axt/CHOPPING auf, gibt Rast-Wert (verlängert Ökonomie-Spanne, adressiert auch die Survival-Decke aus BACKLOG 10.08.).
   Genau **eine** Schicht, nicht drei: Wer nur den Prototyp will, nimmt `rope` + `spear_cord`. Detail-Balance entscheidet der Direktor/Dev während der Umsetzung — der Spec legt das **System** fest (Werkzeug-als-Zutat + einmaliger Komponenten-Reveal + gestufte Erreichbarkeit).
5. **Engine-Matching unverändert:** `_slot_satisfied` matcht `tool_tags` bereits (sie liegen als Item-Tags vor) — es braucht keinen neuen Slot-Typ. Tier-2-Blueprints sind von Start an im `blueprint_reachability`-Zähler erreichbar (Reachability prüft nur, ob es eine legale Tag-Kombination *gibt*), aber für einen naiven Spieler erst nach Werkzeugbau **praktisch** erreichbar — genau die Discovery-Verlagerung.
6. **Constitution-Check:** kein vorgegebenes Rezept (Hinweis nennt nie Material/Rezept), CLI-Text bleibt, stdlib only, keine bestehende Metrik entfernt/abgeschwächt (additiv). Entdeckung wird **vertieft** (neue gestufte Ziele), nicht abgekürzt (wer das Werkzeug nicht selbst baut, bekommt keinen Hinweis). Die Erkenntnis „jedes Entdeckte kann selbst Zutat sein“ ist System-Depth, kein Item-Ballon — bewusst kleiner Tier-2-Satz.

## Akzeptanzkriterien
- Ein Blueprint, dessen Slot ein `tool_tag` (z.B. `CUTTING`) verlangt, ist **erst nach** Besitz eines Werkzeugs mit genau diesem Tag craftbar; vorher scheitert er ehrlich (Reason/Label vorhanden) statt Fehlstart.
- Erstmals gebautes Werkzeug → genau **ein** generischer Hinweis `NEW_COMPONENT:<tag>` („…lässt sich noch mit etwas anderem verbinden“); Wiederholungsbau desselben Tag-Typs bleibt stumm. Kein Rezept-Leak im Text.
- `feedback_quality`-Konsistenz: `NEW_COMPONENT:<tag>` hat ein Label in `_feedback_message`, der Label-Vollständigkeits-Test bleibt grün.
- Tier-2-Ergebnisse sind neue, craftbare, sinnvolle Items (kein Müll); `content_reachable` bleibt 1.0 (kein dangling Template).
- `python -m pytest` bleibt grün (neue Tests: Werkzeug-als-Zutat craftbar nach Tool-Besitz, gescheitert vorher, Einmaligkeit des Reveals, kein-Rezept-Leaken, Tier-2-Ergebnis-Item).
- **`session_depth` in der nächsten Scorecard steigend** (→ Ziel ≥ 30–35, weg vom Stall bei ~25), bei unveränderten Seeds.

## Erwartete Metrik-Wirkung
- **`session_depth`**: **steigend** (primärer, gewollter Effekt). Die zweite Schicht gibt dem stallenden/naiven Runner nach der alten Erschöpfungsstelle ein neues Discovery-Ziel (Werkzeugbau → new-component-Reveal → Tier-2-Kombinationen). Die Entdeckungsmenge wird vertikal statt horizontal erweitert. Ehrliche Skepsis: Die Größe des Effekts hängt am Tier-2-Satz — nur 1–2 Blueprints ergeben wenig; 3 mit jeweils Werkzeug-Gate verschieben die Stall-Grenze realistisch von ~25 auf ~35+.
- `craft_variety`: **leicht stützend** (neue legale Craft-Ergebnisse pro Materialsortiment).
- `discovery_gap`/`forage_pressure`: **keine beabsichtigte Änderung** (discovery_gap ist ohnehin durch REC-001 unzuverlässig; forage_pressure bleibt Probe bis 20.08.). Werkzeug-als-Zutat senkt die Entdeckungslücke nicht gezielt — das ist bewusst SPEC-003/REC-001 vorbehalten.
- `content_reachable`: bleibt 1.0 (alle neuen Templates sauber definiert).
