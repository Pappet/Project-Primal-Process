# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand
Die Messung ist jetzt **ehrlich**: mit REC-001 (angewendet 14.08.) löst der Reachability-Zähler Tag-Familien auf → `blueprint_reachability` 1.0 (alle 8 Blueprints erreichbar), und der wahre `discovery_gap` steht bei **0.625 — über dem Band 0.6** (naive Spieler finden nur 0.375 des Erreichbaren). Das ist das dunkelste Signal: die Discovery ist aktuell faktisch schwer, nicht leicht. Gleichzeitig ist **`session_depth` 25 flach seit vier Messungen** — die Langeweile-Stelle unverändert: 8 Blueprints + 5 Prozesse + 16 Templates sind in unter 30 min realem Spiel geleert (geführte Erschöpfung ~31 Aktionen). Alles andere (Einstieg 34.5, `craft_variety` 3.0, `content_reachable` 1.0, `feedback_quality` 1.0) ist gesund oder an der Decke.

## Was als nächstes besser werden muss
1. **Discovery wieder auffindbar machen — `discovery_gap`** (0.625 über Band → zurück in 0.2–0.6). Der über-Band-Wert heißt: ein naiver Spieler findet deutlich weniger, als erreichbar wäre (0.375 vs. 1.0). **SPEC-003 (partieller Match) reaktivieren** — es ist die *einzige* Discovery-Mechanik, die die Lücke schließt statt sie zu vergrößern, und braucht KEIN Metrik-Gate (reines Feedback/Experimentiergedächtnis). Die frühere Aussetzung (`Überführung-Risiko`) galt Content-Mechaniken, nicht Gap-schließendem Feedback; mit ehrlichem Zähler ist die Wirkung jetzt verifizierbar.
2. **Langeweile-Stelle verschieben — `session_depth`** (25 → ≥30). Der eigentliche Hebel bleibt **SPEC-006** (Werkzeug-als-Zutat), aber er ist auf **tool-aware reachability (Peters Freigabe)** blockiert und würde den ohnehin über-Band `discovery_gap` weiter anheben — also erst nach Schritt 1. Der sofort abarbeitbare Weg in Richtung Entdeckungstiefe ist SPEC-003 (Spieler geben nicht mehr „kalt" auf → experimentieren länger weiter).
3. **skill_spread-Deutung klären — `skill_spread`** (0.216, „höher besser"). Kein Blind-Fix: Befund steht (10.08.) — es ist eine **gehobene Einsteiger-Decke**, kein Tiefen-Regress. Es braucht Peters Metrik-Deutungs-Entscheid (A/B/C in DECISIONS.md); bis dahin Metrik unangetastet, nur beobachtend.

## Tasks
> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.
> `[ ]` offen · `[~]` in Arbeit · `[x]` erledigt

- [x] **SPEC-003 — Partielle Match-Erkennung (`discovery_gap` in Band).** ✅ DEV 17.08. Fehlschlag mit ≥2/3 Slots eines unbekannten Blueprints → generisches `NEAR_MISS:<bp_id>` (Ja/nein auf die Teilmenge, kein Rezept-/Tag-Leak); einmalig pro Blueprint (Experimentiergedächtnis `Player.near_misses`), danach still bis zum echten Craft; bekannte Blueprints behalten das konkrete Merkmal (SPEC-002 vor SPEC-003). Quelle: SPEC-003-partial-match-recognition.md.
- [ ] **SPEC-008 — Wissens-Gate: `min_survival_req`-gestufte Tier-2-Blueprints (`session_depth`).** Der tote `min_survival_req`-Filter (alle Blueprints 0.0, aber `core.py:405` prüft + `survival` akkumuliert +0.2/Discovery) wird als zweite Discovery-Schicht aktiviert: 2–3 Tier-2-Blueprints (z.B. `rope` 0.4, `cord_spear` 0.6), erst nach ≥2 entdeckten Tier-1-Blueprints craftbar. **Metrik-sicher** (im Gegensatz zu SPEC-006): verifiziert reachability bleibt 1.0, `session_depth` 25→32 (n=20, deterministisch). Kein Metrik-Core/Engine-Eingriff nötig — nur `data/blueprints.json` + `data/items.json` + Tests. Quelle: SPEC-008-survival-gate-tier2.md.
- [ ] **SPEC-006 — Werkzeug als Zutat (`session_depth`).** ⚠️ **Blockiert — braucht Peters Freigabe (tool-aware reachability, Metrik-Core).** Bleibt zurückgestellt: mit `discovery_gap` über Band (0.625) würde eine Tier-2-Schicht die Lücke weiter anheben und `blueprint_reachability` regredieren. Erst nach SPEC-003 + stabiler Gap neu bewerten. Optionen A/B/C in DECISIONS.md / JOURNAL 11.08.
- [~] *(beobachtend)* **forage_pressure (Probe bis 20.08.)** — kein Ziel. Erstwert 0.707 über Band 0.1–0.5 bleibt definitorisch verdächtig. Nach Probezeitende (in 4 Tagen) entscheiden: Definition/Band anpassen (braucht Peter) oder Spiel reiben lassen. Beobachten, nicht steuern.
- [~] *(beobachtend)* **warmth_stability (Probe bis 27.08.)** — kein Ziel. Erstwert 0.460 im Band, p25=p75 identisch (flache Policy). Nach Probeende prüfen, ob Streuung informativer wird. Beobachten, nicht steuern.
- [ ] **skill_spread-Deutung — klären, nicht fixen.** Metrik bleibt unangetastet (Constitution). Befund steht; es wartet auf Peters Entscheid (A/B/C in DECISIONS.md). Akzeptanz: Peters Freigabe eingegangen und angewandt, keine stille Änderung.

**Erledigt (Kontext):**
- [x] **REC-001 — Reachability-Zähler kalibriert.** ✅ Freigegeben 14.08. + angewendet. `_pair_slots` löst Familien → `blueprint_reachability` 0.75→1.0, `discovery_gap` ehrlich 0.625 (über Band). Kein Spielverhalten geändert.
- [x] **SPEC-003 — Partielle Match-Erkennung.** ✅ Dev 17.08. (siehe oben im Tasks-Block). `discovery_gap`-Hebel ohne Metrik-Gate.
- [x] **SPEC-005 — Mengen-basiertes Mehrfach-Slot-Crafting.** Stack `quantity N` füllt N identische Slots; `NOT_ENOUGH_QUANTITY`-Feedback; kein Rezept-Leak; pytest grün.
- [x] **SPEC-007 — Feuer & Wärme.** Aktives Location-Feuer (FIRE_HEAT 40), Stoke, `fur_cloak` (CLOTHING 0.6), hartes `required_tag_in_env`. `content_reachable` 1.0 (16/16). `warmth_stability`-Metrik ergänzt (Probe bis 27.08.).
- [x] **skill_spread-Regress-Rückwärtsprüfung.** Befund 10.08.: kein Tiefen-Regress, gehobene Einsteiger-Decke; Metrik-Interpretation an Peter delegiert (DECISIONS A/B/C).

---
*Nächste Scorecard-Kontrolle: nächster Play-Job. Plan-Neufassung: nächster Direktor (So).*