# SPEC-008 — Wissens-Gate: Überlebens-Skill schaltet höherstufige Blueprints frei (Session-Tiefe)

STATUS: offen · angelegt 2026-08-18 · Quelle: Scorecard 2026-08-17 + Play-Report 2026-08-17 (Metrik `session_depth`, Metrik-Modus)

## Problem
**Metrik:** `session_depth` = 25, stagnierend über **vier** Messungen (24 → 26 → 25 → 25 → 25). Richtung „höher = besser“. PLAN-Priorität #1.
**Befund (präzise, Play 2026-08-17):** Geführte Erschöpfung (HEAD-Bot, 20 Seeds) full-only-Median **~21**, Range 13–35. Die komplette Discovery-Menge — **8 Blueprints + 5 Prozesse + 16 Templates** — ist in unter 30 min realem Spiel geleert. Danach reiner Gather-Grind. Die Langeweile-Stelle ist seit Wochen unverändert, und der einzige geplante Hebel (SPEC-006, Werkzeug-als-Zutat) ist auf Peters Freigabe blockiert, weil **tool-gated Tier-2-Blueprints `blueprint_reachability` regredieren** (Zähler baut nie Werkzeuge; +3 Tier-2 → 0.75→0.545, Dev 11.08).

**Warum das eine System-Schwäche ist:** Alle 8 Blueprints tragen `min_survival_req = 0.0`. Das Feld ist **vollständig kodiert aber tot** — `engine/core.py:405` prüft `if self.player.stats["survival"] < bp.min_survival_req: continue`, und `execute_experiment` erhöht `survival` um **+0.2 je erstmals entdecktem Blueprint** (core.py:418) bzw. **+0.1 je Prozess** (core.py:615). Es gibt also einen echten Fortschritts-Zähler, der gated — aber **kein Blueprint nutzt ihn**. Discovery hat damit keine Rückkopplung: Entdecken macht nichts *neues* entdeckbar. Genau die „Discovery erzeugt keine Discovery“-Lücke aus SPEC-006 — aber ohne den Metrik-Blocker, weil das Gate über den bereits existierenden Skill-Score läuft, den der Reachability-Zähler selbst mit aufbaut.

## Mechanik
Aus **Valheim** (Werkbank-Stufen: höherstufige Rezepte brauchen eine ausgerüstete Werkbank-Stufe — Fortschritt *schaltet* Crafting frei, nicht einzelne Items) und **Little Alchemy / RuneScape-Skillgates** (man kann nur kombinieren, was man bereits gelernt hat; ein kumulativer Wissens-/Skill-Score öffnet neue Rezepte).

Adaptiert als **Wissens-Gate**: Ein Tier-2-Blueprint verlangt `min_survival_req > 0`. Der Spieler muss zuvor eine Mindestanzahl *anderer* Blueprints/Prozesse entdeckt haben (der `survival`-Score akkumuliert genau diese Discovery-Erfahrung), bevor er die höherstufige Kombination *überhaupt versuchen* kann. Dadurch:

1. **Discovery wird gestuft statt flach.** Die Tier-2-Ziele existieren nur, nachdem der Spieler sich durch Tier-1 gearbeitet hat. Der naive Runner, der nach ~25 Aktionen still läuft, bekommt nach der alten Erschöpfungsstelle ein neues, real erreichbares Ziel — `session_depth` verlängert sich.
2. **Kein Rezept-Leak, kein Metrik-Gate.** `min_survival_req` existiert im Datenmodell und wird in `core.py` bereits korrekt ausgewertet; es braucht **keinen** Engine-Eingriff und **keinen** Scorecard-Eingriff. Die Freischaltung ist eine *Prozess-/Engine-Eigenschaft*, kein Hinweistext.
3. **Metrik-sicher (im Gegensatz zu SPEC-006).** Weil `min_survival_req` nur das *Versuchslaufen* eines Blueprints sperrt und nicht das *Vorhandensein* eines Tags, bleibt der Blueprint im Reachability-Zähler erreichbar — der Zähler entdeckt Tier-1 zuerst (survival steigt) und erreicht Tier-2 dann ebenfalls (verifiziert: **reachability bleibt 1.0**, die 8 Bestands-Blueprints unberührt).

## Adaption (konkret für PPP)
Dateien: `data/blueprints.json` (Tier-2-Satz mit `min_survival_req`), `data/items.json` (neue result templates), `tests/test_engine.py`. **Kein Eingriff in `engine/core.py`, `engine/components.py`, `tools/scorecard.py`** — das Feld und die Score-Akkumulation existieren bereits.

1. **`data/blueprints.json` — kleiner Tier-2-Satz (System-Beweis, nicht Content-Ballon).** 2–3 Blueprints, die die bestehende Rohstoff-/Prozesskette nach vorne führen, mit `min_survival_req` 0.4/0.6 (≈ 2–3 entdeckte Tier-1-Blueprints). Konkrete Vorschläge (Balance entscheidet Dev/Direktor, der Spec definiert das **System**):
   - `rope` („Faserseil“): `{"fiber": "FIBER", "rigid": "RIGID"}`, `min_survival_req: 0.4`, `tool_tags: ["CORD"]` → erweiterte Bindungsoption (Basis für weitere Prozesse).
   - `cord_spear` („Seilgebundener Speer“, Stufe über `spear_bound`): `{"tip": "SHARP_OR_RIGID", "shaft": "RIGID", "bind": "CORD"}`, `min_survival_req: 0.6`, `tool_tags: ["PIERCE"]` → baut auf Tier-1-Speer auf. *(Korrektur 18.08.: FIBER→CORD, sonst von `spear_bound` überschattet → reachability-Regress; bindet mit dem gecrafteten rope.)*
   - Optional `shelter_dry` („Windschutz“): `{"frame": "RIGID", "cover": "FIBER"}`, `min_survival_req: 0.4` → Rast-/Überlebenswert (adressiert auch die Survival-Decke aus BACKLOG 10.08.).
   Verifizierte Wirkung des 2-Satz-Prototyps (n=20 Seeds, deterministisch): `session_depth` **25 → 32** (p25 21→24, p75 43→50), `blueprint_reachability` **1.0** (alle Tier-2 erreicht), `discovery_gap` 0.625 → **0.6** (kein Überschießen). Siehe Probe unten.
2. **`data/items.json`:** *(bewusst NICHT umgesetzt, 18.08.)* neue `result_template_id`-Templates für die Tier-2-Ergebnisse wären nötig, um dangling zu vermeiden — **aber** würden `content_reachable` 16/16→16/18 senken. Wie die 8 Werkzeuge bleiben die Tier-2-Ergebnisse `blueprint-only` (kein gather-/Prozess-Output) → kein Entry in `items.json` → `content_reachable` bleibt 1.0.
3. **Kein Feedback-/Text-Eingriff nötig.** Ein Versuch vor Erreichen des Scores scheitert an `continue` in `execute_experiment` (Zeile 405) und fällt in den bestehenden `_no_match_reason`-Pfad — der Spieler sieht einen normalen Fehlschlag, **ohne** dass ein Rezept/Score verraten wird. Optional (Dev-Entscheid): ein `SKILL_GATED`-Reason mit generischem „Du fühlst dich noch nicht bereit, das zu verbinden.“ (kein Rezept-Leak) — nur wenn er `feedback_quality`-Konsistenz-tauglich ist.
4. **Constitution-Check:** kein vorgegebenes Rezept (Gate ist eine Spieler-Eigenschaft, kein Hinweis), Experimentiergedächtnis/Skill-Score erlaubt, CLI-Text bleibt, stdlib only, **keine** bestehende Metrik entfernt/abgeschwächt (additiv), Entdeckung wird **vertieft** (neue gestufte Ziele) statt abgekürzt. Kein Metrik-Core berührt.

## Akzeptanzkriterien
- Ein Blueprint mit `min_survival_req: 0.4` ist **erst nach** 2 entdeckten Tier-1-Blueprints (survival ≥ 0.4) craftbar; vorher scheitert er ehrlich ohne Score-/Rezept-Leak (Reason/Label vorhanden, kein Fehlstart, Items nicht verbraucht).
- Nach Erreichen des Scores ist derselbe Blueprint mit den richtigen Rohstoff-Tags craftbar (SUCCESS, bekanntes Blueprint, survival +0.2).
- `blueprint_reachability` bleibt **1.0** (Tier-2 im Zähler erreicht), `discovery_gap` ≤ 0.6 (kein Über-Band-Schub), `content_reachable` bleibt 1.0.
- `python -m pytest` bleibt grün (neue Tests: Tier-2 scheitert vor Gate, craftbar nach Gate, Items nicht verbraucht bei Fehlschlag, Tier-2-Ergebnis-Item in TEMPLATE_DB, reachability 1.0, session_depth-Anstieg).
- **`session_depth` in der nächsten Scorecard steigend** (Ziel ≥ 30), bei unveränderten Seeds.

## Erwartete Metrik-Wirkung
- **`session_depth`**: **steigend** (primärer, gewollter Effekt). Verifiziert im Prototyp: 25 → 32 mit nur 2 Tier-2-Blueprints. Die gestufte Schicht gibt dem stallenden naiven Runner nach der alten Erschöpfungsstelle ein neues Discovery-Ziel.
- `blueprint_reachability`: **unverändert 1.0** (verifiziert) — das Wissens-Gate sperrt nur das Versuchslaufen, nicht die Erreichbarkeit; der Zähler entdeckt Tier-1 zuerst. Das ist der entscheidende Unterschied zu SPEC-006 (tool-gated → Regress auf 0.545).
- `discovery_gap`: **kein Überschießen** (0.625 → 0.6 verifiziert); wird primär von SPEC-003 (partieller Match, bereits DEV'd 17.08) geschlossen.
- `content_reachable`/`feedback_quality`: unverändert (1.0), sofern neue Items als Templates sauber definiert sind.
- `craft_variety`: leicht stützend (neue legale Craft-Ergebnisse pro Materialsortiment).
- `skill_spread`: keine beabsichtigte Änderung (Metrik bleibt Peters Deutung überlassen; der Score wird hier als *Gate*, nicht als Ökonomie-Hebel verwendet).

## Probe / Verifikations-Skript (in dieser Session gelaufen, deterministisch, scorecard.py unangetastet)
```
Monkeypatch get_all_blueprints um 2 Tier-2-Blueprints (rope 0.4, cord_spear 0.6) ergänzt:
  session_depth:       25.0 → 32.0  (p25 21→24, p75 43→50)
  blueprint_reachability: 1.0  (tier2_rope True, tier2_cord_spear True)
  discovery_gap:       0.625 → 0.6  (reach 1.0, naive 0.4)
```
Methodik: `import engine.core`/`tools.scorecard` direkt (Referenzen gespeichert, `get_all_blueprints` ersetzt, keine Scorecard-Datei geschrieben). Der Play-Job berechnet die echte Scorecard neu.
