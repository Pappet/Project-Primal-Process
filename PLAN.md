# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand
Die Messung ist ehrlich: `blueprint_reachability` **1.0** (alle 10 Blueprints erreichbar, REC-001), `content_reachable` **1.0** (18/18 nach SPEC-009), `discovery_gap` mit SPEC-003 zurück **im Band** (0.625→**0.6**, aber exakt auf der oberen Bandkante = „kaum entdeckbar“-Grenze). Parallel hat SPEC-009 (Verletzung & Heilung) eine zweite, aktive Überlebensökonomie geliefert (`recovery_stability` 0.375, im Band), und `craft_variety` ist auf **3.5** gestiegen. Aber der Nordstern bewegt sich nicht: **`session_depth` bleibt 25 flach** — die komplette entdeckbare Welt (10 BPs + 5 Prozesse) leert sich in ~15–25 geführten Aktionen; danach ist es Grind. `skill_spread` (0.216) und `feedback_quality` (0.916) sind keine Spiel-Regresse, sondern warten auf Peters Metrik-Entscheide. Der `forage_pressure`-Wert ist definitionsabhängig zu hoch (0.707, Band 0.1–0.5, Probe seit 20.08. beendet) — Entscheid, kein Tuning-Ziel.

## Was als nächstes besser werden muss
1. **Die Langeweile-Stelle verschieben — `session_depth` (25 → höher).** Der Hebel ist die echte zweite Discovery-Schicht (SPEC-006: Werkzeug als Zutat), aber er ist auf **tool-aware reachability (Peters Freigabe)** blockiert, und der naive `session_depth`-Bot ist strukturell blind für gestufte Gates (SPEC-008 lieferte die Schicht, ohne die Zahl zu bewegen). Ohne Peters Metrik-Entscheid (Recalibrierung des Bots = Scorecard-Kern) wird `session_depth` nicht steigen; deshalb: **Decision-Paket fertigstellen** (Optionen + Wirkungs-Schätzung gemessen, nicht geraten), damit Peter schnell entscheiden kann — kein Content-Ballon, um die Zahl zu fälschen.
2. **`discovery_gap` stabil im Band halten, weg von der 0.6-Kante (0.6, Band 0.2–0.6).** Jede weitere Druck-/Überlebensmechanik (forage, warmth, recovery) schiebt naive Bots Richtung Stall → Gap droht über die Kante zu kippen. Konkreter, additiver, leakt-freier Hebel liegt in der Discovery selbst: **SPEC-003-Deckungslücke schließen** — die 2-Slot-Blueprints (`spear`, `spear_bound`) können aktuell *nie* einen Near-Miss-Hinweis geben (`2 ≤ overlap < len` ist für len=2 nie wahr). Diese erweitern → naive Trefferquote steigt → Gap wandert in die Bandmitte statt auf der Kante zu hängen. Metrik, die sich bewegen soll: `discovery_gap` (Richtung: weg von der oberen Kante, im Band).
3. **`forage_pressure`-Probe schließen (Probe seit 20.08. beendet).** Wert 0.707 über Band 0.1–0.5 — aber die Definition `stock < max_stock` zählt jeden Teilerfolg als Knappheit und sättigt prinzipbedingt nahe 1.0. Der Sensor misst aktuell „Node nicht bei 100 %“, nicht „Spieler fühlte Grind“. Entscheid an Peter: **Definition/Band anpassen** (Metrik-Core → Freigabe) oder Band als Referenz/Draft akzeptieren. Kein Spieldesign-Re-balancieren auf einen Messwert-Artefakt. Metrik, die sich bewegen soll: `forage_pressure` (Band-Entscheidung).

## Tasks
> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.
> `[ ]` offen · `[~]` in Arbeit · `[x]` erledigt

- [x] **SPEC-009 — Verletzung & Heilung.** ✅ DEV 20.08. → siehe unten „Erledigt“. `recovery_stability` in Probe (bis 03.09.), **kein Ziel**.
- [x] **SPEC-008 — Wissens-Gate Tier-2.** ✅ DEV 18.08., Spec-Datei nachgezogen 21.08. `session_depth` blieb 25 — Metrik-Frage (s. Ziel 1). **Kein Content-Inflation-Fix.**
- [x] **SPEC-003 — Partielle Match-Erkennung (Near-Miss).** ✅ DEV 17.08.
- [x] **REC-001 — Reachability-Zähler kalibriert.** ✅ Freigegeben 14.08., angewendet.
- [ ] **DISCOVERY-LÜCKE: Near-Miss für 2-Slot-Blueprints erweitern (`discovery_gap` weg von der 0.6-Kante).** NEU (aus Ziel 2). SPEC-003 kann für len=2 (`spear`, `spear_bound`) nie `NEAR_MISS` feuern — Lücke in der Discovery-Hilfe. Additive, leakfreie, ohne Rezept-Verrat. **Akzeptanz:** die 2-Slot-Blueprints liefern bei ≥1 gehaltenem + unbekanntem Rest-Material den generischen „gehört zusammen“-Hinweis (kein Tag/Rezept-Leak); naive Trefferquote steigt, `discovery_gap` bleibt ≤0.6 (kein Überschießen); pytest grün. Quelle: SPEC-003-partial-match-recognition.md.
- [ ] **SESSION-DEPTH-ENTSPERRUNG — Entscheid-Grundlage für Peter (`session_depth`).** NEU (aus Ziel 1). Deliverable ist der fertige Entscheid-Block (nicht die Implementierung): messbare Option **A** (tool-aware reachability, Zähler baut Werkzeuge als Vorschritt → SPEC-006 umsetzbar, REC-001-Familie) vs **B** (session_depth-Bot ziel-bewusst kalibrieren, Scorecard-Core) vs **C** (accept: Gate bleibt, Zahl flach als ehrliches Signal). **NICHT `tools/scorecard.py` anfassen.** Akzeptanz: `proposals/`-Datei mit gemessener Wirkung je Option (inline-Probe, Scorecard-Dateien unangetastet) + DECISIONS-Eintrag; Peters Entscheid abgewartet. Quelle: JOURNAL 18.08./19.08./21.08., DECISIONS.md.
- [ ] **forage_pressure-Nachlese (Peters Freigabe, kein Ziel).** Probe seit 20.08. beendet. Wert über Band (0.707 vs 0.1–0.5), definitionsbedingt (Artefakt), darum keine Tuning-Forderung ans Spiel. Akzeptanz: Peters Entscheid Definition/Band eingegangen; falls Definition bleibt, als „hoher, aber sensorischer Wert“ im Journal dokumentiert.
- [ ] **skill_spread-Deutung — klären, nicht fixen, (Peter-Entscheid A/B/C).** Metrik bleibt unangetastet (Constitution). Akzeptanz: Freigabe eingegangen + angewandt, keine stille Änderung.
- [ ] **feedback_quality-NEAR_MISS-Blindstelle (Peter-Entscheid).** `_expected_fragment` kennt `NEAR_MISS:` nicht → zählt als uninformativ (1.0→0.916). Kein Spielfehler; der Near-Miss-Text ist *absichtlich* vage. Entscheidung: ehrliches Mapping (Metrik-Core → Freigabe) oder Kosten akzeptieren. Akzeptanz: Peters Entscheid dokumentiert. **Nicht** still in `_expected_fragment` eingreifen.
- [~] *(beobachtend)* **warmth_stability** (Probe bis 27.08.) — 0.460 im Band, p25=p75 flach. Vor Probensende keine Aktion.
- [~] *(beobachtend)* **recovery_stability** (Probe bis 03.09.) — 0.375 im Band, p25=p75 flach (wie warmth). Vor Probensende keine Aktion.

**Erledigt (Kontext):**
- [x] **SPEC-005** — Mengen-basiertes Mehrfach-Slot-Crafting (Stack quantity füllt N Slots).
- [x] **SPEC-007** — Feuer & Wärme (Location-Feuer, Stoke, `fur_cloak`, `warmth_stability` in Probe).
- [x] **SPEC-004** — Resource depletion.
- [x] **SPEC-002** — Blueprint-Familien.

---

*Nächste Scorecard-Kontrolle: nächster Play-Job. Plan-Neufassung: nächster Direktor (So).*