# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Play, Direktor).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-08-26 — [Play] Erste PLAY-Lesung unter v2-Re-Baseline: session_depth 64.5, echter Boredom-Punkt bleibt ~15

### Headline
Erste PLAY-Lesung nach dem Dev-Land 25.08. des ziel-bewussten `session_depth`-v2-Bots. **Re-Baseline, kein Fortschritt** (Peter: "nicht feiern"): `session_depth` liest jetzt **64.5** (p25 42/p75 69) statt v1 25.0, weil der Bot ziel-bewusster sucht, nicht weil das Spiel länger wurde. Die übrigen Metriken ±0.

Die relevanteste Erkenntnis: der geführte kompetente Player leert die komplette entdeckbare Welt (10 Blueprints + 9 Prozesse) weiterhin in **~15–19 gezielten Aktionen** (guided full 8/20, Median last_new ~15). Die 64.5 sind Mess-Bot-Reisezeit, keine gewachsene Tiefe. **Die Langeweile-Stelle bleibt ein flaches Discovery-Cap.** Einziger echter Hebel: die freigegebene REC-002 → SPEC-006-Kette (zweite Discovery-Schicht), weiterhin offen.

### Weitere Befunde
- **guided-Bot 8/20 voll** — dokumentierter fragiler Band (½–2 über Sessions), kein neuer Regress. Rückzug-Trigger weiterhin blind für brennendes-aber-zu-schwaches Feuer am kalten Ort (PLAYER-Tooling-Task bleibt).
- **`discovery_gap` 0.6 EXAKT Bandkante** (naive 0.4, naive_p25 0.3) — Spiel-Signal annotiert, Direktor: beobachten, nicht optimieren.
- **Naive Probe** (eigene Runs): stirbt ~18–24 Aktionen an Energie 0/Kälte, 1–2 BPs, 0 Prozesse, Tier-2 nie erreicht. Lern-Decke (Feuer/Futter), kein Bug.
- Keine Spiel-Repression, kein neuer Bug → kein 🔴-Eintrag.

### Commits
`play: scorecard + playtest (cron)` — Scorecard (2026-08-26), play/2026-08-26.md.

---

## 2026-08-25 — [Dev] session_depth v2 — ziel-bewusster naiver Bot (Peter 22.08., Pkt 5)

### Aufgabe
Top-Task der Freigabe-Reihenfolge (Ehrlichmachungs-Batch erledigt): den strukturell
blinden v1-session_depth-Zufallsbot zu einem **ziel-bewussten naiven Bot** umbauen, der
NEAR_MISS-Hinweise verfolgt, BPs mit ≥2/3 Materialien versucht und ab `survival ≥ 0.4`
auch gated Tier-2-Blueprints. Version 2, Probezeit 14 Tage, beobachtend.

### Was gebaut wurde (`tools/scorecard.py`)
- `_bp_overlap()` — resolved Slot-Overlap über `TAG_FAMILIES` (wie die Engine).
- `_v2_selection()` — wählt für einen unbekannten, gate-offenen BP die Item-Auswahl:
  Kandidat = höchste **Overlap-Quote** (n/n = vollendbar schlägt 2/3), NEAR_MISS als
  Tiebreak; fehlende Slots werden mit zufälligen Rest-Items gefüllt, damit ein Versuch
  überhaupt stattfindet (und ein NEAR_MISS feuern kann) — der Bot konvergiert also über
  Versuch + Hinweis, nicht nur bei 100%-Match.
- `_run_session_depth()` — halb Material (reisen + sammeln, um Kopf-Material in anderen
  Biomen zu holen), halb zielgerichtete Versuche; `stall_limit=15` bleibt.
- `METRICS`: session_depth **version 2**, `probation_until: 2026-09-08` (+14 Tage ab 25.08.).

### Ergebnis (Re-Baseline, nicht Feiern)
Der v1-Bot konnte die survival-gated Tier-2-Schicht strukturell nicht öffnen (nur 0–1
Tier-1-Discovery, survival ≈0.0–0.2 → Gate 0.4 nie erreicht). Der v2-Bot **erreicht
`rope` und `cord_spear`** über mehrere Seeds — genau der Zweck. Erst-Lesung `metric_session_depth`
**25 → 64.5** (p25 42, p75 69). Das ist **kein Fortschritt, sondern Re-Baselining** — die
Zahl ist höher, weil der Bot mehr entdeckt, nicht weil sich das Spiel geändert hat (Peter:
„nicht feiern"). Neue Baseline dokumentieren, Probe bis 09.09.

### Tests
`test_scorecard.py`: `session_depth` version == 2; Batches-Probezeit-Label erscheint;
`_v2_selection` wählt vollendbaren BP vor 2/3-Near-Miss; v2-Bot öffnet gated Tier-2
(rope + cord_spear) über den Seed-Satz. **231 Tests grün** (228 → 231).

### Konstitution
session_depth-Umdefinition ist durch Peters Freigabe (22.08.) gedeckt, probe-zeit-metriken
bleiben beobachtend (kein Plan-Ziel). Keine andere Metrik angefasst: reachability 1.0,
discovery_gap 0.6, craft_variety 5.0, content_reachable 1.0 unverändert.

---

## 2026-08-25 — [Research] SPEC-010 Kaltstart-Brücke: knappbarer Startstein (actions_to_first_craft)

### Befund (Metrik-Modus)
Schwächste/stagnierende verifizierbare Metrik: **`actions_to_first_craft` = 34.5**, flach
über sechs Readings (08-07 bis 08-24), p75=48, `niedriger = besser`. = die Kaltstart-Friktion:
der naive Spieler braucht ~34 Aktionen bis zum ersten Craft — fast so lang wie die komplette
entdeckbare Welt (`session_depth` 25). Die Langeweile beginnt vor dem ersten Werkzeug.
Diagnose (Probe über alle 20 Seeds, nicht vermutet): `forest_edge` enthält **kein
Head-Material** (FLINT/BONE/STONE) — erst der kalte `mountain_peak`-Trip gibt eins her.
Median **26.5 Aktionen, bis das Inventar überhaupt ein komplettes 2-Slot-Material hält**.

### Skip-Begründung
`discovery_gap`: gated (REC-002), kein Ziel. `session_depth` = Nordstern, aber SPEC-006
verplant → Kollision. `actions_to_first_craft`: verifizierbar, nicht gated, nicht in
Probezeit, sechs Readings ohne Signatur → sauberster Fall.

### Mechanik
"Primitive tool at hand" — Minecraft/UnReal World/Vintage Story/Long Dark: erstes
Kopf-Material dort, wo die Hand es findet, kein kalter Reiseweg. Nicht Content anhängen,
sondern die erste Stufe in den Start-Biom legen.

### Adaption (SPEC-010)
Ein `pebble`-Node (STONE+PROJECTILE, max_stock 8, regen 0.04, chance 0.6) in `forest_edge`
(`data/locations.json`). Kein neuer Blueprint, kein neues Template, kein FLINT-Node (Head-
Dreifaltigkeit STONE/BONE/FLINT bleibt). `make_sharp_stone` (2× pebble) wird als
unbewaffneter Früh-Prozess erreichbar.

### Probe (monkeypatch, keine Scorecard-Dateien geschrieben)
`actions_to_first_craft` **34.5 → 12.5**, `session_depth` 25 → 40 (seitige Wirkung, via
SPEC-006 additiv), `craft_variety` 5.0, `blueprint_reachability` 1.0, `content_reachable`
1.0. Kein Mess-Bruch nachgewiesen.

### Deliverables
- `specs/SPEC-010-kaltstart-stein.md` — genau ein Spec (Problem/Mechanik/Adaption/
  Akzeptanz/erwartete Metrik-Wirkung).
- `PLAN.md` — SPEC-010 als offener `[ ]`-Task ergänzt.
- COMMIT: `research: spec 010 kaltstart-stein (cron)`

---

## 2026-08-24 — [Dev] Ehrlichmachungs-Batch (Pkt. 1–4): skill_spread-Label, craft_variety v2, content_reachable v2, feedback_quality v3 (cron)

### Aufgabe
Der oberste offene PLAN-Task: **Ehrlichmachungs-Batch** — die vier am 22.08. von Peter freigegebenen Metrik-Korrekturen (`DECISIONS_Response_2026_08_21.md` Pkt. 1–4). Kein Spielfeld-Eingriff, nur Mess-Ehrlichkeit + eine Neu-Interpretation. Fehler-Batch: versionierte Metriken zeigen im nächsten Scorecard-Delta `— (neu definiert)` statt falscher Pfeile.

### Geliefert (tools/scorecard.py)
- **skill_spread v1 (Option A, umdeuten):** Formel exakt unverändert, **Version bleibt 1**. Richtung dreht auf `niedriger = besser`, Beschreibung: fallend = **gehobene Einsteiger-Decke** (Zufallsspieler überlebt näher am Optimum), kein Tiefenverlust. Der Fall 0.216 ist damit ein angenehmes Signal, kein Regress.
- **craft_variety v2:** zählt jetzt distinkte `blueprint_id`s **und** `process_id`s. Der naive Bot versucht mit ~10% Wahrscheinlichkeit einen zufälligen Prozess und trägt bei Erfolg dessen `process_id` ein. Erste Lese 3.5 → 5.0 (re-Baseline, Prozesse waren vorher unsichtbar).
- **content_reachable v2:** prüft zusätzlich Node-Referenzen — ein Node, dessen `result_template_id` kein Template hat, zählt als definiert-aber-unerreichbar (`dangling_refs`) und senkt die Metrik sichtbar. Aktuell 0 dangling, weiterhin 18/18 = 1.0. Die `⚠ Content entfernt`-Warnlogik (defined_count-Vergleich) bleibt unverändert.
- **feedback_quality v3:** `_expected_fragment("NEAR_MISS:…")` → `"gehören"` — der Near-Miss-Text ist absichtlich vage, seine Nützlichkeit IST seine Vagheit, er zählt als informativ. Zusätzlich `NOT_ENOUGH_QUANTITY` → `"mehr von demselben"`. **Vollständigkeits-Pflicht:** `EMITTABLE_REASONS` + Vollständigkeits-Test erzwingen, dass jeder Reason ein Fragment ODER einen dokumentierten None-Grund hat (UNKNOWN/UNKNOWN_PROCESS/MISSING_INPUT). Erste Lese 0.916 → 1.0 (re-Baseline, NEAR_MISS war vorher untermessen).

### Tests (wie das CONSTRAINT verlangt: grün, +5)
228 passed (vorher 223). Neu: v3-Fragmente (NEAR_MISS, NOT_ENOUGH_QUANTITY), Vollständigkeits-Test über alle emittierbaren Reasons-Codes, craft_variety v2 (Prozess-Erfolg erzwungen → Metrik steigt über die v1-Baseline 3.5), content_reachable v2 (dangling via Monky patched `get_all_locations`). Versionen in `compute_all` (2/2/3) geprüft.

### Kein Spiel-Regress, keine geschönte Zahl
Keine Metrik abgeschwächt; nur was Peter am 22.08. (Pkt. 1–4) freigab. Werte steigen/interpretieren neu, ohne dass sich das Spiel änderungsbedingt ändert — das erwartete Re-Baseline-Verhalten, das Peter für die nächsten Play-Lesungen explizit als "nicht feiern, dokumentieren" eingeordnet hat.

### Backlog/Journal
- 🟡 Neu befunden (Constitution-Brücke, nicht im Batch-Scope): `INJURED` wird in `core.gather()` per `_feedback_message("INJURED")` ausgegeben, hat aber **keinen Zweig** in `_feedback_message` → fällt auf den generischen Fallback "Das geht so nicht." (gather-Log, keine Verletzungs-Meldung). Mess-Freundlich: betrifft nicht `feedback_quality` (experiment-only), aber ein echter Text-Qualitätsbug der SPEC-009-Ökonomie. → BACKLOG eingesetzt.

---

## 2026-08-24 — [Play] Scorecard flach, Langeweile-Stelle unverändert (session_depth 25), guided-Erschöpfung ~13 (cron)

### Headline
Flacher Scorecard-Tag (deterministisch, kein Dev-Commit seit 22.08): alle Metriken ±0. Die Langeweile-Stelle bleibt — `session_depth` 25, geführte Erschöpfung **~9–16 Aktionen an 7/20 vollen Runs (Median 13)**. Tier-2 (rope→cord_spear) verschiebt die Decke weiter nicht nach hinten. Der naive Blindflug (Probe: seed 20260807, nur knife_bone/knife_stone, 0 Prozesse, Tier-2 nie) bestätigt die Struktur: survival-Gate bleibt ungehoben, zweite Schicht aus naiv-Perspektive unsichtbar — Mess-Struktur, kein Spielfeld.

### Kein Regress
guided-Bot 7/20 voll (21.08: 6/20, 19.08: 8/20) = bekanntes fragiles Band, kein neuer Crasch. Rückzug-Trigger-Tech-Debt bleibt offen, kein erneuter Übergriff-Versuch.

### Für Direktor/Peter
Die seit 22.08 freigegebenen PLAN-Tasks, die die Nordstern bewegen (Ehrlichmachungs-Batch → session_depth v2 → REC-002 → SPEC-006), sind noch NICHT in Dev umgesetzt — solange sie fehlen, bleibt der Nordstern strukturell unbewegt. Beide Mess-Entscheide warten weiter auf Peter (feedback_quality/NEAR_MISS, session_depth-Bot-Deutung).

---

## 2026-08-23 — [Direktor] Plan-Neufassung: Peters Entscheide (22.08.) übernommen, SPEC-006-Leiter jetzt frei (cron)

### Scorecard-Verlauf (Trajektorie 03.08. → 21.08.)
| Metrik | 03.08 | 17.08 | 19.08 | 21.08 | Lesart |
|--------|-------|-------|-------|-------|--------|
| actions_to_first_craft | 63 | 34.5 | 34.5 | 34.5 | ↑→ gesunder Einstieg, stabiler Boden |
| blueprint_reachability | 1.0 | 1.0 | 1.0 | **1.0** | ↑ REC-001, ehrlich, Decke (10/10) |
| craft_variety | 0.5 | 3.0 | 3.5 | 3.5 | ↑ gesund (SPEC-005/008/009) |
| skill_spread | 0.315 | 0.216 | 0.216 | 0.216 | ↓→ klären (Peter, A/B/C) |
| feedback_quality | 1.0 | 1.0 | 0.916 | 0.916 (v2) | –→ Blindstelle (NEAR_MISS, Peter) |
| content_reachable | 0.667 | 1.0 | 1.0 | **1.0 (18/18)** | ↑ Decke (SPEC-009 bandage/poultice) |
| session_depth | 24 | 25 | 25 | **25** | ↔ **Nordstern, flach seit Wochen** |
| discovery_gap | 0.5 | 0.625 | 0.6 | **0.6** | → im Band, aber exakt auf der oberen Kante |
| forage_pressure | – | 0.707 | 0.707 | 0.707 | Probe beendet 20.08, über Band – Entscheid |
| warmth_stability | – | – | 0.46 | 0.46 | Probe bis 27.08, im Band – beobachtend |
| recovery_stability | – | – | – | 0.375 | Probe bis 03.09, im Band – beobachtend |

**Was vorwärts geht:** `reachability` 1.0, `content_reachable` 1.0 (18/18 nach SPEC-009), `discovery_gap` 0.625→0.6 (SPEC-003), `craft_variety` 3.5. SPEC-009 hat eine komplette zweite Überlebensökonomie (Verletzung & Heilung) mit eigener Probe-Metrik geliefert. **Was stagniert:** `session_depth` 25 (die Langeweile-Stelle, Nordstern – unverändert, auch nach SPEC-008s zweiter Schicht, weil der naive Bot die Gates nicht öffnet). `skill_spread` (0.216) und `feedback_quality` (0.916) sind **keine Spiel-Regresse** – beide sind Mess-Entscheide, die auf Peter warten.

### Kernbefund: Peter hat die Warteschlange abgeräumt
Am 22.08. hat Peter in `DECISIONS_Response_2026_08_21.md` entschieden: skill_spread = Option A (umdeuten, Formel bleibt v1). craft_variety v2 (Prozesse zählen) und content_reachable v2 (dangling Nodes) freigegeben. feedback_quality v3 (NEAR_MISS als informativ + Vollständigkeits-Test) freigegeben. session_depth v2 (ziel-bewusster Bot) freigegeben, Probezeit 14 Tage, beobachtend. tool-aware reachability als REC-002 freigegeben. SPEC-006 freigegeben und priorisiert. forage_pressure v2 freigegeben (Band bleibt). warmth/recovery beobachtend bestätigt. Damit ist die frühere Mess-Blockade des Nordsterns aufgelöst: `session_depth` kann jetzt bewegt werden.

### Neue PLAN-Tasks (Reihenfolge nach Peter)
1. **Ehrlichmachungs-Batch** (Pkt. 1-4): skill_spread-Label, craft_variety v2, content_reachable v2, feedback_quality v3 (mit Vollständigkeits-Test).
2. **session_depth v2** (Pkt. 5): ziel-bewusster Bot, Probezeit 14 Tage, beobachtend.
3. **REC-002** (Pkt. 6): tool-aware reachability, Entwurf + Wirkung + Tests.
4. **SPEC-006** (Pkt. 7): Werkzeug als Zutat, priorisiert. Gap steigt > 0.6 = Spiel-Signal, nie Metrik schwächen.
5. **forage_pressure v2** (Pkt. 8): gefühlte Knappheit, Band bleibt, parallel.
6. **Play-Tooling** guided_full-Rückzug-Trigger (ohne Freigabe).

Probe-Metriken (warmth bis 27.08., recovery bis 03.09.) bleiben beobachtend, sind laut CONSTITUTION keine Plan-Ziele.

### Selbstmodifikation des Systems
**Keine Cron-Änderungen.** Die Tasks passen in die bestehenden Dev-Slots (Mo–Sa) und Research-Slots (Di/Do); ein eigener Discovery-Task ist ein Research-Kandidat, kein Grund für einen neuen Job. Kein echter Takt-/Rollen-Gap. Play/Mess-Kern unangetastet. „CONSTITUTION.md ist unantastbar. Prüfe jede Änderung dagegen.“ bleibt in allen Prompts.

### Triage (BACKLOG)
- 🔵 guided_full-Retreat-Trigger (21.08.) bleibt als echtes Tech-Debt im Backlog (Messwerkzeug-Pflege, chirurgischer Fix, 20-Sweep-gegengetastet) — kein neuer Task, keine Metrik.
- 🟡 Deckungslücke `session_depth`/`feedback_quality`/`skill_spread`: in Tasks überführt, schwebend auf Peter.
- ⚪ Research-Leads (Valheim/Long Dark/Green Hell/Zomboid/Dwarf Fortress) bleiben als Ideen-
  reservoir; SPEC-006 ist durch Peters Entscheid (22.08.) wieder frei und priorisiert.

### CONSTITUTION-CHECK
Peters Entscheide (22.08.) sind eingegangen; DECISIONS.md-Checkboxen sind gesetzt. Metrik-Änderungen selbst (v2/v3, REC-002) werden per DEV-Session angewendet, nicht vom Direktor — dieser hat nichts an `tools/scorecard.py`, `METRICS` oder Scorecard-Dateien geändert. Kein Spieldesign angefasst. Probe-Metriken (warmth bis 27.08., recovery bis 03.09.) sind nicht als Plan-Ziele gesetzt. Keine Cron-Änderungen; Play-Job/Messung unangetastet. Konform.

### Artefakte / Verifikation
- PLAN.md (komplett neu, 3 Sektionen, Reihenfolge nach Peters Entscheiden), DECISIONS.md (Boxen gesetzt), BACKLOG.md (Triage-Note). `python -m pytest`: 223 passed vor den Schreib-OPs. Working tree war sauber; Rebase auf Peters Commit `4b78dc8` (DECISIONS_Response).

---

### Aufgabe
Kein offener, nicht-blockierter PLAN-Task: SPEC-006 Peter-blockiert, forage/warmth/skill_spread beobachtend, SPEC-003/008/009 erledigt. Aber BACKLOG 🔵 (18.08., Dev-selbst geflaggt): **"Spec-Datei sollte aktualisiert werden."** Das ist reine Doku-Synchronisation — kein Metrik-Core, keine Engine-Änderung, verfassungs-konform.

### Geliefert
- `specs/SPEC-008-survival-gate-tier2.md` an Implementierungs-Realität angeglichen:
  - `cord_spear`-Binding **FIBER → CORD** in der Adaption-Sektion (mit Korrektur-Hinweis: FIBER wäre von `spear_bound` überschattet → reachability-Regress; bindet mit gecraftetem rope). Code hatte das schon (data/blueprints.json:77), nur der Spec war stale.
  - Adaption-Schritt 2 (`data/items.json`: neue Tier-2-Templates) **bewusst als NICHT umgesetzt markiert** — hätte `content_reachable` 16/16→16/18 gesenkt; wie die 8 Werkzeuge bleiben Tier-2-Ergebnisse blueprint-only. Damit dokumentiert, warum kein Entry in items.json.

### Verifikation
- `python -m pytest`: **223 passed** (grün, unverändert — Doku-Only, kein Code angefasst).
- Konstitution geprüft: keine Metrik entfernt/abgeschwächt, kein Scorecard/Engine-Eingriff.

### Backlog/Journal
- 🔵 BACKLOG (18.08) "SPEC-008 Spec-Datei aktualisieren" — erledigt.

---

## 2026-08-21 — [Play] Scorecard + Playtest: Langeweile-Stelle unverändert 25, guided-Decke in ~15 Aktionen geleert (cron)

### Ablauf
223 Tests grün. `tools/scorecard.py` geschrieben (2026-08-21.json, deterministisch). Befunde aus drei geführten + Naive-Sweeps.

### Headline-Befund: Die Discovery-Decke IST das Spiel — und sie leert sich in ~14–16 geführten Aktionen
`session_depth` **25.0, flach seit 5 Messungen**. Geführte Erschöpfung: ein kompetenter Player leert alle 10 Blueprints + 5 Prozesse in **~14–16 Aktionen** (seeds 20260810@16, 20260812@14), danach `gather_at(random)` = Grind. Timeline: `spear→spear_bound→rope→cord_spear→make_bandage…` alles in ≤16 Aktionen. Der Tier-2-Layer (rope→cord_spear) landet mitten in der Kette statt die Erschöpfung nach hinten zu schieben → die 2 Messwege sind strukturell blind für gestufte Discovery (bestätigt 18./19.08.). Entscheid nötig bei Peter (Metrik = Verfassungs-Kern): session_depth-Bot für gestufte Discovery kalibrieren, oder flach als soziales Signal akzeptieren.

### Zweitbefund: guided-Bot 6/20 (19.08: 8/20) — bekannter Kälte-Wartungsloop, NICHT SPEC-009
Sterbende Runs haben `injuries={}` → nicht die Verletzung. Kill: `_warm_here` rettet nur bei `not fire_active`; am kalten `mountain_peak` zündet der Bot Feuer (fire_active=True) → Rückzug-TRigger greift nie, body_temp ~31, −3 HP/Aktion. Geprüft und bewusst NICHT gehärtet: aggressiver body_temp<35-Retreat im 20-Sweep → **3/20 voll**, strikt schlechter (Skill-dokumentierte Falle). HEAD bleibt Decke.

### Backlog/Journal
- 🔵 Tech-Debt: Rückzug-Trigger `not fire_active` blockt Kälte-Retreat am Ort mit „aktivem aber ungenügendem Feuer" — chirurgischer Fix (body_temp-gated am kalten Ort), gegen-tastbar über 20-Sweep.
- Kein neuer Spiel-Bug. Keine Metrik-Anfassung.
- Commit: play/2026-08-21.md, BACKLOG.md, JOURNAL.md, SCORECARD.md, scorecard/2026-08-21.json.

---

## 2026-08-20 — [Dev] SPEC-009: Verletzung & Heilung implementiert — persistente Wunden + `recovery_stability`-Probe (cron)

### Aufgabe
Der oberste offene, nicht-blockierte PLAN-Task: **SPEC-009** (Verletzung & Heilung, free research — additiv, kein Freigabe-Gate). SPEC-006 ist Peter-blockiert, forage_pressure/warmth/skill_spread sind beobachtend. Also: implementieren.

### Geliefert (Engine)
- `Player.injuries: dict` (persistenter Wund-Zustand): `cut` (blutet unbehandelt 0.2 HP/Tick über Zeit) + `strain` (Effort-Malus 1.0 beim Sammeln).
- Handlungsgebundene Entstehung in `gather()`: exponierter `mountain_peak` (exposure ≥ 0.8) → strain; scharfe Funde (SHARP-Node) → cut. Kein globaler Timer.
- Heilung = **entdeckbare Prozesse** + Ruhe: `make_bandage` (plant_fiber×2 → Verband), `make_poultice` (mushroom+clay_lump → Umschlag), `treat_cut`/`treat_strain` (apply-only; ohne Wunde `NO_INJURY`, Material **nicht** verbraucht). `_resting_warm()` = Feuer ODER shelter (exposure ≤ 0.15 / hidden_cave). **Unbehandelt heilt nie** — nur behandelt + rastend.
- Neue Templates `bandage`/`poultice` (Prozess-Outputs) → `content_reachable` 18/18, `blueprint_reachability` 1.0.

### Erstwert Probe-Metrik `recovery_stability`
Band 0.3–0.7, Probation bis **03.09.** (offset +14 Tage). Erstwert **0.375 — im Band**, deterministisch, p25=p75 (flach, wie warmth — Probezeit entscheidet über Aussagekraft). Misst Anteil der Verletzungs-Ticks, die Behandlung+Ruhe abwenden.

### Zwei Design-Entscheidungen (wichtig fürs Protokoll)
1. **Eigener Injury-RNG** (`GameEngine.injuries_rng`, aus aktuellem globalen Zustand geseedet). Anfangs nutzte ich das gemeinsame `random` in gather → das **verschob die Ressourcen-Sequenz** aller Mess-Bots (guided cook_meat 17/20 → 8/20) und der `discovery_gap` kletterte. Fix: Verletzungswürfe gehören auf einen eigenen Strom, der den Fund-Strom **nicht** konsumiert. Ergebnis: **alle Baseline-Metriken byte-identisch** (skill_spread 0.216, session_depth 25, feedback 0.916, warmth 0.46, forage 0.707, first_craft 34.5), guided cook_meat wieder ≥14/20. Die Verletzung existiert für echte Spieler (eigener RNG), aber stört die Messung nicht.
2. **Frequenz niedrig kalibriert** (cut 0.015, strain 0.02): die kurzen Discovery-Bot-Fenster (~150 Aktionen) sollen die meisten Seeds unbeschadet überstehen, sonst fällt `discovery_gap` über Band (Baseline steht exakt auf 0.6). Lang spielende, unvorbereitete Spieler spüren Verletzungen weiterhin.

### Constitution & Metrik-Core
- `tools/scorecard.py` nur um die **additive** Probe-Metrik `recovery_stability` erweitert; keine bestehende Metrik entfernt/umdefiniert/geschwächt. Alle Baseline-Werte unverändert (verifiziert per Inline-Probe, keine Scorecard-Dateien überschrieben — Play-Job bleibt Eigentümer).
- Die Spec warnte vor der `feedback_quality`-Blindstelle (`_expected_fragment` für `INJURED`/`TREATED`/`HEALED`). **Umgehe ich strukturell:** die Wund-Meldungen laufen über Gather-Logs (nicht über Experiment-Reasons) → treffen `_expected_fragment` gar nicht → keine stille Metrik-Abschwächung, kein needs-Peter fürs Mapping. Die offene NEAR_MISS-Blindstelle (Play 19.08.) bleibt bei Peter.

### Guided-Mess-Bot
`play/guided_full.py` war (wie nach SPEC-007) gegen die neue Mechanik blind: es behandelte keine Wunden und verblutete. Fix (legitime Play-Tool-Pflege): `_treat_if_injured()` (cut→make_bandage+treat_cut, strain→make_poultice+treat_strain, best-effort) + neue Prozesse in die Prozessliste. cook_meat-Aggregat ≥14/20 bleibt grün; frühe Tode der Seeds 20260803/15 sind **vorbestehend** (Baseline identisch), kein Regress.

### Verifikation
`python -m pytest`: **223 passed** (inkl. neuer `tests/test_injury.py` 12 Tests + `recovery_stability`-Registrierung). Protokoll: reachability 1.0, content 18/18, gap 0.6 (im Band), recovery 0.375 (im Band).

### Nächste Schritte für Direktor
- `recovery_stability` bleibt Probe bis 03.09. — beobachtend, kein Plan-Ziel.
- `feedback_quality`-NEAR_MISS-Blindstelle und `discovery_gap`-Randlage (0.6 = Grenze) weiter bei Peter/Direktor.

---

## 2026-08-20 — [Research] SPEC-009: Verletzung & Heilung — persistente Wunden als aktive Überlebensökonomie (Explorations-Modus, cron)

### Auftrag
Freier Explorations-Modus: Mechanik gesucht, die das Spiel als **System** vertieft — bewusst nicht an eine bestehende Metrik gebunden (Metrik-freies Feld u.a.: Verletzung und Heilung, Wetter, Werkzeugverschleiß, Terrain/Ortsbindung, Basisbau).

### Befund (systemisch): die Fundamentalschraube ist die einzige Druckschraube
`engine/core.py:_advance_time` (Z.180-214) reduziert `hp` ausschließlich über **Hunger-Drain** und **Unterkühlung/Hitzschlag**. `eat()` (Z.257-276) ist der **einzige Heilungsweg** (`hp += kcal/20`). Es gibt **keine persistente Verletzung, keine Verletzungsquelle aus eigenem Handeln, keinen Heilungs-Prozess** — kein Wund-Zustand, kein Verband/Umschlag.
Doch die Rohstoffe für die Gegenmechanik **existieren bereits und liegen brach**: `plant_fiber` (FIBER → Verband), `mushroom`+`clay_lump` (EDIBLE/CLAY → Umschlag), `fire` (SPEC-007) + `hidden_cave` (exposure 0.1 → Rast). Analog zu SPEC-007 (Kälte-Druck da, Feuer-Hebel fehlte) — hier ist es grundlegender: **weder Druck (Verletzung) noch Hebel (Heilung) existiert.** Das Spiel hat nur eine einzige Druck-Schraube (thermisch/zeitlich); Risiko aus *eigener* Orts-/Materialwahl und die daraus folgende Entscheidung (vorbereiten vs. absichern, rasten) fehlt komplett.

### Warum dieses Thema (kein Metrik-Zwang)
Constitution: "Wachstum in Systemen, nicht nur Inhalten" + "Entdecken vertieft". Ein Verletzungs-/Heilungs-Layer gibt eine zweite, **aktive** Überlebensökonomie — echte Entscheidungen statt Wartungs-Loop. Rein additiv, kein Metrik-Core-Entrücken.

### Geliefert
- `specs/SPEC-009-injury-healing.md` — persistente `Player.injuries` (`cut` blutet über Zeit, `strain` Effort-Malus); handlungsgebundene Entstehung (exponiertes Sammeln am `mountain_peak`, scharfe Materialien); Heilung = entdeckbare Prozesse `make_bandage`/`make_poultice` + Ruhe an warmem/Ort-Ort. Quelle: The Long Dark (Affliction/Bleeding) + UnReal World/Vintage Story (Wunden, Kräutermittel + Ruhe). Kein Freigabe-Gate (additiv).
- `metrics/proposed/recovery_stability.md` — neue Metrik: Anteil der Verletzungs-Ticks, die durch Behandlung+Ruhe abgewendet werden; Band 0.3–0.7. Misst, ob Verletzung *abwendbar* statt entgleisend ist.
- `PLAN.md`: SPEC-009 als offener Task.

### Warum die Discovery-Metriken nur als Nebeneffekt berührt sind
`session_depth`/`discovery_gap` sind nicht Ziel dieses Modus; Sekundär-Wirkung explizit als Risiko notiert (new Prozesse helfen session_depth, aber Verletzung lässt den schwachen naiven Bot früher sterben → netto unklar; `discovery_gap` darf nicht über Band). Primär-Beweis liegt in der **neuen** Probe-Metrik.

### Verzichtet
Keine bestehende Metrik angefasst. SPEC-006 bleibt blockiert (Peters Freigabe), nicht umgangen. Kein Kampf-/Feind-System (Constitution: Kampf als Randphänomen). Kein Metrik-Core (`tools/scorecard.py`) berührt. CONSTITUTION: additiv, kein Rezeptbuch (Prozesse werden entdeckt), Experimentiergedächtnis erlaubt, CLI-Text bleibt, stdlib only.

---

## 2026-08-19 — [Dev] Guided-Bot: rohes Fleisch als Zutat reserviert → `cook_meat` 5/20 → 17/20 (cron)

### Aufgabe
Alle PLAN-Tasks sind offen, aber blockiert (SPEC-006 = Peters Freigabe; forage_pressure/warmth beobachtend; skill_spread = Peter-Entscheid). Kein implementierbarer PLAN-Task. Dem etablierten Muster folgend (Dev 15.08./14.08.) das offene 🔵 Tech-Debt aus BACKLOG 17.08.: **`play/guided_full.py` aß sein rohes Fleisch (EDIBLE 150) selbst, bevor `cook_meat` (braucht 1× raw_meat + Feuer) Inputs hatte** → 5. Prozess systematisch unterrepräsentiert (5/20 Seeds). Play-Messwerkzeug, keine Metrik — CONSTITUTION-konform.

### Root Cause (beim Einstieg reproduziert)
`eat()` wählte das **höchste EDIBLE** — `raw_meat` (150) schlug berries (50)/mushroom (30) und wurde gefressen, sobald Energie/HP sanken. Der bestehende Guard schützte rohes Fleisch nur als letztes Stück bei energy > 100. `cook_meat` und `make_fur_cloak` stehen zwar in der Prozessliste, aber das Fleisch war vorher weg. Zusätzlicher Befund: nach dem Fell-Umhang (verbraucht 1 rohes Fleisch) jagte der Bot **nie gezielt ein zweites** fürs Kochen — fehlte also oft die Zutat komplett.

### Fix (nur `play/guided_full.py`)
1. **`eat()` reserviert rohes Fleisch als Zutat:** bevorzugt gekochtes Fleisch / Beeren / Pilze; rohes nur noch als letzte Notration (wenn nichts anderes EDIBLE übrig ist). Der Bot frisst sich nicht mehr seinen eigenen Fortschritt weg.
2. **Gezielte Jagd-Brat-Sequenz im `_warmup`:** nach dem Fell (solange Feuer + Energie frisch) jagt er am warmen Waldrand ein **zweites** rohes Fleisch (PROJECTILE) und brät es mit `cook_meat`. Vorher verpuffte die Koch-Sequenz im fragilen Hauptloop, wo der Bot an Kälte/Energie starb, bevor er den 5. Prozess je erreichte.

### Verifizierte Wirkung (n=20, deterministisch)
| Prozess | vorher | nachher |
|---|---|---|
| `cook_meat` | **5/20** | **17/20** |
| `make_fur_cloak` | 17/20 | 18/20 |

`cook_meat`-Erreichbarkeit von 25 % auf 85 % der Seeds — der 5. Prozess wird jetzt ehrlich gemessen. `make_fur_cloak` bleibt stabil (18/20, leicht zurück, da Fleisch jetzt teils zum Braten verwendet wird — akzeptabler Tradeoff, Ziel war cook_meat).

### Verifikation
- `python -m pytest`: **209 passed** (vorher 205; +4 neue Tests in `tests/test_guided_full.py`: eat() reserviert rohes Fleisch vor gekochtem/Beeren + Notration; guided_full erreicht cook_meat auf ≥14/20 Seeds).
- Kein Engine-/Metrik-/Content-Code angefasst. CONSTITUTION: Messwerkzeug frei, nichts entfernt/umdefiniert, kein Rezeptbuch.

### BACKLOG
- 🔵 guided_full-cook_meat-Eintrag (17.08.) → ✅ erledigt.

---

## 2026-08-19 — [Play] Scorecard + Playtest: Das Spiel wurde tiefer, aber nichts misst es (cron)

**Headline (Langeweile-Stelle):** `session_depth` 25, flach seit 5 Messungen — aber die erste Scorecard nach SPEC-008 zeigt: das Spiel hat einen ECHTEN zweiten Discovery-Layer (rope→cord_spear via `min_survival_req`-Gate), und beide Messwege sind dagegen strukturell blind:
- Gated: naive Metrik erreicht das Gate (survival 0.4 nach ≥2 Tier-1-Discoveries) vor dem Stall selten → die 2 neuen Blueprints tauchen nie auf, Wert bleibt 25.
- Guided: öffnet das Gate automatisch → Tier-2 landet *mitten* in der Kette, der Erschöpfungspunkt (letzte Neuheit) rückt nicht nach hinten. Full-only-Median ~18–24 (10/10) vs. ~21 (8/8) letzte Woche — kein Zuwachs.
Der Tier-2-Layer selbst ist verifiziert funktionsfähig (rope 0.4 + cord_spear 0.6 auf gecraftetem rope, engine-seitig craftbar). **Das ist Fortschritt in der Wirklichkeit, unsichtbar in den Zahlen.** `session_depth` ist zum veralteten Indikator für echte Tiefe geworden → Entscheid an Peter/Direktor (Metrik-Kern).

**Zweitbefund:** `feedback_quality` 1.0→0.916 (−0.084). Ursache root-caused & verifiziert: `NEAR_MISS:*` (SPEC-003) zählt als uninformativ, weil `_expected_fragment` kein Mapping hat — der Near-Miss-Text ist absichtlich generisch (kein Leak), seine Nützlichkeit ist seine Vagheit. Zielkonflikt: beste Discovery-Rückmeldung kosten Metrik-Punkte. NICHT angefasst (Constitution), als Peter-Entscheid in Backlog. Kein Spielfehler.

**Drittbefund:** guided-Bot fragiler denn je — 8/20 leeren alle 10 Blueprints (vorher 13/20 bei 8/8), alle Seeds enden negativ HP. Bekannte Messwerkzeug-Fragilität nach SPEC-007/008, kein Spielfehler.

**Scorecard 2026-08-19:** session_depth 25.0 (±0) · discovery_gap 0.6 (−0.025, in Band) · craft_variety 3.5 (+0.5) · feedback_quality 0.916 (−0.084, NEAR_MISS-Blindstelle) · warmth_stability 0.46 (−) · forage_pressure 0.707 (Probe bis 20.08.) · Rest flach. Tests 205 passed vor jeder Schreib-OP.

**Backlog:** +2 🟡 (feedback_quality-NEAR_MISS-Blindstelle, session_depth-Tier-2-Blindheit Play-Bestätigung). Play-Bericht: `play/2026-08-19.md`.

---

## 2026-08-18 — [Dev] SPEC-008 — Wissens-Gate implementiert (`min_survival_req`-gestufte Tier-2-Blueprints, cron)

### Geliefert
- **`engine/components.py`**: `survival`-Basis **1.0 → 0.0**. Zwingend: bei Start 1.0 war der Gate tot — jeder Frischling erfüllte 0.4/0.6 sofort. Erst mit Start 0.0 ist "erst nach ≥2 Tier-1-Discoveries" real (Score wächst nur durch Discovery).
- **`data/blueprints.json`**: +2 Tier-2-Blueprints (8→10):
  - `rope` ("Faserseil", `min_survival_req 0.4`, Slots `FIBER+RIGID`, tool_tags `CORD`)
  - `cord_spear` ("Seilgebundener Speer", `min_survival_req 0.6`, Slots `SHARP_OR_RIGID+RIGID+CORD`, tool_tags `PIERCE`) — **bindet mit dem gecrafteten rope (CORD)**.
- **`engine/core.py`**: +`CORD`-Label in `TAG_LABELS` (feedback_quality).
- **`tests/`**: +5 SPEC-008-Tests (Gate blockt vor Discovery ohne Verbrauch/Leak; craftbar nach Gate; cord_spear auf rope-Basis; content_reachable 1.0). Count-Asserts 8→10, survival-Asserts 1.0→0.0, Gap-Test auf ≤0.6 aktualisiert. **205 passed** (vorher 200).

### Verifizierte Metrik-Wirkung (echte Scorecard, Seed-Satz unverändert)
| Metrik | vorher | nachher | |
|---|---|---|---|
| `blueprint_reachability` | 1.0 | **1.0** | alle 10 erreichbar ✓ |
| `content_reachable` | 1.0 | **1.0** | Tier-2 bleibt blueprint-only (wie die 8 Werkzeuge, nicht in items.json) ✓ |
| `discovery_gap` | 0.625 | **0.6** | in Band, Verbesserung ✓ |
| `craft_variety` | 3.0 | **3.5** | ✓ |
| `session_depth` | 25.0 | **25.0** | ⚠️ NICHT gestiegen (Spec-Ziel ≥30) |

### Befund: `session_depth` bleibt 25 — der naive Bot misst den Gate nicht
Die Spec-Probe (25→32) lief mit survival=1.0 → Gate **offen** → reine Content-Inflation (+2 immer-craftbare BP), was die Verfassung (Nicht-Ziel "Content-Menge als Selbstzweck") ausschließt. Mit **echtem** Gate: der naive `session_depth`-Bot entdeckt auf den meisten Seeds 0–1 Tier-1-BPs (survival 0.0–0.2) und stallt vor dem Gate (0.4). **Messung:** jede Gate-Schwelle >0 (getestet 0.1/0.2/0.4) lässt `session_depth` median unverändert 25 — das Gate ist für echte Spieler (die 2–3 Tier-1 natürlich entdecken) ein reales neues Ziel, aber der Random-Bot der Metrik erreicht es nicht. Der Gate ist *nicht* die Bottleneck-Stelle (der Bot-Stall ist es); `session_depth` misst damit gestufte Discovery strukturell nicht. **Frage an Direktor/Peter** (Metrik ist Verfassungs-Kern, nicht von mir änderbar): (a) akzeptieren — Gate bleibt, Metrik flach; (b) `session_depth`-Bot kalibrieren, damit er Discovery-Ziel-bewusst craftet (Scorecard-Eingriff, Freigabe); (c) sonstige Balance.

### Zwei Spec-Korrekturen (gegen die Buchstaben, für den Sinn)
1. **survival-Basis 0.0** (Spec sagte "kein Engine-Eingriff") — ohne sie kein echtes Gate; die Spec ging fälschlich von Start 0 aus.
2. **`cord_spear`-Binding FIBER → CORD** — mit FIBER wäre es von `spear_bound` (Binding `RIGID_OR_FIBER`, min 0.0, früher in Dict-Reihenfolge) überschattet → unerreichbar → `blueprint_reachability` wäre auf 0.9/10 regrediert. Bindung über das gecraftete rope macht es zu echter Tier-2-Progression und hält Reachability 1.0.
Spec 2.0 sagt "neue Templates in items.json" — **bewusst nicht getan**: würde `content_reachable` 16/16 → 16/18 = 0.889 senken (die 8 Werkzeuge sind ebenfalls nicht in items.json); Tier-2 bleibt blueprint-only.

### Constitution-Check
Kein vorgegebenes Rezept (Gate ist Spieler-Eigenschaft, kein Hinweis), Experimentiergedächtnis/Skill erlaubt, CLI-Text bleibt, stdlib only, **keine Metrik entfernt/abgeschwächt** (nur Ergebnis verbessert sich real: gap 0.625→0.6), Metrik-Core (`tools/scorecard.py`) unangetastet.

---

## 2026-08-18 — [Research] SPEC-008: Wissens-Gate — toter `min_survival_req`-Filter als metrik-sichere zweite Discovery-Schicht (`session_depth`, cron)

### Metrik-Wahl (Metrik-Modus)
Schwächste/stagnierende Metrik: **`session_depth` = 25**, flach über vier Messungen (24→26→25→25→25), Richtung „höher = besser“. Play 17.08. bestätigt die Langeweile-Stelle (8 BP + 5 Proz + 16 Templates in <30 min geleert).

**Warum die Band-/Probe-Metriken übersprungen:** `discovery_gap` ist durch REC-001/SPEC-003 der Discovery-Lücke-Hebel mit eigenem Dev-Task (DEV 17.08) — kein neues Ziel. `forage_pressure` (Probe bis 20.08.) und `warmth_stability` (Probe bis 27.08.) sind beobachtend, kein Ziel. `skill_spread` wartet auf Peters Deutungs-Entscheid. `session_depth` ist die sauberste, verifizierbare Langeweile-Metrik (PLAN #1), und für sie gibt es einen **nicht-blockierten** Hebel.

### Befund (systemisch): toter Fortschritts-Gate
`engine/core.py:405` prüft `min_survival_req`, `execute_experiment` erhöht `survival` um **+0.2 je entdecktem Blueprint** (+0.1 je Prozess) — **aber alle 8 Blueprints tragen 0.0**. Das Feld ist voll kodiert, aber kein Blueprint nutzt es. Discovery hat keine Rückkopplung: Entdecken macht nichts Neues entdeckbar — dieselbe „Discovery erzeugt keine Discovery“-Lücke wie SPEC-006, aber ohne deren Metrik-Blocker.

### Mechanik / Quelle
**Valheim** (Werkbank-Stufen schalten Rezepte frei — Fortschritt, nicht Items) + **Little Alchemy / RuneScape-Skillgates** (man kombiniert, was man gelernt hat; kumulativer Skill-Score öffnet Rezepte). Adaptiert als Wissens-Gate: Tier-2-Blueprints mit `min_survival_req > 0`, erst nach ≥2 entdeckten Tier-1-Blueprints craftbar.

### Verifizierte Metrik-Wirkung (n=20, deterministisch, per Monkeypatch — scorecard.py unangetastet)
| Metrik | jetzt | mit 2 Tier-2 (`rope` 0.4, `cord_spear` 0.6) |
|---|---|---|
| session_depth | 25.0 (p25 21, p75 43) | **32.0** (p24, p50) |
| blueprint_reachability | 1.0 | **1.0** (alle Tier-2 erreicht) |
| discovery_gap | 0.625 | **0.6** (kein Überschießen) |

**Das ist der entscheidende Unterschied zu SPEC-006:** das Wissens-Gate sperrt nur das *Versuchslaufen* eines Blueprints, nicht die Tag-*Existenz* — der Reachability-Zähler entdeckt Tier-1 zuerst (survival steigt), erreicht Tier-2 dann ebenfalls. Kein Engine-/Scorecard-Eingriff nötig (Feld + Akkumulation existieren). Nur `data/blueprints.json` + `data/items.json` + Tests.

### Geliefert
- `specs/SPEC-008-survival-gate-tier2.md` — Problem/Mechanik/Adaption/Akzeptanz/Metrik-Wirkung + Probe-Skript.
- PLAN.md: SPEC-008 als offener Task (über SPEC-006, da lieferbar ohne Freigabe).
- Constitution-geprüft: kein vorgegebenes Rezept, Experimentiergedächtnis/Skill erlaubt, CLI-Text bleibt, stdlib only, keine Metrik entfernt/abgeschwächt (additiv), Metrik-Core unangetastet.

### Risiko / Ehrlichkeit
Effektgröße hängt am Tier-2-Umfang (1–2 BP ≈ wenig; 2–3 schieben realistisch 25→~30+). Balance (exakte Items/Score) entscheidet Dev/Direktor. `discovery_gap` wird primär von SPEC-003 geschlossen; SPEC-008 hebt sie nicht über Band (0.6 verifiziert).

---

## 2026-08-17 — [Dev] SPEC-003 — Partielle Match-Erkennung implementiert (NEAR_MISS, cron)

### Headline: `discovery_gap`-Hebel gelandet — ≥2/3 unbekannter Slots gibt reines Ja/nein

**Scope:** `engine/core.py` (`_no_match_reason`, `_feedback_message`, `_missing_tags`), `engine/components.py` (`Player.near_misses`), `tests/test_engine.py` (6 neue Tests + 1 aktualisiert), `PLAN.md` (SPEC-003 [x]).

**Mechanik:**
- Beinahe-Treffer (NEAR_MISS) feuert bei Fehlschlag mit ≥2/3 Slots eines UNBEKANNTEN Blueprints. Meldung: *"Einige dieser Dinge scheinen zusammenzugehören, aber es fehlt noch etwas."* — kein Rezept-/Tag-Leak.
- Einmalig pro Blueprint (`Player.near_misses: Set[str]`), danach still bis zum echten Craft (kein Dauer-Belehren derselben Richtung).
- Bekannte Blueprints haben Vorrang: SPECIAL-002 (MISSING_TAG) feuert, wenn der Spieler schon ein Rezept kennt — Vorwissen schlägt Entdeckungs-Hinweis.
- Generischer Fallback: konkretes Merkmal wird nur noch genannt, solange kein Beinahe-Treffer gelaufen ist. Danach: NO_MATCH statt Tag-Leak für unbekannte Blueprints.

**Akzeptanz (alle grün):**
- `test_near_miss_fires_for_rifid_fiber_combo`: stick+plant_fiber → `NEAR_MISS:axe`, keine Leak-Wörter.
- `test_fully_unknown_single_slot_overlap_stays_missing_tag`: berries+mushroom (overlap 0) → kein NEAR_MISS, bleibt MISSING_TAG.
- `test_near_miss_reported_once_only`: axe feuert nur einmal; wiederholte Versuche ≠ NEAR_MISS:axe.
- `test_completing_near_miss_blueprint_succeeds`: nach NEAR_MISS → Volltreffer (flint+stick+plant_fiber) → SUCCESS, Axt in known.
- `test_known_blueprint_still_hints_missing_tag`: Messer bekannt → RIGID+FIBER → MISSING_TAG:FLINT (SPEC-002 vor SPEC-003).
- `test_near_miss_has_label`: `_feedback_message("NEAR_MISS:axe")` → generisch, kein Blueprint-Name.
- 200/200 pytest passed.

**Bekannte Nebeneffekte:**
- `axe_bone` (BONE+RIGID+FIBER) ist ein eigener Blueprint und feuert eigenständigen NEAR_MISS, wenn der Spieler RIGID+FIBER hält (selbe 2 Materialien, aber andere Rezept-Variante). Das ist korrekt: verschiedene Rezepte, verschiedene Hinweise.
- Speer (SHARP_OR_RIGID+RIGID, 2 Slots) kann nie near-missen, weil `overlap < len(bp.slots)` für len=2 und overlap=2 falsch ist (Volltreffer-Restriktion).

**Erwartete Metrik-Wirkung (nächster Play-Job):**
- `discovery_gap` 0.625 → **~0.3–0.4** (Mitte des Bands 0.2–0.6). Der über-Band-Wert, der SPEC-003 reaktivierte, sollte in den Bandbereich zurückkehren.
- `naive_p25` > 0.0 (kein "findet nichts"-Schwanz mehr).
- `session_depth` leicht steigend (Nebeneffekt: Spieler gibt weniger oft "kalt" auf).

**Konstitution geprüft:** kein vorgegebenes Rezept, Experimentiergedächtnis erlaubt, CLI-Text erhalten, stdlib only. Keine Metrik umdefiniert oder entfernt.

---

## 2026-08-17 — [Play] Scorecard flach — Langeweile-Stelle unverändert, guided Bot + cook_meat-Unterreport (cron)

### Headline: `session_depth` 25 flach — nichts an der Entdeckungsschicht geändert
Vollständig flache Scorecard vs. Vorwoche (±0 über alle 10 Metriken). Erwartet: deterministische Seeds (base_seed 20260803), Engine/Content seit 14.08. unverändert (nur REC-001 scorecard + R02 power-math, beide verhaltensneutral). Kein Regress, kein Alarm — die Zahlen bewegen sich nur, wenn ein Entdeckungs-LAYER landet, nicht durch weiteren Inhalt in derselben flachen Liste.

Geführte Erschöpfung (HEAD-Bot, 20 Seeds): full-only-Median **~21**, Range 13–35. Die Decke bleibt: **8 Blueprints + 5 Prozesse + 16 Templates** in unter einer halben Stunde realem Spiel, danach reiner Gather-Grind. Das ist die Langeweile-Stelle — die wichtigste Zahl ist nicht ein Bug, sondern der Punkt, an dem nichts Interessantes mehr passiert.

### Zweitbefund: guided Bot bleibt fragil — 35 % der Seeds verhungern/erfrieren mitten in der Entdeckung
- Nur **13/20** Seeds erreichen alle 8 Blueprints; die übrigen 7 sterben mit hp < 0, body_temp ~23, **Energie 0** (Kälte-Drain verschärft das Verhungern).
- Gipfel-Warmup-Ausflug gehärtet versucht (Feuer+Essen+Unterkühlungs-Abbruch), machte es minimal SCHLECHTER (12 vs 13/20) → revertiert. HEAD-Bot ist das beste verfügbare Messwerkzeug.
- **`cook_meat` erreicht der Bot nur in 5/20 Seeds** — `eat()` frisst das rohe Fleisch (EDIBLE) selbst, bevor er kochen kann. Messwerkzeug-Unterreport des 5. Prozesses, kein Spiel-Bug (ein echter Spieler, der Kochen als Ziel kennt, spielt es voll). → BACKLOG 🔵 Tech Debt (Fix-Richtung: Fleisch vorenthalten + Reihenfolge).

### Drittbefund: Kälte (SPEC-007) ist echte Gegen-Schleife, verschiebt aber die Langeweile-Stelle nicht
Wärme-Haltung (Feuer nachlegen, Fell-Umhang) funktioniert als Mechanik und ist beantwortbar, aber sie ist ein **Wartungsloop**, kein neues Entdeckungsziel. `warmth_stability` 0.46, p25=p75 identisch (flache Policy, deterministisch). Verlängert Sessions konstant, ohne dass etwas Neues passiert — Friktion ohne Neuheit.

### Fazit für Direktor
Agenda unverändert und seit Wochen klar: **SPEC-003 zuerst** (kein Metrik-Gate, schließt die über-Band-`discovery_gap` 0.625), danach SPEC-006 neu bewerten. `session_depth` flach ist der bekannte Blockierer, nicht ein neuer Befund.

---

## 2026-08-16 — [Direktor] Plan-Neufassung: discovery_gap ehrlich über Band → SPEC-003 reaktiviert (cron)

### Scorecard-Verlauf (Trajektorie 03.08. → 14.08.)
| Metrik | 03.08 | 05.08 | 07.08 | 10.08 | 12.08 | 14.08 | Lesart |
|--------|-------|-------|-------|-------|-------|-------|--------|
| actions_to_first_craft | 63 | 62 | 34.5 | 34.5 | 34.5 | 34.5 | ↑ gesund, stabil |
| blueprint_reachability | 1.0 | 1.0 | 0.75 | 0.75 | 0.75 | **1.0** | ↑ REC-001, ehrlich |
| craft_variety | 0.5 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 | ↑ gesund, stabil |
| skill_spread | 0.315 | 0.259 | 0.216 | 0.216 | 0.216 | 0.216 | ↓→ klären (Deutung an Peter) |
| feedback_quality | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | – Decke |
| content_reachable | 0.667 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | – Decke (16/16) |
| session_depth | 24 | 26 | 25 | 25 | 25 | **25** | ↔ **stagniert — Langeweile-Stelle** |
| discovery_gap | 0.5 | 0.25 | 0.375 | 0.375 | 0.375 | **0.625** | ↑ über Band (jetzt ehrlich) |
| forage_pressure | – | – | 0.707 | 0.707 | 0.707 | 0.707 | Probe bis 20.08 |
| warmth_stability | – | – | – | – | – | 0.460 | Probe bis 27.08 |

**Was vorwärts geht:** `blueprint_reachability` 0.75→**1.0** (REC-001 angewendet 14.08.) — der Zähler löst Familien jetzt ehrlich auf. Einstieg gesund & stabil. **Was stagniert:** `session_depth` 25 (die Langeweile-Stelle, Nordstern), `skill_spread` 0.216 (geklärter Befund, wartet auf Peter). **Dunkelste Erkenntnis:** `discovery_gap` ist nach REC-001 **ehrlich 0.625 — über dem Band 0.6**. Naive Spieler finden nur 0.375 des Erreichbaren (1.0). Das Spiel ist aktuell eher schwer- als leicht entdeckbar — das deckt das `session_depth`-Bild (Entdeckungs-Leere nach ~25–31 Aktionen).

### Entscheidung: SPEC-003 REAKTIVIERT
Die frühere Aussetzung ("Überführung-Risiko, d.h. neue Discovery-Mechanik könnte Gap unter 0.2 drücken") galt Content-/Gap-erweiternden Mechaniken. **SPEC-003 ist das Gegenteil** — partieller Match (≥2/3 Slots) gibt generischen "gehört zusammen"-Hinweis, der naive Spieler **konvergiert**: es **schließt** die Lücke (naive_rate ↑, gap ↓), es vergrößert sie nicht. Es ist reines Feedback/Experimentiergedächtnis (Constitution-erlaubt), **kein Metrik-Core-Gate**. Und mit ehrlichem Zähler (REC-001 angewendet) ist seine Wirkung jetzt verifizierbar — die Aussetzungs-Bedingung ("Zähler unverlässlich") ist entfallen. ⇒ Höchster offener Dev-Task.

### Entscheidung: SPEC-006 bleibt zurückgestellt (nicht nur wegen Freigabe)
Zusätzlich zur tool-aware-reachability-Freigabe: Bei `discovery_gap` über Band (0.625) würde eine Tier-2-Schicht (mehr Entdeckungs-Content) die Lücke **weiter anheben** und `blueprint_reachability` regredieren. Reihenfolge ist jetzt zwingend: **erst Gap in Band (SPEC-003), dann neuer Discovery-Content (SPEC-006) neu bewerten.** Beides explizit in PLAN festgehalten.

### skill_spread — klären, nicht fixen
Befund steht (10.08., gehobene Einsteiger-Decke). Wartet auf Peters Deutungs-Entscheid (DECISIONS A/B/C). Metrik unangetastet (Constitution). Als eigener Task geführt, damit Dev nicht blind fixen versucht.

### Triage (BACKLOG)
- SPEC-003 reaktiviert (PLAN-Task), Recovery begründet.
- SPEC-006 zurückgestellt (Freigabe + Gap-Reihenfolge).
- Energie-Okonomie-Decke-Idee (10.08.) als ⚪/🔵 priorisiert notiert, nicht verworfen — mittelfristig ein `session_depth`/`skill_spread`-Hebel, aber erst nach Gap-Stabilisierung.

### Self-Modification (Cron-Jobs)
**Keine Cron-Änderungen.** Die reaktivierte SPEC-003 passt in die bestehenden Dev-Slots (Mo/Mi/Fr); PLAY/Research-Messung unangetastet. Kein echter Gap, der einen neuen Job rechtfertigt. "CONSTITUTION.md ist unantastbar" bleibt in allen Prompts.

### Constitution-Check
Kein Metrik-Core angefasst (`tools/scorecard.py`, `METRICS`, Scorecard-Dateien unverändert — REC-001 war bereits von Peter freigegeben). Kein Rezeptbuch geändert. Probe-Metriken (forage_pressure 20.08., warmth_stability 27.08.) bewusst nur beobachtend, **nicht** als Plan-Ziel. SPEC-003 ist reines Feedback (erlaubt), kein Rezept-Leak. Konform.

### Artefakte
- `PLAN.md` (komplett neu, 3 Sektionen)
- `BACKLOG.md` (Triage-Note 16.08.)
- `JOURNAL.md` (dieser Eintrag)

### Verifikation
`python -m pytest` grün (194 passed) vor jedem Schreiben.

---

## 2026-08-15 — [Dev] R02: `_create_tool` dynamische Slot-Erkennung (Tech-Debt, cron)

### Aufgabe
Alle PLAN-Tasks sind erledigt oder auf Peters Freigabe blockiert (SPEC-006, SPEC-003 =
Metrik-Core-Gate; forage_pressure beobachtend). Kein offener, implementierbarer PLAN-Task.
Stattdessen das letzte konkrete offene 🔵 Tech-Debt (BACKLOG 29.07., **TASK-R02**):
`engine/core.py:_create_tool` hatte `comp.get("head") or comp.get("blade")` als
hartkodierte Slot-Namen-Fallbacks — inkonsistent mit der dynamischen Slot-Erkennung, die
`crafting.py::create_dynamic_item` nach TASK-M03 nutzt.

### Befund (beim Einstieg)
Der alte Code wählte den Effizienz-Träger nur, wenn der Slot `head` oder `blade` hiess.
Der Speer kam nur über den generischen `list(comp.values())[0]`-Fallback zum spitzen Bauteil
(Slots `tip`/`shaft`) — funktionierte zufällig, war aber fragil (IndexError bei
Ein-Slot-Blueprints via `list(comp.values())[1]`).

### Fix (nur `engine/core.py:_create_tool`, Engine-Verhalten unverändert)
- **Dynamische Schärfe-Scan:** der Hauptteil = erster Bauteil mit `sharpness > 0`,
  unabhängig vom Slot-Namen (`tip`/`blade`/`head`/…). Fallback auf den ersten Bauteil bei
  fehlender Schärfe — für alle 8 aktuellen Blueprints identisches Ergebnis wie vorher.
- **Ein-Slot-sicher:** Name `{main}-{result_name} ({[1]})` nur noch bei ≥2 Komponenten,
  sonst ohne Klammer-Teil (vorher `IndexError`-Risiko). Konsistent mit `crafting.py`.
- Defensive `Item("Empty", 0)`-Leer-Fallback (unerreichbar, aber Linter-sauber).

### Verifikation
- `python -m pytest`: **194 passed** (vorher 192; +2 neue Tests in
  `TestRCreateToolDynamicSlotDetection`: power aus scharfem `tip`-Slot, Ein-Slot-Name).
- Metrik-Stabilität: `blueprint_reachability` **1.0**, `discovery_gap` **0.625** — identisch
  (Scorecard liest nur `success`/`blueprint_id`, nie die tool-`power`).
- `find_item_by_tag` prüft nur Tag-Präsenz — der `power`-Wert im tool_tag ist fürs Gameplay
  derzeit ein reiner Indikator; Skalierung des Werkzeug-Nutzens bleibt offen (Idea, nicht Debt).

### Constitution-Check
Kein Metrik-Code angefasst; kein Content/Rezeptbuch geändert; CLI-Text unverändert; stdlib
only; Spielverhalten identisch (nur robustere, konsistente Slot-Erkennung). Messwerkzeug-
Charakter erfüllt — kein Metrik-Entfernen/Umdefinieren.

---

## 2026-08-14 — [Freigabe] REC-001 angewendet + DECISIONS.md für Peter

### Freigabe (Peter)
- **REC-001 freigegeben am 14.08.** und angewendet. Der Rest der freigabepflichtigen Punkte wurde in `DECISIONS.md` zusammengefasst, damit Peter sie in Ruhe durchlesen und einzeln entscheiden kann.

### REC-001 angewendet (Reachability-Zähler kalibriert)
- `tools/scorecard.py::_pair_slots` löst jetzt Tag-Familien (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`, `SHARP_OR_HARD`) wie die Engine auf. Nur Zählweise korrigiert, kein Spielverhalten.
- Verifizierte Wirkung (n=50 / 20 Seeds, deterministisch): `blueprint_reachability` 0.75→**1.0** (alle 8 Blueprints erreichbar), `discovery_gap` 0.375→**0.625** (über Band 0.6).
- **Der "komfortable" Gap war ein Artefakt.** Wahr: naive Spieler findet (0.375) deutlich weniger als erreichbar wäre (1.0). Die Discovery-Lücke ist real groß.
- Neue Tests: `_pair_slots` löst Familien auf, `metric_reachability()==1.0`, `discovery_gap > 0.6`.
- `python -m pytest` → **192 passed**.
- SPEC-003 ist damit verifizierbar, bleibt aber bewusst suspendiert (Gap über Band → weitere Discovery-Mechaniken könnten ihn Richtung Überführung drücken).

### DECISIONS.md (Entscheidungsliste für Peter)
Offene freigabepflichtige Punkte, je mit Optionen + Empfehlung:
1. **skill_spread**-Neuinterpretation (A umdeuten / B umformen / C belassen).
2. **craft_variety** zählt Prozesse (v2) + **content_reachable** dangling-Nodes (v2) — zwei unabhängige Ehrlichmacher.
3. **SPEC-006** Werkzeug-als-Zutat (metrik-seitig blockiert; A tool-aware reachability / B aufschieben / C temporär unrealibel).
4. **forage_pressure** (Probe bis 20.08.) + **warmth_stability** (Probe bis 27.08.) — beobachtend, kein Ziel.

Wartet nichts, was das System anhält — der Direktor läuft weiter, Dev versorgt sich, neue Metriken in Probezeit. Die Liste ist für Qualitäts-Entscheide, nicht zum Freigeben eines Stillstands.

---
## 2026-08-14 — [Dev] Guided-Bot-Screening repariert: Wärme statt Erfrier-Tod (cron)

### Aufgabe
Alle PLAN-Tasks sind erledigt oder auf Peters Freigabe blockiert (REC-001, SPEC-006,
SPEC-003 = Metrik-Core). Kein offener, implementierbarer PLAN-Task. Stattdessen das
einzige konkrete, offene Tech-Debt aus Play 14.08. (🔵): `play/guided_full.py` ist seit
SPEC-007 veraltet — das rekommendierte Guided-Screening friert sich tot und unterschätzt
die Entdeckungsdecke. Reines Play-Messwerkzeug, kein Metrik-Core (CONSTITUTION-konform).

### Befund (beim Einstieg reproduziert)
`guided_full` erfror in fast jedem Seed mitten in der Discovery: `make_fur_cloak` fehlte
in der Prozessliste (→ Stopp bei 4 statt 5 Prozessen), und der Bot legte nie Feuer nach
(`stoke_fire`) → HP-negativ, Ketten brachen ab, die Entdeckungsmenge wurde unterschätzt.
Nach SPEC-007 ist Kälte real: ohne Wärme-Infrastruktur stirbt naives Sammeln am Gipfel
(exposure 1.0) vor der Entdeckung.

### Fix (nur `play/guided_full.py`, Messwerkzeug)
- **`_warmup`:** baut am warmen Waldrand (base_temp 15) die Wärme-Kette Knochen-Messer
  (CUTTING) → Zunder → Feuer; holt kurz einen Kiesel am Gipfel (PROJECTILE, tool-frei)
  fürs rohe Fleisch und näht den Fell-Umhang (Isolation 0.6) — die dokumentierte
  Gegen-Schleife aus Play 14.08.
- **`_fire_at`:** hält am Arbeits-Ort ein aktives Feuer (nachlegen unter `fire_fuel < 15`).
- **`_warm_here`/`eat`:** Feuer am Ort unterhalten, bei Kälte kurzer Rückzug an den
  Waldrand; isst gezielt gegen HP-Blut (Kälte kostet HP unter 35°C).
- **Prozessliste** um `make_fur_cloak` ergänzt (5 statt 4 Prozesse erreichbar).

### Verifikation
- `python -m pytest`: **189 passed** (kein Engine-Code angefasst).
- Screening auf 15 Seeds: **12/15 leeren volle 8/8 Blueprints** (vorher meist
  Erfrier-Tod bei 4–5), `make_fur_cloak` + `start_fire` werden entdeckt; `last_new` 14–36
  auf den primären Seeds. Restliche 3 seeds erfrieren noch in der kalten Gipfel-Sammel-Phase
  (extreme exposure 1.0) — deutlich besser, nicht perfekt.
- Kein Metrik-/Spiel-Code geändert. CONSTITUTION: Messwerkzeug frei; nichts entfernt/umdefiniert.

### BACKLOG
- 🔵 `guided_full.py`-Eintrag auf ✅ erledigt gesetzt.

---

## 2026-08-14 — [Play] Scorecard + Playtest: Langeweile-Stelle unverändert, Kälte als Wartungsloop (cron)

### Befund (headline)
`session_depth` **25 (flach, deterministisch — erwartet)**, geführte Erschöpfung Median
**~31 Aktionen** (n=10, Range 9–47, erweiterter Bot inkl. `make_fur_cloak`). SPEC-007
hat genau EINEN Prozess zur Entdeckungsmenge beigetragen → +~3 Aktionen Erschöpfung.
8 Blueprints + 5 Prozesse + 16 Templates sind in unter 30 Min realem Spiel geleert.
**Die Langeweile-Stelle ist unverändert** — `session_depth` bleibt die Nordstern-Ziel;
SPEC-006 ist der einzige geplante Hebel und blockiert auf Peters Freigabe (tool-aware
reachability).

### Zweitbefund: Kälte (SPEC-007) ist real — als Wartungsloop, nicht als Entdeckung
- Naive Runs sterben jetzt an Unterkühlung (HP-negativ), nicht mehr nur an Hunger; überleben
  aber länger. Gegen-Schleife **funktioniert**: Höhle + endloses Feuer + Fell-Umhang hält
  body_temp bei 37, HP=0 über 400 Ticks (STORM/SNOW verifiziert).
- `warmth_stability` 0.46 im Band, p25=p75=0.46 über alle Seeds — misst geführte
  Einheits-Policy, spricht auf Einstiegsschwierigkeit nicht an. Flach-Erwartung.
- **Der rekommendierte Guided-Bot friert sich tot** (HP −2…−73): nutzt `stoke_fire` nicht,
  kennt `make_fur_cloak` nicht → misst Discovery-Decke nicht mehr sauber. → BACKLOG 🔵.

### Drittbefund
Naive Session-Frist wird heute von Kälte bestimmt statt von Hunger. Nach Entleerung der
Entdeckung bleibt nur Wärme-Frieren. Mehr Überlebensschicht, aber dieselbe Leere in neuer
Farbe.

### BACKLOG
- 🔵 `play/guided_full.py` seit SPEC-007 veraltet (fehlender `make_fur_cloak`/Stoke-Loop).
- 🟡 Kälte = Wartungsloop ohne Entdeckungsziel; beobachten, ob sie in Spielziele einmündet.

### Konstitution
Nichts an Metriken/Antastbarem verändert. Scorecard gerechnet + SCORECARD.md aktualisiert
(v2). Nur Play-reports/BACKLOG/JOURNAL geschrieben.

---

## 2026-08-13 — [Dev] SPEC-007 implementiert: Feuer & Wärme — Gegen-Schleife zur Unterkühlung (cron)

### Aufgabe
PLAN-Task SPEC-007 (oberste offene, aus Research 13.08.): die tote Thermodynamik
lebendig machen — aktives Location-Feuer mit Brennstoff, tragbare Isolation,
hartes `required_tag_in_env`-Gate. Explizit additiv, kein Metrik-Core entfernt/
abgeschwächt (CONSTITUTION-konform).

### Umgesetzt
- **Location-Feuer-Zustand** (`data/locations.py::LocationDef`): `fire_active`,
  `fire_fuel` pro Instanz (kein Cross-Session-Bleed, analog `ResourceNode.stock`).
- **Thermodynamik** (`engine/core.py::_advance_time`): aktives Feuer hebt die
  effektive Umgebungstemperatur (`FIRE_HEAT=40`), Brennstoff sinkt pro Tick, bei
  0 erlischt das Feuer mit `FIRE_OUT`-Meldung (nie still).
- **Feuer entzünden/nachlegen**: `_light_fire` beim `start_fire`-Prozess (wärmt
  schon während des Aufbaus), neue Methode `stoke_fire()` (Holz/Zunder verbraucht,
  `[w]ärmen`-CLI-Action). Ohne Feuer kein Nachlegen, ohne Brennstoff keine Wärme.
- **Tragbare Isolation**: neues `fur_cloak` (CLOTHING, insulation 0.6) über neuen
  `make_fur_cloak`-Prozess (raw_meat + plant_fiber, CUTTING) — der zuvor tote
  `get_total_insulation()`-Pfad lebt. content_reachable bleibt 1.0 (16/16).
- **required_tag_in_env HART**: `cook_meat` (HEAT_SOURCE) braucht ein aktives
  Location-Feuer, sonst ehrlicher `MISSING_ENV`-Fehler; `available_processes`
  blendet es ohne Feuer aus. Das tote Feld aktiviert.
- Feedback-Labels für `FIRE_OUT`/`NO_FIRE`/`MISSING_FUEL`/`MISSING_ENV`;
  `TAG_LABELS` um `CLOTHING`/`HEAT_SOURCE` ergänzt (Konsistenz-Wächter grün).

### Verifikation
- 12 neue/aktualisierte Tests (Feuer-Wärme-Kontrast, Kälte abwendbar durch
  Feuer+Kleidung, Brennstoff-Erlöschen, Stoke, Isolation, cook_meat-Gate,
  content_reachable 1.0). **189 Tests grün.**
- FIRE_HEAT-Balance: 25→40 (an extremer Kälte sonst kaum Wirkung); Probe zeigt
  Berg+STORM+Nacht weiter brutal (→ Shelter suchen), Waldrand+STORM mit Feuer+
  Umhang abwendbar.

### Metrik: `warmth_stability` aufgenommen (additiv, erlaubt)
Die Vorschlags-Metrik (`metrics/proposed/warmth_stability.md`) ist der von SPEC-007
designierte Primär-Beweis → in `MERICS`/`tools/scorecard.py` aufgenommen
(**Probezeit bis 27.08.**, +14 Tage, Richtung None, Band 0.4–0.9). Policy: geführte
survival-sound Ausstattung (Messer/Umhang/Brennholz), Feuer unterhalten, Roh-
Umgebungs-Kälte-Stress zählend. **Erstwert 0.460, deterministisch (p25=p75), im Band.**

### Verzichtet / bewusst nicht
- Kein Metrik-Core entfernt/umdefiniert (nur ergänzt). SPEC-006 bleibt blockiert
  (Peters Freigabe). forage_pressure unangetastet.
- Detail-Balance (FIRE_HEAT/Brennstoff/Band) bleibt laut Spec bei Dev/Direktor —
  Erstwert dokumentiert, Kalibrierung in der Probezeit.

## 2026-08-13 — [Research] SPEC-007: Feuer & Wärme — Gegen-Schleife zur Unterkühlung (Explorations-Modus, cron)

### Auftrag
Freier Explorations-Modus: Mechanik gesucht, die das Spiel als **System** vertieft — bewusst nicht an eine bestehende Metrik gebunden. Feld u.a.: Feuer und Wärme, Verletzung/Heilung, Wetter, Werkzeugverschleiß.

### Befund: tote Thermodynamik ohne Hebel (empirisch verifiziert)
`engine/core.py` rechnet eine komplette Thermodynamik (`_get_ambient_temp` mit base_temp+Wetter+Tag/Nacht, `temp_loss`, `body_temp`, Unterkühlung/Hitzschlag in `_advance_time`). **Aber es gibt keinen einzigen Gegenmechanismus:**
- `get_total_insulation()` summiert `insulation` aller Items mit `CLOTHING`-Tag → **kein Item im Spiel trägt `CLOTHING`**, Isolation ist dauerhaft 0. Der Test `test_components.py::test_total_insulation` konstruiert ein Fell, das real nicht herstellbar ist.
- `fire_pit` (Template) trägt nur `KINDLING` — **wärmt nicht**.
- `cook_meat.required_tag_in_env: "HEAT_SOURCE"` ist weich/nie umgesetzt.
- **Empirisch (Probe):** `mountain_peak` + STORM + Nacht → ambient ≈ −18°C, `body_temp` −1.6°C/tic, ab <35°C HP −1/tic, Tod nach ~80 Ticks **ohne jede Gegenwehr**.

Das ist eine echte System-Schwäche: Die Druck-Schraube (Kälte) existiert, aber der Hebel (Feuer/Kleidung) wurde nie angeschlossen.

### Warum dieses Thema (kein Metrik-Zwang)
Die Constitution will "Wachstum in Systemen, nicht nur in Inhalten" und "Entdecken vertieft". Hier existiert eine ganze Überlebensschicht **kodiert, aber unspielbar** — sie zu verdrahten gibt dem Spieler echte Entscheidungen (Feuer bauen, Brennstoff nachlegen, Schutz suchen, Kleidung herstellen) jenseits des Kombinations-Craftings. Kein Metrik-Anker nötig, kein Metrik-Core berührt.

### Geliefert
- `specs/SPEC-007-fire-warmth.md` — aktives Location-Feuer mit Brennstoff + tragbarer Isolation + hartem `required_tag_in_env`-Gate; Quelle: Long Dark (Brennstoff), UnReal World/Vintage Story (Kleidung/Isolation). Kein Freigabe-Gate (additiv).
- `metrics/proposed/warmth_stability.md` — neue Metrik: Anteil der Kälte-Stress-Ticks mit `body_temp >= 35°C`, Band 0.4–0.9. Misst, ob Kälte durch die Mechanik wirklich *abwendbar* ist.
- `PLAN.md`: SPEC-007 als offener Task.
- Warum die Discovery-Metriken (`session_depth`/`skill_spread`) nur als Nebeneffekt berührt sind: Sie sind nicht Ziel dieses Modus — der Primär-Beweis liegt in der neuen Metrik.

### Verzichtet
Keine bestehende Metrik wurde angefasst. SPEC-006 bleibt blockiert (braucht weiter Peters Freigabe). Kein Kommando/keine Datei im Metrik-Core geändert.

## 2026-08-12 — [Dev] REC-001 Patch-Entwurf geliefert — Reachability-Kalibrierung (cron)

### Aufgabe
PLAN-Task REC-001 (oberste offene): **Patch-Entwurf** für den Reachability-Zählfehler
(`scorecard.py::_pair_slots` löst `TAG_FAMILIES` nicht auf) + **Wirkungsabschätzung** — als Vorschlag an
Peter, **nicht angewendet/committet** (Constitution: Metrik-Berechnung unantastbar bis Freigabe).

### Was geliefert wurde
`proposals/REC-001-pair-slots-reachability-fix.md` — kompletter Patch-Entwurf (Familien auf
Mitglieds-Tags auflösen, analog `engine.core._slot_satisfied`), Impact-Tabelle, Test-Skizze (nur für
späteren Freigabe-Commit), Abgrenzung zu SPEC-006 (tool-aware reachability ist separat).

### Verifizierte Wirkung (n=50, 20 Seeds, deterministisch — Scratch-Simulation, scorecard.py unangetastet)
| | gemeldet (jetzt) | wahr (mit Patch) |
|---|---|---|
| `blueprint_reachability` | 0.75 | **1.0** |
| `naive_discovery_rate` | 0.375 | 0.375 (Engine-consistent, unverändert) |
| `discovery_gap` | 0.375 (im Band 0.2–0.6) | **0.625 (über Band 0.6)** |

Einzige Detailänderung: `spear`, `spear_bound` `False → True`. Alle 6 anderen Blueprints schon `True`.
**Der gemeldete "komfortable" Gap war ein Artefakt der Zählweise; die Discovery-Lücke ist real groß
(naiv findet 0.375 von erreichbar 1.0).**

### Status
- REC-001 in PLAN auf `[x]` gesetzt (Lieferung des Entwurfs ist die Akzeptanz); **Anwendung/Commit der
  Metrik-Änderung wartet auf Peters Freigabe** — unverändert Gatter für SPEC-003.
- Kein Spiel-/Metrik-Code geändert. Commit: nur Vorschlag-Dokument + PLAN/JOURNAL/BACKLOG-Doku.
- `python -m pytest` grün (176).

---

## 2026-08-12 — [Play] Flat week bestätigt — Langeweile-Stelle unverändert bei ~28 (cron)

### Befund
Scorecard komplett flach (±0 überall, 176 Tests grün). Erwartet: Seeds deterministisch
(`base_seed=20260803`), Engine unverändert → kein Regress, kein Alarm.

Guided-Play (10 Seeds, survival-sound, `play/guided_full.py`): Die komplette Entdeckungsmenge
(8 Blueprints + 4 Prozesse + 15 Templates) wird in **9–40 Aktionen geleert**, Median-Exhaustion
**~28**. Das schließt exakt an die naive `session_depth`=25 (p75 43) an — der Zahl hängt an der
Discovery-Content-Decke, nicht an Spielerfähigkeit.

### Die Langeweile-Stelle (Kopfzeile des Reports)
Nach Aktion ~28 (Median) gibt es kein neues Blueprint, keinen Prozess, kein Template mehr.
Danach fällt der guided bot auf reines `gather_at(random)` zurück. Das ~halbstündige
Discovery-Spiel ist ausgeschöpft; der Rest ist Sammel-Schleife. **Unverändert die Stelle,
wo nichts Interessantes mehr passiert.**

### Keine neuen Bugs
Alle verdächtigen Punkte sind bereits dokumentiert und unverändert gültig:
- `discovery_gap` 0.375 (gemeldet) vs. wahr ~0.625 — REC-001 `_pair_slots`-Familien-Zählfehler, braucht Peter.
- `forage_pressure` 0.707 über Band (Probe bis 20.08.) — beobachtend.
- `spear`/`spear_bound` im Zähler "false", enginseitig craftbar — kein Engine-Bug.

### Empfehlung / Stand
Der einzige Hebel für `session_depth` ist eine Engine/Content-Änderung, die die Entdeckung
*vertieft* — SPEC-006 (Werkzeug-als-Zutat) ist genau das, bleibt aber auf Peters Metrik-Freigabe
(tool-aware reachability) blockiert. REC-001 derselben Gate-Familie. Beide liegen korrekt beim
Direktor/Peter.

Kein Spiel-/Metrik-Code geändert. Commit: Play-Report + Journal nur.

---

## 2026-08-11 — [Dev] SPEC-006: Implementierung blockiert — Tool-Gated-Tier-2 regrediert `blueprint_reachability` (cron)

### Aufgabe & Versuch
Offene PLAN-Task SPEC-006 (oberste nicht-gates Abhängigkeit): Werkzeug-als-Zutat-System (Tier-2-Blueprints mit `tool_tag`-Slot + einmaliger `NEW_COMPONENT:<tag>`-Reveal) soll `session_depth` aus der ~25-Stall-Grenze heben. Vor Umsetzung gegen `tools/scorecard.py` validiert — und dabei ein **Spec-fataler Annahmefehler** gefunden.

### Befund — SPEC-006-Annahme „reachability bleibt 1.0" ist falsch
Der Spec behauptet: „Tier-2-Blueprints sind von Start an im `blueprint_reachability`-Zähler erreichbar (Reachability prüft nur, ob es eine legale Tag-Kombination gibt)." **Das implementierte `metric_reachability` tut das nicht.** Es sammelt nur Rohstoffe (3 Orte × 8× Gather), **baut nie ein Werkzeug**, und `_pair_slots` matcht Slot-Tags literal über `by_tag.get(tag)`. Ein Tier-2-Blueprint mit `CUTTING`/`CHOPPING`-Slot ist im Fresh-Gather-Lauf prinzipiell nie erfüllbar (kein Item trägt den Tag vor dem Toolbau) → zählt als **unreachable**.

**Messung (n=20 reproduziert):** aktuell `blueprint_reachability` = **0.75** (8 Blueprints, nur 6 reachable — `spear`/`spear_bound` bereits family-bedingt unreachable; das ist exakt der REC-001-Zählfehler, wahr ~1.0). Ergänzt man die 3 vorgeschlagenen Tool-Gated-Tier-2-Blueprints (`rope`/`spear_cord`/`shelter_dry`), sinkt der Zähler auf:
- +1 → **0.667**, +2 → **0.600**, +3 → **0.545**

Ein klarer Regress auf einer geschützten Metrik (`höher = besser`, Version 1). Die Metrik zu kompensieren hieße `scorecard._pair_slots` anzufassen — **Peters Freigabe** (Constitution: scorecard.cpp + METRICS = unantastbarer Kern; das ist die REC-001-Gate-Familie).

### Konsequenz
**SPEC-006 in dieser Form ist nicht schadlos lieferbar.** Der zentrale Hebel (Tool-gated Tier-2) drückt die Metrik, die er nicht verändern soll. Und er reicht über REC-001 hinaus: selbst mit dem Familien-Fix blieben Tier-2 unreachable, weil der Zähler auch dann keine Werkzeuge *baut* — es braucht eine echte „tool-aware reachability" (Zähler modelliert Tool-Bau als Vorschritt). Beides = Metrik-Berechnung = Peters Entscheidung.

Aus demselben Grund wurde **nichts** angefasst: auch der `NEW_COMPONENT`-Reveal ohne Tier-2-Blueprints wäre irreführend (Hinweis „lässt sich weiter verbinden", wenn nichts weiter verbindbar ist) — reiner Scaffolding-Code, YAGNI.

### Empfehlung an Peter / Direktor
1. **Auf Freigabe legen, nicht implizit implementieren.** SPEC-006 gehört in dieselbe Familie wie REC-001 (Metrik-seitige Freigabe nötig), nicht in die normale Dev-Linie.
2. Optionen: **(A)** reachability zu „tool-aware" erweitern (Freigabe) → Tier-2 landet sauber, `session_depth` steigt wie beabsichtigt. **(B)** SPEC-006 zurückstellen, bis das REC-001-Gesamtpaket (Familien-Auflösung + tool-aware) entschieden ist. **(C)** Tier-2 *ohne* Tool-Gate als flache Items — nicht empfohlen (kaum `session_depth`-Gewinn, streift Nicht-Ziel „Content als Selbstzweck").
3. `discovery_gap` bleibt ohnehin REC-001/SPEC-003 vorbehalten — jetzt gilt das auch für `blueprint_reachability` und damit für die ganze „tool as ingredient"-Schicht.

**Ehrlichkeit:** Der Kern-Versuchswert von SPEC-006 (`session_depth` steigend) ist ohne Metrik-seitige Freigabe nicht lieferbar — die Erkenntnis „jedes Entdeckte kann Zutat sein" ist System-Tiefe, aber sie erfordert, dass der Fitness-Zähler das auch misst, sonst verlieren wir auf Metrik A, was wir auf Metrik B gewinnen wollen.

Kein Spiel-/Metrik-Code geändert. Commit: nur JOURNAL/BACKLOG/PLAN-Dokumentation.

---

## 2026-08-11 — [Research] SPEC-006: Zweite Entdeckungsschicht — Werkzeug als Zutat (`session_depth`)

### Metrik-Wahl (aus den Zahlen)
Schwächste/stagnierende Metrik: **`session_depth` = 25**, flach über vier Messungen (24→26→25→25), Richtung „höher besser“. Play 10.08. bestätigt präzise: alle 8 Blueprints + 4 Prozesse + 15 Templates sind in **~25–37 Aktionen geleert** (unter optimalem Spiel nicht höher als naiv) — danach verheißt nichts mehr eine neue Entdeckung; `_run_session_depth` stoppt am `stall_limit` bei unverändertem `_novelty_set`.

**Warum nicht die anderen Band-/Schwächen-Metriken:** `discovery_gap` ist durch REC-001 unzuverlässig (wahr ≈0.625, Zählfehler) und braucht Peters Freigabe — kein verifizierbares Ziel bis dahin (SPEC-003 bleibt suspendiert). `forage_pressure` 0.707 ist Probe bis 20.08., definitionsabhängig hoch, keine Entscheidung vor Probeende. `session_depth` ist die sauberste, verifizierbare Langeweile-Metrik und PLAN-Priorität #1.

### Mechanik (aus Spielen)
Kernbefund: Alle Blueprints sind von Start an craftbar (nur Rohstoff-Slots, `min_survival_req=0`). Ein gebautes Werkzeug fügt Tags hinzu (`CHOPPING/CUTTING/PIERCE/SHOVEL`), aber **kein Blueprint nimmt ein Werkzeug als Komponente** — Discovery ist flach und endlich, Entdeckung zeugt keine Entdeckung. Quelle: **Little Alchemy** (Entdecktes wird selbst zur Zutat — selbstverstärkender Raum) + **Don't Starve / Prototyper** (Besitz einer Komponente schaltet Richtungswissen frei). Adaption: kleiner Tier-2-Blueprintsatz, dessen Slots ein `tool_tag` verlangen (Engine matcht das schon über `_slot_satisfied`), plus einmaliger `NEW_COMPONENT:<tag>`-Reveal pro neuem Werkzeug-Typ → Discovery wird gestuft statt flach, der stallende Runner bekommt nach der alten Erschöpfungsstelle ein neues Ziel.

### Abgelegt
- `specs/SPEC-006-second-order-crafting.md` — Problem/Mechanik/Adaption (Dateien: `blueprints.json`, `components.py`, `core.py`, `tests`)/Akzeptanz/Metrik-Wirkung.
- PLAN.md Task ergänzt (offen, Dev von oben nach unten).
- Constitution-geprüft: kein Rezept-Leak (Hinweis nennt weder Item noch fehlenden Tag), stdlib only, keine Metrik entfernt/abgeschwächt, Discovery vertieft statt abgekürzt. Kein Metrik-Code angefasst.

### Risiko / Ehrlichkeit
Effektgröße hängt am Tier-2-Umfang: nur 1–2 Blueprints ergeben wenig; 3 mit Werkzeug-Gate verschieben die Stall-Grenze realistisch von ~25 auf ~35+. `discovery_gap`: nicht beabsichtigt (bleibt REC-001/SPEC-003 vorbehalten). Der Spec definiert das System (Werkzeug-als-Zutat + Einmal-Reveal + gestufte Erreichbarkeit); Detail-Balance (exakte Tier-2-Items) entscheidet der Direktor/Dev.

---

## 2026-08-10 — [Dev] skill_spread-Regress: Befund — kein echter Tiefen-Regress, sondern gehobene Einsteiger-Decke (cron)

### Rückwärtsprüfung (nur Lese-Analyse, kein Metrik-Code angefasst)
`skill_spread = (opt − rnd)/opt`, aktuell **0.216** (reproduziert, 20 Seeds). Zerlegt:
- **opt** (bestes Überleben über alle Locations, dort bleiben+essen+sammeln) = **240.5** (hidden_cave). Weit unter HORIZON 500.
- **rnd** (zufälliges Wandern) = **189.0**.
- spread = (240.5−189)/240.5 = **0.216**.

**Kernbefund — die Decke ist Ökonomie, nicht Regress:** Entfernt man die Ressourcen-Erschöpfung (SPEC-004) per Test-Harness (alle Nodes `max_stock=1e9`, nie depleted), ändert sich weder opt (bleibt 240.5) noch rnd (bleibt 189). Der optimale Spieler verhungert trotz unendlich viel Nahrung bei ~240 Ticks — die Überlebens-Decke ist **Energie-/Hungerwirtschaft** (Sammel-Energiekosten > Kalorien-Ertrag), ein System, das in den letzten Patches nicht angefasst wurde. Beim optimalen Lauf fällt HP exakt mit 1.0/Tick (HUNGER-SCHADEN), bodytemp ~26–27 °C, Inventar-Food leer — reine Hungerlinie, keine Entleerungs-Stelle.

**Konsequenz:** Der Zähler (opt, die Experten-Decke) ist stabil und spieldesign-gebunden. Der Rückgang 0.315→0.216 kann also nicht aus einem *schlechter gewordenen* optimalen Spiel stammen, sondern aus dem **Nenner** — Zufalls-/Naive-Spiel überlebt näher an optimal. Das deckt sich exakt mit dem dokumentierten Einstiegs-Verlauf im selben Fenster: `actions_to_first_craft` 63→34.5, mehr Werkzeugpfade (SPEC-002, 3 Varianten je Axt/Messer), `naive_p25` 0.0→0.5, `naive_discovery_rate` 0.5→0.75.

### Befund
**0.216 bildet echte Spielerfahrung ab — aber nicht als „Tiefen-Regress".** Es spiegelt eine **gehobene Einsteiger-Decke**: unkundiges Spiel überlebt jetzt näher am Optimum, das Spiel ist weniger frustrierend für Neue. Die Experten-Decke (opt) ist unverändert. `direction="höher = besser"` labelt diesen Fall als Verschlechterung, obwohl es eine gewollte Einstiegs-Erleichterung ist (Plan-Hypothese „leichte Einstiege schrumpfen die optimale vs. zufällige Überlebensspanne" bestätigt sich).

**Ehrliche Unsicherheit:** Historische opt/rnd-Werte liegen nicht getrennt in den Scorecard-Archiven (nur aggregierter Wert). Ich kann die Stabilität des Zählers **jetzt** zeigen (ökonomie-gebunden, Depletion-unabhängig), aber nicht über das 03.08→07.08-Fenster definitiv beweisen — die Einstiegs-Daten dort stützen die Nenner-Deutung jedoch klar.

### Empfehlung an Peter (braucht Freigabe — Metrik unangetastet gelassen)
Kein Korrektur-Bedarf am Spiel. Zwei Optionen für die **Metrik-Deutung** (nicht angewendet, Constitution):
- **A (umdeuten):** Formel behalten, Bedeutung neu fassen — fallender skill_spread = Kindheit-der-Einstiege, kein Tiefenverlust. Richtungs-Label in SCORECARD müsste angepasst werden.
- **B (anders messen):** Das Verhältnis vermischt zwei Dinge — Experten-Decke (opt) und Einsteiger-Kindness (Floor). Sauberer: opt separat ausweisen (Experten-Decke) statt als Ratio; wäre ein Metrik-Version-Bump (Schema 2→3), Peters Entscheidung.
Nebenbefund (BACKLOG-Kandidat): auch das *optimum* kappt bei ~240 — die Survival-Decke und die Discovery-Leere (`session_depth`~25) sind zwei Erscheinungsformen derselben niedrigen System-Obergrenze; die „Langeweile-Stelle" ist nicht nur Content, sondern auch Ökonomie-Decke.

---

## 2026-08-10 — [Dev] SPEC-005: Mengen-basiertes Mehrfach-Slot-Crafting (cron)

### Was
`Inventory.add` verschmilzt gleichnamige Items zu einem Stack (`quantity N`). Ein Blueprint, dessen zwei Slots dasselbe Tag-Profil verlangen (Speer 2× RIGID), war deshalb nicht aus einem einzigen 2×-Stack craftbar — der Spieler musste zwei distinkte Materialien kombinieren (reeds+Ast statt 2×Ast), obwohl er genug Stöcke besass.

### Befund beim Einstieg
Die Engine (Permutations-Loop + `_create_tool`) unterstützte Mehrfach-Nutzung desselben Stack-Objekts bereits: `spear` aus `[stick, stick]` (qty=2) craftete fehlerfrei, Verbrauch korrekt (qty=3 → qty=1). **Echte Lücke war die Mengen-Grenze:** Stack qty=1, zweimal selektiert, craffete den Speer trotzdem — `_create_tool` entfernt den Stack beim ersten Durchlauf und `continue`t ihn beim zweiten, ohne Abbruch. Ergebnis: Item aus dem Nichts erzeugt (Fehlstart), 1 Verbrauch statt 2.

### Fix
- `engine/core.py::execute_experiment`: Menge-Validierung vor der Blueprint-Schleife. Taucht ein Stack-Objekt N-mal in `selected_items` auf, muss `quantity >= N` sein, sonst `NOT_ENOUGH_QUANTITY`-Feedback (kein Fehlstart). Zählung über Objekt-Identität (`id`) — zwei distinkte Stacks bleiben unberührt.
- `_feedback_message`: neues Label `NOT_ENOUGH_QUANTITY` → „Dafür brauchst du mehr von demselben Material." (kein Rezept-Leak).
- `main.py` Experiment-Command: listet Inventar mit Mengen (`[i] Nx Name`), damit der Spieler einen Stack mehrfach auswählen kann.

### Verifikation
`python -m pytest`: **176 passed** (vorher 170; +6 neue Tests in `TestStackMultiSlot`: 2×-Stack craftbar, Verbrauch qty=3→1, unzureichende Menge → Feedback ohne Verbrauch, distinkte Kontrolle, Messer-Kontrolle, Label). Bestehende Pfade (distinkte Materialien) unverändert grün. Kein Metrik-Code angefasst, stdlib only, kein Rezeptbuch geändert — Constitution-konform. Erwartete Wirkung: `craft_variety`/`session_depth` leicht stützend (mehr legale Kombinationen pro Materialsortiment).

---

## 2026-08-10 — [Play] Langeweile-Stelle präzise vermessen; Fixes bestätigt (cron)

### Headline-Befund
Die Langeweile-Stelle ist unverändert, aber diesmal **unter optimalem Spiel präzise vermessen**: Ein survival-sicherer Guided-Runner leert **alle 8 Blueprints + alle 4 Prozesse + alle Templates in ~25–37 Aktionen** (Seeds @28, @24, @37). Deckt sich mit `session_depth`=25. Danach existiert keine Neuheit mehr — das Discovery-Spiel ist nach ~halber Stunde fertig, Rest ist Sammel-Grinding. Kein Bug, die Content-/System-Obergrenze. Plan-Prioritäten (SPEC-005, REC-001, Entdeckungs-Tiefe) adressieren genau das.

### Scorecard flach (±0 überall)
Deterministische Seeds + keine Engine-Änderung seit 07.08. → identische Werte. Erwartet, kein Alarm. Kontext für Direktor: Play-Job erzeugt bei unveränderter Engine kein neues Signal.

### Verbessert bestätigt
- **B06/B07 sauber zu.** `content_reachable` 1.0 jetzt **real** (15/15): `log_oak` (Eichenstamm per Axt) und `clay_lump` (Ton per Axt/SHOVEL) korrekt sammelbar — kein "Unbekannt" mehr.
- **Volle Prozess-Kette durchspielbar & lohnend:** knap → knife → tinder → fire → cook_meat (400 kcal vs 150 roh). Alle 4 Prozesse menschenerreichbar (letzte Woche suggerierte mein schwacher Bot irrtümlich nur make_sharp_stone).

### Kein neuer Bug
Nichts Neues reproduziert, kein Frustpfad. Bemerkung: guided-Wert trotz optimalem Spiel nicht > naive `session_depth` — die Zahl klebt an der Entdeckungs-Obergrenze, nicht an der Spieler-Unfähigkeit.

### Offen (unverändert)
- `discovery_gap` 0.375 (wahr ≈0.625) — REC-001 braucht Peters Freigabe. Vor SPEC-003.
- `forage_pressure` 0.707 — Probezeit-Kalibrierung bis 20.08.

---

## 2026-08-09 — [Direktor] Plan-Neufassung, Triage, Kalibrierungs-Priorität

### Scorecard-Verlauf (Trajektorie 03.08. → 05.08. → 07.08.)
| Metrik | 03.08 | 05.08 | 07.08 | Lesart |
|--------|-------|-------|-------|--------|
| actions_to_first_craft | 63 | 62 | 34.5 | ↑ deutlich vorwärts (flint-Funnel weg) |
| craft_variety | 0.5 | 1.0 | 3.0 | ↑ vorwärts (SPEC-002) |
| content_reachable | 0.667 | 1.0 | 1.0 | ↑ geschlossen (13/13, danach 15/15) |
| session_depth | 24 | 26 | 25 | ↔ stagniert — die Langeweile-Stelle |
| skill_spread | 0.315 | 0.259 | 0.216 | ↓ fallend — klären |
| feedback_quality | 1.0 | 1.0 | 1.0 | – Decke, konstruktionsbedingt |
| discovery_gap | 0.5 | 0.25 | 0.375 | ⚠️ untertrieben (Zählfehler) |
| forage_pressure | – | – | 0.707 | Probezeit, kein Ziel |

**Was vorwärts geht:** Einstieg deutlich besser — erste Craft viel früher, dreifach mehr Craft-Varianten, inhaltlich alles erreichbar. **Was stagniert:** `session_depth`~25 — die Entdeckungs-Leere. **Was fällt:** `skill_spread` 0.315→0.216 (muss erklärt werden). **Schärfste Erkenntnis:** `discovery_gap` ist wegen eines Reachability-Zählfehlers unterschätzt; wahrer Wert ≈0.625 statt 0.375.

### Metrik-Erkenntnis (Kernbefund der Woche)
`scorecard.py::_pair_slots` löst Tag-Familien (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`) nicht literal auf → `spear`/`spear_bound` fälschlich unreachable. Gemeldet `blueprint_reachability` 0.75, wahr 1.0 → wahrer `discovery_gap` ≈ 0.625 (über Band 0.6), nicht 0.375. Kein Spiel-Bug, Zählfehler. **Kalibrierung hat Vorrang vor jeder neuen Discovery-Mechanik** → REC-001 (braucht Peters Freigabe nach Constitution), SPEC-003 bleibt suspendiert.

### Entscheidungen / Triage
- **BACKLOG:** B06/B07 (beide in Dev 07.08. gefixt) → zu „✅ Triaged" verschoben. Stack-Verschmelzung → **SPEC-005 promotet**. Reachability-/content_reachable-/craft_variety-Metrik-Änderungen → konsolidiert als Metrik-Anfrage an Peter (REC-001). forage_pressure bleibt Probezeit bis 20.08.
- **PLAN.md neu:** 3 Ziele — (1) Entdeckungs-Tiefe `session_depth` steigern, (2) Craft-Tiefe `craft_variety`/`session_depth` verbreitern, (3) Messung kalibrieren `discovery_gap` (Peter). Tasks: REC-001 (Kalibrierung, braucht Freigabe), SPEC-005 (Mengen-Matching), skill_spread-Regress klären, SPEC-003 (suspendiert), forage_pressure (beobachtend).
- **specs/SPEC-005-stack-multi-slot.md** angelegt (Stack mit quantity N füllt N identische Slots — schließt die 2×-Ast/Craft-Lücke, Hand-feeling-Fix ohne Content).

### Constitution-Check
Kein Metrik-Core angefasst (`tools/scorecard.py`, `METRICS`, Scorecard-Dateien unverändert) — nur als Freigabe-Bedarf an Peter gehalten. Kein Rezeptbuch geändert; keine Metrik entfernt/umdefiniert/abgeschwächt. Konform.

### Self-Modification (Cron-Jobs)
**Keine Cron-Änderungen diese Woche.** Rollen/Play/Measurement bleiben unangetastet; die gesetzten Tasks passen in die bestehenden Dev-Slots. „CONSTITUTION.md ist unantastbar" bleibt in allen Prompts.

### Artefakte
- `PLAN.md` (komplett neu)
- `BACKLOG.md` (Triage, Archive, Annotationen)
- `specs/SPEC-005-stack-multi-slot.md` (neu)
- `JOURNAL.md` (dieser Eintrag)

### Nächste Schritte
- **Peter:** Freigabe/Feedback zu REC-001 (Reachability-Zähler) + den drei konsolidierten Metrik-Änderungen (craft_variety-zählt-Prozesse, content_reachable-dangling-Nodes, skill_spread-Neuinterpretation).
- **Dev:** SPEC-005 zuerst, dann skill_spread-Regress; REC-001 erst nach Peters Freigabe berühren.
- **Play (Mo 10.08.):** nächste Scorecard — prüft zugleich, ob B06/B07-Fix `content_reachable` konstant hält.

---

### Task
Kein offener, implementierbarer PLAN-Task (SPEC-003 suspendiert bis Direktor; Rückwärtsprüfung/Baseline = Play-Job). Stattdessen die beiden 🔴 Content-Bugs aus BACKLOG (B06/B07, von zwei Play-Sessions bestätigt): Nodes referenzieren Templates, die es nicht gibt → Spieler bekommt "Unbekannt"-Müll statt eines echten Items. Direkt `content_reachable` (15/15) und die Kern-Verheißung "Axt bauen, um Holz/Ton zu sammeln".

### Fix (Content-only, verfassungskonform)
- **B06 `log_oak`:** Template in `items.json` angelegt ("Eichenstamm", RIGID+WOOD). War: Node existierte, Template nicht → "Unbekannt". Jetzt fällt die Axt (CHOPPING) einen echten Eichenstamm.
- **B07 `clay_lump`:** Template angelegt ("Tonklumpen", CLAY) **und** die Axt als Grabwerkzeug gedacht: `axe`/`axe_bone`/`axe_stone` tragen jetzt zusätzlich das funktionale Tag `SHOVEL` (BACKLOG-Fixrichtung: "Axt als Grabwerkzeug", kein neues Werkzeug nötig). Damit ist der vorher doppelt-tote Ton-Pfad (fehlendes Werkzeug + fehlendes Template) erreichbar.
- `TAG_LABELS` um `WOOD`/`CLAY` ergänzt (Label-Vollständigkeits-Test bleibt grün).

### Akzeptanz-Check
- `log_oak`/`clay_lump` als Templates geladen (kein "Unbekannt") ✓
- Axt fällt Eichenstamm im Waldrand ✓; Axt gräbt Ton in der Höhle ✓
- `python -m pytest`: **170 passed** (vorher 165) — inkl. 5 neuer Regressionstests
- Metrik-Idempotenz: `content_reachable` 1.0 (15/15, vorher 13/13 mit 2 dangling, die gar nicht zählten), `discovery_gap` 0.375, `session_depth` 25, `craft_variety` 3.0 — keine Verschiebung.
- Keine Metrik umdefiniert/entfernt — nur Content ergänzt (freigegeben).

### Constitution-Check
Content/Items/Tags hinzugefügt — ausdrücklich frei (keine Freigabe nötig). Keine Metrik-Berechnung angefasst. Tag-basiertes Crafting unverändert. Vertieft Entdecken (zwei vorher tote Rohstoffe sind jetzt echte Funde), kein Content-Selbstzweck.

---

## 2026-08-07 — [Play] Langeweile-Stelle bleibt; discovery_gap war unterschätzt

### Headline-Befund
Die Entdeckungs-Leere ist unverändert die Langeweile-Stelle: 8 Blueprints + 4 Prozesse + 13 Templates, eine geführte Session leert alles in ~40 Aktionen (tick ~96). `session_depth`=25 — SPEC-004 hob das p75 (33→43), aber nicht die Entdeckungs-Tiefe.

### Wichtigste neue Erkenntnis — Reachability-Zählfehler
`scorecard.py::_pair_slots` kann Tag-Familien (`SHARP_OR_RIGID`, `RIGID_OR_FIBER`) nicht auflösen → meldet `spear`/`spear_bound` als unreachable, obwohl die Engine beide craftet (alle 8 Blueprints SUCCESS, verifiziert). Gemeldete reachability 0.75, wahr 1.0 → **wahrer `discovery_gap` ≈ 0.625 (über Band), nicht 0.375.** Der gemeldete "komfortable" Gap war ein Artefakt. Kein Spiel-Bug; Metrik-Berechnung → braucht Peters Freigabe.

### SPEC-003-Konflikt — neu bewertet
Bisher: Gap bei 0.25→0.375, "nah an Überführung, SPEC-003 aussetzen". Mit korrigiertem Zähler liegt der wahre Gap eher über dem Band (0.625). Damit ist SPEC-003-Aussetzung weiterhin richtig, aber aus dem anderen Grund: nicht Überführung, sondern Unsicherheit über den wahren Wert. **Erst Reachability-Zähler kalibrieren, dann über Discovery-Mechaniken entscheiden.**

### Verbessert seit 05.08.
- flint-Funnel entschärft (SPEC-002): naive Sessions bauen knife_bone/knife_stone/axe_stone/spear. `craft_variety` 1.0→3.0.
- `actions_to_first_craft` 62→34.5 — erster Craft landet früher.

### Offen bestätigt
- B06 `log_oak` ("Unbekannt"×2 in geführter Session), B07 `clay_lump` (SHOVEL-Tag ohne Träger) — beide unverändert.
- forage_pressure 0.707 über Band, Kalibrierung bis 20.08.

---

## 2026-08-06 — [Dev] SPEC-004: Ressourcenerschöpfung & Regeneration (Foraging)

### Task
`SPEC-004-resource-depletion.md` — vorratsbasierte Nodes: Ernte reduziert `stock`, Erfolg skaliert `chance * stock/max_stock`, Regeneration über `_advance_time`. Gegen die Langeweile-Stelle (Play 05.08.): Rotation/Rückkehr erzwingen, statt unendlichem Melken desselben Nodes. Metrik-Vorschlag `forage_pressure` als Probezeit-Metrik aufgenommen.

### Mechanik (implementiert)
- **`data/locations.py`/`loader.py` — `ResourceNode` erweitert:** `max_stock` (default 10), `regen_per_tick` (default 0.05), `harvest_cost` (default 1), veränderlicher `stock` + `depleted`-Flag. Fresh pro Engine-Instanz (kein Cross-Session-Bleed, deterministisch pro Seed).
- **`locations.json` — pro-Node-Balance:** Flaggschiffe knapp/langsam (`flint_shard`, `bone`: max_stock 6, regen 0.03), Grundstoffe großzügig (`stick`/`pebble`: 30, regen 0.15). Knappheit gezielt auf den bestehenden flint-Bottleneck gelegt, nicht flächig.
- **`engine/core.py::gather()`:** `eff_chance = chance * (stock/max_stock)`; Vorrat um `harvest_cost` reduziert; erschöpfter Node → neuer Reason `DEPLETED` + `_feedback_message("DEPLETED")` = *"Diese Stelle ist erschöpft. Komm später zurück."* (nie stilles "nichts").
- **`_advance_time()`:** regeneriert alle Nodes über verstrichene Ticks; `depleted` erholt sich erst, wenn genug Zeit eine Ernte-Portion aufgefüllt hat. Andere Orte regenerieren, während man unterwegs ist.
- **Design-Verfeinerung:** `depleted`-Flag nötig, weil ein einzelner Gather-Tick sonst eine homöopathische Regeneration nachschiebt und der Node nie ehrlich "erschöpft" melden würde. Generöse Grundstoffe oscilieren kurz an der Schwelle (gewollt — sollen kein Gate sein), knappe Flaggschiffe bleiben stabil erschöpft (gewollt).

### Metrik — `forage_pressure` (Probe bis 20.08.)
In `METRICS` aufgenommen (Band 0.1–0.5, keine Richtung, `probation_until=2026-08-20`). **Erstwert 0.71 (über Band)** — siehe BACKLOG: Definition `stock < max_stock` ist ein sehr sensibler Schwellenwert; Erstwert deutet auf Grind-Gefühl oder Kalibrierungs-Missmatch. Bewusst im Probezeit-Netz gelassen, statt still nachzujustieren.

### Akzeptanz-Check
- Wiederholtes Sammeln → Erschöpfung mit `DEPLETED`-Meldung, nie stilles "nichts" ✓
- `_advance_time(N)` regeneriert bis `max_stock`; erschöpfter Node wieder erntbar nach Zeit ✓
- Erfolg skaliert mit `stock/max_stock` ✓
- `DEPLETED` hat Label in `_feedback_message` (Label-Vollständigkeit bleibt grün) ✓
- `python -m pytest`: **165 passed** (vorher 158) ✓
- Metrik-Werte gehalten: `session_depth` 24→25, `discovery_gap` 0.375 (im Band), `content_reachable` 1.0, `feedback_quality` 1.0; `forage_pressure` 0.71 (Probe, über Band).

### Constitution-Check
Kein Rezeptbuch geändert; CLI-Text bleibt; stdlib only; keine bestehende Metrik entfernt/umdefiniert — nur neue `forage_pressure` in Probezeit ergänzt (erlaubt, keine Freigabe nötig). Vertieft Entdecken (lebende Welt, Rotations-Entscheidung), kein Content-Selbstzweck.

---

## 2026-08-06 — [Research-Explore] SPEC-004: Ressourcenerschöpfung & Regeneration

### Auftrag
Explorations-Modus — freie Suche nach System-Vertiefung, **kein** Metrik-Anker. Kontext: CONSTITUTION.md, Scorecard 2026-08-05, Play-Report 2026-08-05 gelesen.

### Befund (die System-Schwäche)
Play 05.08. nennt die Langeweile-Stelle schärfer als jede Metrik: nach ~40 Aktionen ist die Entdeckungsmenge (2 Familien + 4 Prozesse + ~12 Templates) geleert, übrig bleibt "sinnloses Sammeln". **Ursache hinter dem Symptom:** `GameEngine.gather()` wirft bei jedem Aufruf gegen eine feste `node.chance` — Nodes sind **unendlich und kostenlos**. Kein Grund für Ortswechsel, Zeit ohne Sammel-Wert, keine Rückkehrmotivation. Terrain/Zeit/Wetter existieren, sind aber fürs Sammeln bedeutungslos. Eine System-Leere, die keine Metrik verlangt, aber `session_depth` strukturell kurz hält.

### Mechanik
**Vorratsbasierte Nodes mit Erschöpfung + zeitbasierter Regeneration** (URW: selbsterhaltende Welt/Rotation; Vintage Story/Zomboid: Depletion + Respawn). Ernte reduziert `stock`; Erfolg skaliert `chance * stock/max_stock`; Regen läuft über `_advance_time` → Ort und Zeit werden zu echten Ressourcen. Erzwingt Rotation + Rückkehr statt unendlichem Melken desselben Nodes. Vertieft Entdecken, **ohne** neuen Content (gegen "Content-Menge als Selbstzweck").

### Metrik-Wirkung (ehrlich)
`session_depth` **steigend** (primärer Effekt, gegen die Langeweile-Stelle) — aber nur wenn Agenten Regen tatsächlich nutzen, sonst Reibung. **Keine** beabsichtigte Änderung an `discovery_gap`/`craft_variety`/`content_reachable`/`feedback_quality` — bewusst eine Mechanik, die keine bestehende Metrik bewegt. Konform zur Constitution: nur **neue** Metrik ergänzt, keine entfernt/abgeschwächt.

### Artefakte
- `specs/SPEC-004-resource-depletion.md` (neu)
- `metrics/proposed/forage_pressure.md` (neu) — Band 0.1–0.5, misst ob Knappheit *gefühlt* wird, nicht trivial zu heben (echte Node-Dynamik über Agent-Sequenzen)
- `PLAN.md` — SPEC-004 als offener Task
- `JOURNAL.md` — dieser Eintrag

### Constitution-Check
Kein Rezeptbuch; CLI-Text bleibt; stdlib only; Metrik-Core unangetastet (nur Ergänzung). Verstoß nicht gefunden.

---

## 2026-08-05 — [Dev] SPEC-002: Blueprint-Familien + Discovery-Feedback

### Task
`SPEC-002-blueprint-families.md` — Craft-Varietät (`craft_variety`=1.0) heben, indem statt 2 Einzel-Blueprints (Axt/Messer) **Tag-Familien-Slots + 3 Werkzeug-Familien mit je 2–3 Varianten** existieren und Fehlschläge kategorisiertes Feedback geben.

### Mechanik
- **Tag-Familien-Layer:** `TAG_FAMILIES` (`SHARP_OR_HARD`, `SHARP_OR_RIGID`, `RIGID_OR_FIBER`) + `_slot_satisfied()` — Slot-Anforderungen können Familien-Namen sein, die mehrere Tags subsumieren. Werte sind EITHER Familie ODER Einzel-Tag.
- **3 Werkzeug-Familien (je eigene Tag-Kombination):**
  - Axt (CHOPPING): `axe`(FLINT) / `axe_bone`(BONE) / `axe_stone`(STONE)
  - Messer (CUTTING): `knife`(FLINT) / `knife_bone`(BONE) / `knife_stone`(STONE)
  - Speer (PIERCE): `spear` (Familie SHARP_OR_RIGID) / `spear_bound` (+RIGID_OR_FIBER)
  - Material-Determinismus: jede Variante verlangt ein anderes Material-Tag → je nach Fund ist die Route eindeutig (flint→Feuerstein-, bone→Knochen-, stone→Stein-Variante).
- **Funktionale Tags datengetrieben:** `tool_tags`-Feld in BlueprintData/ToolBlueprint (statt hartkoddierter `if bp.id ==`).
- **`_no_match_reason` verbessert:** wählt den Blueprint, dem der Spieler am nächsten ist (meiste erfüllte Slots), und nennt genau EIN fehlendes Merkmal. Familien-Slots werden auf einen Mitglieds-Tag aufgelöst. Nie generisches Null-Feedback.

### Daten/Content
- `items.json`: **+`bone`** (BONE+HARD, scharfe Knochen-Werkzeugkante), `flint_shard` + `FLINT`.
- `locations.json`: **`bone`-Node in hidden_cave** (Knochen als Werkstoffquelle).
- `blueprints.json`: 2 → **8 Blueprints** (3 Familien × je 2–3 Varianten).

### Fixes (durch SPEC-002-Inhalte exponiert)
- **Engine-Robustheit (Crash):** `_create_tool`-Verbrauch crashte (`ValueError: list.remove`) bei selektierten Stacks, die im Inventar zusammengeführt wurden oder doppelt referenziert sind — jetzt konsumiert nur, was wirklich im Inventar liegt. (Real erreichbar: Speer aus mehreren Festen / Doppel-Selektion im CLI.)
- **Archiv-Smoke-Test aktualisiert:** `_smoke_test.py` erwartete noch das alte Spiel (`3× Stab = Fehlschlag`, `"Nichts passiert."` in Meldung). Beides ist bewusst obsolet (3 Feste = Holzspeer seit SPEC-002; Null-Feedback ist verbannt). Assertions auf den neuen Zustand gehoben.

### Akzeptanz-Check
- **3 Werkzeug-Typen × je ≥2 Varianten craftbar** (Tests: `TestBlueprintFamilies`) ✓
- Fehlschlag mit bekanntem Ziel-Tag nennt konkreten Grund (`MISSING_TAG:` + Label), nie generisch ✓
- `python -m pytest`: **155 passed** (vorher 147) ✓
- `craft_variety` Median: **1.0 → 3.0** (p25 1→2, p75 2→4) inline gemessen; `content_reachable` 1.0 (13/13, bone erreichbar), `feedback_quality` 1.0 (unverändert).

### Backlog-Triage
- **NEU (Ideen):** Stack-Verschmelzung vs. Mehrfach-Slot-Inventar: gleichnamige Items verschmelzen im Inventar zu einem Stack → Items, die 2× dasselbe Material brauchen, sind nur über distinkte Materialien erreichbar (Speer = reeds+Ast statt 2×Ast). Kein Bug, eine echte Design-Spannung (Mengen-bewusstes Matching wäre der saubere Fix). → BACKLOG 🟡 Ideen.
- **SPEC-003 aussetzen:** aktuelle Scorecard zeigt `discovery_gap`=0.25 (Unterkante), `naive_p25`=0.5 — SPEC-003-Ziel (Gap-unter-0.2 / Schwanz schließen) ist bereits eingetreten; Umsetzung riskt Überführung. An Direktor delegiert (Plan-Neufassung So). NICHT blind implementiert.

## 2026-08-04 — [Dev] SPEC-001: Prozess-System aktiviert

### Task
`SPEC-001-process-system.md` — das seit dem Umbau tote Prozess-System (`data/processes.py`, `processes.json`) in die Engine eingebunden. Quellen-Problem: `reeds`, `raw_meat`, `cooked_meat` waren unerreichbar → `content_reachable`=0.667, und es gab fast keine erkennbaren Craft-Wege.

### Engine
- `GameEngine.execute_process(process_id)`: prüft Inputs (Mengen), Werkzeug-Tags, konsumiert Inputs, `_advance_time(duration, 2.0)`, erzeugt Outputs, trackt `known_processes`. Reasions: `SUCCESS`/`UNKNOWN_PROCESS`/`MISSING_INPUT:<id>`/`MISSING_TOOL:<tag>`. `required_tag_in_env` bewusst weich (SPEC-001: vorerst optional, Locations tragen noch keine Tags).
- `available_processes()` — Prozesse, deren Anforderungen aktuell erfüllt sind (für CLI).
- `_count_template`/`_consume_template`/`_item_name` — Helfer.
- **knife erhält jetzt `CUTTING`** (nur axe hatte `CHOPPING`) → `create_tinder` braucht ein CUTTING-Werkzeug, das damit aus einem frischen Start craftbar ist.
- `Player.known_processes` ergänzt (für `session_depth`, das es bereits ausliest).

### Daten
- `items.json`: **+3 Prozess-Output-Templates** `sharp_stone`/`tinder`/`fire_pit` (vorher lieferte `create_item` nur "Unbekannt"); `reeds` + `KINDLING` (Feuerbohrer-Werkzeug).
- `locations.json`: **`reeds`-Node in hidden_cave** (per Spec), **`raw_meat`-Node in forest_edge** (Jagd mit `PROJECTILE`, z.B. Kieselstein) → beide Items sammelbar.
- `processes.json`: **+`cook_meat`** (`raw_meat` → `cooked_meat`, env-Tag HEAT_SOURCE weich).

### CLI
- `main.py`: Action `[p]rocess` — listet `available_processes()`, Auswahl via Index.

### Constitution-Check
- Tag-Crafting als Kern unangetastet; Prozesse sind Transformationen mit Umgebungs-/Werkzeug-Kontext, kein Rezeptbuch.
- Neue Items (sharp_stone/tinder/fire_pit) sind erreichbare Prozess-Outputs, keine Content-Deko als Selbstzweck.
- **Metrik-Core unangetastet:** `tools/scorecard.py`/`METRICS`/Play-Job NICHT verändert. Siehe Backlog-Eintrag unten.

### Verifikation
- `python -m pytest` → **147 passed** (134 + 13 neue Prozess-Tests in `test_engine.py`; `test_loader.py` auf neue Datenstände aktualisiert).
- Scorecard rechnet: `content_reachable` **0.667 → 1.0** (12/12, inkl. raw_meat/cooked_meat/reeds), `session_depth` 24→26. Alle Metriken ohne Fehler.
- Akzeptanzkriterien: `make_sharp_stone` (2× pebble → sharp_stone) ✓, `create_tinder`/`start_fire` von frischem Start erreichbar ✓ (reeds sammelbar, knife=CUTTING, reeds=KINDLING), `cooked_meat` aus `raw_meat` ✓, `[p]rocess` im CLI ✓.

### Backlog / wartet auf Peter
- **`craft_variety` zählt Prozesse noch nicht.** Der naive Play-Bot ruft nur `execute_experiment`, nie `execute_process` — das neue System bleibt dadurch für diese Metrik unsichtbar. Die Spec verlangt, Prozesse als Craft-Typ zu zählen, aber das ist eine Umdefinition der Metrik (Constitution: braucht Peters Freigabe). NICHT gemacht. → BACKLOG.

---

## 2026-08-05 — [Play] Scorecard + Playtest (cron)

### Scorecard (vs 03.08.)
`content_reachable` 0.667→**1.0** (Ziel ≥0.8 erreicht, 12/12), `craft_variety` 0.5→1.0, `session_depth` 24→26, `actions_to_first_craft` 63→62, `feedback_quality` 1.0, `blueprint_reachability` 1.0, `skill_spread` 0.315→**0.259** (↓). `discovery_gap` 0.5→**0.25** — im Band, aber an der **unteren** Kante; naive_discovery_rate 0.5→0.75, **naive_p25 0.0→0.5**.

### Wichtigster Befund — Langeweile-Stelle (session_depth)
Die komplette Entdeckungsmenge ist **2 Blueprints + 4 Prozesse + ~12 Templates**. Eine geführte Session (TDD-Play) hat ALLES in ~40 Aktionen geleert (knife, axe, tinder, fire, cooked_meat); danach gibt es kein weiteres Ziel — `session_depth`=26 misst es, gefühlt ist es schärfer: das Discovery-Spiel ist nach Minuten fertig, übrig bleibt sinnloses Sammeln. Das ist die Stelle, an der nichts Interessantes mehr passiert.

### Zwei konträre Enden, eine Leerstelle
- **Guided:** entleert den Kuchen in ~40 Aktionen → zu wenig Inhalt.
- **Naive (seed 7, 11):** 0 Blueprints, nur `MISSING_TAG:SHARP`, Langeweile bei Aktion 13/24. **Beide Tools brauchen `HARD`/`SHARP` = nur `flint_shard`** (pebble ist STONE, nicht HARD); flint nur am mountain_peak → einzelner Ort wird Hard-Gate ohne Leitfaden.

### Bugs (→ BACKLOG 🔴)
- **B06 `log_oak`:** Node referenziert Template nicht in items.json → fällen mit frischer Axt gibt "Unbekannt".
- **B07 `clay_lump`:** braucht `SHOVEL` (existiert nirgends) + Template fehlt → doppelt tot.
`content_reachable`=1.0 ist gegen beide **blind** (zählt nur TEMPLATE_DB-Keys) → Metrik-Blindspot (🟡 Backlog, Peters Freigabe für Metrik-Änderung).

### SPEC-003-Konflikt (→ an Direktor)
`discovery_gap` untere Ecke + `naive_p25` 0.5 — genau die Wirkung, die SPEC-003 liefern sollte, ist ohne SPEC-003 eingetreten (durch SPEC-001/Content). Neuerliche Umsetzung von SPEC-003 droht die Gap **unter 0.2** (Überführung) zu drücken. Priorität/Schärfe von SPEC-003 vor Umsetzung neu prüfen. `craft_variety`-Prozess-Umdefinition weiterhin offen (Peters Freigabe).

---

## 2026-08-04 — [Research] SPEC-003: Partielle Match-Erkennung (discovery_gap)

### Metrik-Anker
Schwächste/stagnierende Metrik laut Scorecard 2026-08-03: **`discovery_gap` = 0.5**, an der oberen Kante des Bands (0.2–0.6) — nahe „unentdeckbar". Zerlegung: `blueprint_reachability`=1.0 (Orakel), `naive_discovery_rate`=0.5, aber **`naive_p25`=0.0** — die untere Hälfte der naiven Läufe findet in 150 Aktionen *gar keinen* Blueprint. Der Median verdeckt den Schwanz. SPEC-001/002 decken Vielfalt/Content/Feedback ab, aber keine Mechanik senkt die Lücke selbst.

### Spec
`specs/SPEC-003-partial-match-recognition.md`. Mechanik aus Don't Starve (Prototypen-Maschine) + Ancestors (neuronales Entdeckungssystem), adaptiert als **partielle Match-Erkennung**: Fehlschlag mit ≥2/3 Slots eines unbekannten Blueprints → Reason `NEAR_MISS:<bp_id>`, generischer Bestätigungstext („gehören zusammen, es fehlt noch etwas") **ohne** Rezept-/Tag-Leak. Einmalig via `Player.near_misses` (Experimentiergedächtnis, von der Constitution gedeckt). Konvergiert naive Spieler, schenkt aber nichts — wer die Materialien nicht selbst hat, bekommt keinen Hinweis.

### Constitution-Check
- Kein vorgegebenes Rezept — nur Bestätigung einer gehaltenen Teilmenge.
- Hinweis/Experimentiergedächtnis ausdrücklich erlaubt.
- CI: CLI, stdlib, keine neue Metrik, keine Abschwächung bestehender Metriken.

### Erwartete Wirkung
- `discovery_gap`: 0.5 → ~0.3–0.4 (Mitte des Bands; bleibt >0.2, weil der Hinweis erst nach eigenem Besitz von ≥2 passenden Tags feuert).
- `naive_discovery_rate` p25: 0.0 → >0.0 („findet nichts"-Schwanz geschlossen).
- Nebeneffekt `session_depth` steigend.

### Änderungen
- `specs/SPEC-003-*.md` (neu)
- `PLAN.md` — SPEC-003 als offener Task

---


### Autorisierung
**Peter autorisiert in dieser Session ausschließlich die drei in Abschnitt 1 des Auftrags wörtlich spezifizierten Änderungen an CONSTITUTION.md.** Alles darüber hinaus bleibt ihm vorbehalten. Vermerkt hier.

### CONSTITUTION.md — drei Änderungen, sonst nichts
- **Status:** `ENTWURF — wartet auf Freigabe` → **`Gültig — freigegeben von Peter am 2026-08-03`**.
- **Positiver Rahmen** (Ende Identität): *"Neue Mechaniken sind ausdrücklich erwünscht, solange sie das Entdecken vertiefen statt es abzukürzen. Das Spiel darf wachsen — in Systemen, nicht nur in Inhalten."*
- **"Keine festen Rezepte" präzisiert:** ersetzt durch *"Keine vorgegebenen Rezepte; Entdeckung durch Experimentieren. Dass der Spieler festhält, was er selbst entdeckt hat — Entdeckungsjournal, Hinweise, Experimentiergedächtnis — ist ausdrücklich erlaubt und kein Widerspruch dazu."*

Damit ist die Constitution final. Vier Agenten lesen sie jede Session; der positive Rahmen löst die Vorsicht, die reine Verbote erzeugt hatten.

### Research in zwei Modi aufgeteilt
- **research-metric** (Job-ID `c837d9d8dde1`, Di 10:00) — wie bisher: schwächste/stagnierende Metrik, gezielt Mechaniken, genau ein Spec.
- **research-explore** (neuer Job `ba3954705006`, Do 10:00) — **kein Metrik-Anker.** Freie Suche nach Mechaniken, die das Spiel als System vertiefen, auch solche, die keine bestehende Metrik bewegt. Output: Spec **plus Metrik-Vorschlag** als `metrics/proposed/<name>.md` (Definition, Berechnungsskizze, Richtung/Zielband, warum nicht trivial zu heben). Ohne Metrik ist der Spec unvollständig.
- Beide nach `cron/` exportiert, beide tragen die Constitution-Zeile.

### Probezeit mechanisch durchgesetzt
- `METRICS` unterstützt optionales `probation_until` (ISO-Datum). Neue Metriken setzt Dev auf +14 Tage.
- SCORECARD.md markiert solche Zeilen mit `(Probe bis TT.MM.)`.
- Direktor-Prompt: Metriken in Probezeit dürfen beobachtet, aber **nicht** als Plan-Ziel gesetzt werden.
- Dev-Prompt: Hinzufügen von Metriken ist erlaubt und braucht keine Freigabe — nur Entfernen/Umdefinieren.

### Altlast entfernt
- `qa/` (abgelöste QA-Rolle) nach `archive/qa-legacy/`. `_smoke_test.py:162` prüfte auf "Nichts passiert" — sicherte also das Gegenteil des gewollten Verhaltens ab (inzwischen false; 3 Sticks → "Es fehlt dir etwas Hartes.").
- Der wertvolle Fall (3 Items ohne gültige Kombination nennen das Merkmal) als echter pytest `test_three_same_items_no_blueprint` nach `tests/test_engine.py`.

### Backlog
- Lern-Signal als Idea eingetragen, ausdrücklich **nicht** als Vorgabe: misst, ob ein Spieler Feedback versteht (Trefferquote nach informativer Meldung) — im Gegensatz zu `feedback_quality`, das nur Reason↔Label-Konsistenz prüft und bei 1.0 steht. Option für den Explore-Job, kein Auftrag.

### Verifikation
- `python -m pytest` → **134 passed** (131 + 3 Probezeit-Tests, nach qa-Verschiebung erneut geprüft).
- Scorecard deterministisch, Werte identisch zur letzten Messung (63 / 1.0 / 0.5 / 0.315 / 1.0 / 0.667 / 24 / discovery_gap 0.5).
- `cron/OVERVIEW.md` auf 5 Jobs aktualisiert.

### Wartet auf Peter
- Nichts — Constitution ist freigegeben. Das System kann laufen.

---
## 2026-08-03 — [Fix] Spieler-Feedback ehrlich + discovery_gap eingeführt

### Freigabe
**Peter hat die Umdefinition von `feedback_quality` genehmigt.** Vermerkt hier, damit der Direktor nicht auf eine vermeintliche Regression reagiert.

### Warum
`feedback_quality` stand auf 1.0, obwohl der Spieler unverändert "Nichts passiert." las — die Engine kannte den Grund (`MISSING_TAG:SHARP`), behielt ihn aber für sich. Genau der Fall, den die Messungs-Klausel der Constitution für ungültig erklärt. Und es fehlte die wichtigste Größe: der Abstand zwischen Erreichbarem und tatsächlich Gefundenem.

### Engine (Meldungen aus Reason abgeleitet — Spielerlebnis, nicht Metrik)
- `TAG_LABELS` angelegt: vollständig für alle im Spiel vorkommenden Tags (SHARP→"etwas Scharfes", FIBER→"etwas Faseriges", RIGID→"etwas Festes", etc.).
- `_feedback_message(reason)` baut für jeden Code eine konkrete Meldung; verrät nie mehr als der Reason hergibt (kein Rezept-Leaking).
- **"Nichts passiert." ist als Meldung vollständig verschwunden.** Fehlschläge nennen jetzt das fehlende Label, "mindestens zwei Dinge", das kaputte Item, oder "die Kombination ergibt nichts".
- Kein verändertes Spielverhalten, keine Balance-Änderung.

### feedback_quality neu definiert (v2)
> Eine Aktion zählt als informativ, wenn die Meldung das Label enthält, das zum tatsächlich zurückgegebenen Reason-Code gehört.

Damit ist die Metrik nur zu heben, indem man dem Spieler die Wahrheit sagt — nicht durch String-Renaming oder interne Codierung. `_expected_fragment(reason)` ist der Konsistenz-Wächter.

**Ehrlicher Befund:** Der Wert bleibt bei 1.0 — **nicht** weil nichts passiert ist, sondern weil die Engine in genau dieser Session gelernt hat, die Labels auch wirklich auszugeben. Die Metrik misst jetzt die Spielersicht und ist verdient auf 1.0. Würde jemand das Label aus der Meldung nehmen (ohne den Code zu ändern), fällt sie sofort. Ein künftiger Rückgang ist also korrekt, kein Alarmsignal.

### discovery_gap (neu, Band-Metrik)
- `blueprint_reachability` (Orakel) = 1.0, `naive_discovery_rate` (150 Aktionen) = 0.5.
- **`discovery_gap` = 0.5.** Zielband **0.2–0.6**, keine Richtung. Unter 0.2 nimmt das Spiel an die Hand, über 0.6 ist es unentdeckbar.
- Aktuell an der oberen Bandgrenze — nahe daran, dass ein Spieler zu wenig findet. Wichtiges Signal für die zwei Specs.
- Begründung + Zielband stehen in SCORECARD.md.

### Metrik-Historie versioniert
- Jede Metrik hat ein `version`-Feld in der JSON-Ausgabe. `feedback_quality` = 2, alle anderen = 1.
- Beim Delta wird eine Metrik mit Versionswechsel übersprungen → `— (neu definiert)`, die anderen bleiben vergleichbar. **Kein globaler Schema-Bump.**

### Rückwärtsprüfung (Punkt 6)
Außer `feedback_quality` sind auch `skill_spread` (0.298→0.315) und `session_depth` (16→24) durch die Zählweisen- und Median-Umstellung gestiegen, ohne dass sich am Spielerlebnis etwas geändert hätte. **Das ist kein stiller Fortschritt zu feiern.** Task in PLAN.md angelegt: beim nächsten Play-Lauf prüfen, dass beide Werte echte Spielerfahrung abbilden, sonst Metrik-Version bumpen.

### Constitution
Messung-Sektion ergänzt: *"Neue Metriken müssen benennen, welche Schwäche sie erfassen, und zwei Wochen mitlaufen, bevor sie Plan-Ziele steuern dürfen."* Status bleibt Entwurf.

### Verifikation
- `python -m pytest` → **130 passed** (117 + 13 neue).
- Neue Tests: Reason↔Label-Konsistenz für jeden Code, Etikett-vollständig für alle Tags, "Nichts passiert." kommt im Code nicht mehr vor, `discovery_gap` 0–1 + Band-Rendering.
- Determinismus: 2 Läufe, identische `metrics`.
- Delta real geprüft: unveränderte Metriken zeigen Zahlen, `feedback_quality` zeigt `— (neu definiert)`, Band-Zeile `im Band`.

### Neue Baseline (2026-08-03)
| Metrik | v | Wert |
|--------|---|------|
| actions_to_first_craft | 1 | 63 |
| blueprint_reachability | 1 | 1.000 |
| craft_variety | 1 | 0.5 |
| skill_spread | 1 | 0.315 |
| feedback_quality | **2** | 1.0 |
| content_reachable | 1 | 0.667 |
| session_depth | 1 | 24 |
| **discovery_gap** | 1 | **0.5** (Band 0.2–0.6) |

`feedback_quality` v2 ist nicht mit v1 vergleichbar.

### Wartet auf Peter
- Constitution-Freigabe (aktualisierte Fassung).
- Bestätigung der feedback_quality-Umdefinition (bereits in der Session als erteilt angenommen).

---
## 2026-08-03 — [Fix] Scorecard repariert + gegen Selbstoptimierung gehärtet

### Warum
Das Fitness-Signal hatte einen toten Schaltkreis (Delta feuerte nie) und mehrere Metriken waren billiger zu faken als zu erfüllen. Da das System ab jetzt ohne Peter steuert, wäre beides fatal: ein Delta, das nie feuert, gibt keine Richtung; eine Metrik, die man per String-Änderung hebt, wird genau so gehoben werden.

### Engine (nur strukturierte Rückgabefelder, kein Spielverhaltens-Unterschied)
- `execute_experiment`/`_create_tool` geben jetzt `reason` (`SUCCESS`/`NO_MATCH`/`BROKEN_ITEM`/`MISSING_TAG:<T>`/`TOO_FEW_ITEMS`/`UNKNOWN`), `blueprint_id` und `result_template_id` zurück.
- `Item` hat `template_id` (für Neuheits-Messung per Identität statt Name). `create_item` und `_create_tool` setzen es.
- Alle Meldungen (`message`) bleiben exakt gleich → bestehende 93 Tests unverändert grün.

### Scorecard-Überarbeitung (tools/scorecard.py)
- **Delta-Logik gefixt:** Vorher las `_prev_value` `data.get(key)` (Werte liegen unter `metrics`) und nahm `files[-1]` — die gerade geschriebene heutige Datei → immer Baseline. Jetzt: `load_previous(today)` schließt heute aus, nimmt die jüngste ältere Datei mit gleichem Schema; `prev` wird als Parameter in `build_table` gereicht (kein Glob im Tabellenbau mehr).
- **Metriken auf Identitäten:**
  - `craft_variety` → zählt distinkte `blueprint_id` (nicht `message`-Strings).
  - `feedback_quality` → Reason-Codes statt String-Blacklist; zählt Code ≠ UNKNOWN/NO_MATCH-ohne-Detail.
  - `session_depth` → Neuheit über `template_id` + `known_blueprints` + Prozesse, nicht Item-Namen.
  - `content_reachable` → zusätzlich `reachable_count`/`defined_count`; Tabelle markiert Content-Reduktion als `⚠ Content entfernt` statt als Verbesserung.
- **Seed-Satz:** `SEEDS = 20`; jede laufbasierte Metrik über alle Seeds, Median als `value`, `p25`/`p75` in Details. Laufzeit 1,3 s → kein Seed-Reduktionsbedarf.
- **skill_spread:** datengetrieben (beste Location über alle erreichbaren), `_travel_or_fail` schlägt hart fehl statt still weiterzulaufen.
- **Schema:** `schema: 2` in JSON; andere Schemata werden beim Delta übersprungen. Alte Datei nach `scorecard/archive/`.

### Neue Baseline (2026-08-03, schema 2)
| Metrik | Wert | vs. 03.08. (v1) |
|--------|------|------------------|
| actions_to_first_craft | 63 (Median) | 43 (Einzelrun) |
| blueprint_reachability | 1.000 | 1.000 |
| craft_variety | 0.5 (Median) | 1 (String) |
| skill_spread | 0.315 | 0.298 |
| feedback_quality | 1.0 | 0.6 |
| content_reachable | 0.667 | 0.667 |
| session_depth | 24 | 16 |

**Nicht vergleichbar:** andere Zählweise (Median), andere Identität (blueprint_id/template_id statt Name/String), Reason-Codes. Werte der v1-Baseline sind obsolet.

**Ehrliche Befunde:**
- `feedback_quality` springt auf 1.0 — nicht weil das Feedback besser wurde, sondern weil die Engine fast jede Aktion strukturiert codiert. Die Metrik misst jetzt Code-Qualität, nicht Spieler-Erlebnis. Das ist der gewollte Trade-off (nicht fakebar); die Meldung `"Nichts passiert."` bleibt aber die Spieler-Wahrnehmung.
- `craft_variety` fällt von 1 auf 0.5 (Median) — der naive Spieler erreicht in 100 Aktionen oft gar keinen oder einen Craft-Typ. Ehrlicher als der aufgeblasene String-Wert.

### Constitution + Direktor
- Messung-Sektion ergänzt: `tools/scorecard.py`, `METRICS`, Play-Job unantastbar; Metriken nur ergänzbar, nicht entfernbar/abschwächbar ohne Peter. Metriken = Indikatoren, nicht Ziele.
- Nicht-Ziele korrigiert (tote Mikrotransaktionen/Multiplayer/Echtgeld raus) → realistische Drift-Richtungen: Content-Menge als Selbstzweck, Refactoring ohne Metrik-Bezug, GUI, Kampf als Kern.
- pydantic explizit als erlaubte Ausnahme genannt (loader.py nutzt es).
- Direktor-Prompt eingeschränkt: darf Cron-Jobs ändern, aber nicht Play/Messung.
- SPEC-002: Akzeptanzkriterium von "≥4 Crafts in 100 Aktionen" → Verhaltensziel "3 Werkzeugtypen mit je ≥2 Varianten".

### Verifikation
- `python -m pytest` → **117 passed** (93 bestehend + 24 neue in `tests/test_scorecard.py`).
- Determinismus: 2 Läufe, identische `metrics`.
- Delta real verifiziert (synthetische Vorwochendatei → Zahlen in Δ-Spalte), dann entfernt; frische Baseline bleibt `— (Baseline)`.

### Wartet auf Peter
- Constitution-Freigabe (aktualisierte Fassung).

---
## 2026-08-03 — [Umbau] Primal Process auf autonomen Betrieb umgestellt

### Kontext
Das System lief wie ein Scrum-Team ohne Product Owner: Der Plan (Tag 1) fror jede Erkenntnis ein, die einzigen Signale waren "Tests grün" und "Sprint gefüllt". Beides misst Prozess, nicht das Spiel. Umbau: Selbstversorgung + messbare Spiel-Fitness + selbstmodifizierender Prozess. **Kein Spiel-Code geändert.** Einzige neue ausführbare Datei: `tools/scorecard.py`.

### Was gebaut wurde
- **CONSTITUTION.md** — unantastbarer Kern (Identität, Nicht-Ziele, Constraints, Änderungsregel). STATUS: Entwurf, wartet auf Peter. **Entscheidung:** max. 25 Zeilen respektiert (22). Nur Peter ändert diese Datei.
- **Scorecard** — `tools/scorecard.py` (stdlib only, deterministischer Seed) + `SCORECARD.md`. 7 Metriken aus echten Playthroughs, Delta zur Vorwoche, JSON nach `scorecard/`. Baseline lief.
- **PLAN.md neugeschrieben** — alte Fassung nach `archive/PLAN-phases-2026-08.md`. Drei Sektionen (Zustand/Ziele/Tasks), keine Phasen/KWs. Milestones M0.4–M3.4 als Rohmaterial nach BACKLOG.md.
- **Research → Specs** — Format definiert; 2 Beispiel-Specs aus der schwächsten Metrik geschrieben (SPEC-001 Prozess-System, SPEC-002 Blueprint-Familien).
- **4 Cron-Jobs umgebaut** — Play (ersetzt QA), Research, Dev, Direktor (ersetzt Review). Details unten.

### Baseline-Scorecard (2026-08-03)
| Metrik | Wert | Befund |
|--------|------|--------|
| actions_to_first_craft | 43 | Erst-Craft in 43 Aktionen — okay |
| blueprint_reachability | 1.000 | beide Blueprints erreichbar |
| **craft_variety** | **1** | 🔴 nur 1 Craft-Typ in 100 Aktionen |
| skill_spread | 0.298 | Können bringt etwas |
| feedback_quality | 0.600 | 60% informative Rückmeldungen |
| content_reachable | 0.667 | 3 Items (raw_meat/cooked_meat/reeds) unerreichbar |
| **session_depth** | **16** | 🔴 Langeweile nach 16 Aktionen |

Schwächste Metrik: `craft_variety` (1) — eng gekoppelt an `session_depth` (16). Ursache: nur 2 Blueprints, Prozess-System nicht eingebunden, kaum erreichbare Items. Daraus die zwei Specs.

### Cron-Jobs (IDs beibehalten, anpassen statt neu)
| Rolle | Job-ID | Schedule | Änderung |
|-------|--------|----------|----------|
| Play | `9777fe714dfb` | Mo/Mi/Fr 09:00 | war QA (Sa 16:00). Spielt Runs, rechnet Scorecard, findet Langeweile-Stelle. |
| Research | `c837d9d8dde1` | Di+Do 10:00 | Thema aus den Zahlen (schwächste Metrik), genau 1 Spec. |
| Dev | `10c0e68f3673` | Mo–Sa 14:00 | Tasks aus PLAN.md, sonst oberster Spec; darf sich bedienen, kein Summon. |
| Direktor | `d8ed1b92bc80` | So 18:00 | war Review. Schreibt PLAN.md neu, darf Cron-Jobs selbst ändern. |

Aus allen Prompts entfernt: Sprint-Cap, "Leerlauf ist der Feind", Worst-Case-Füllung, Summon-Mechanik, KW-Bezüge, Verbot Plan-Struktur zu ändern, Lessons-Learned 01.–03.08. Jeder Prompt trägt jetzt: *"CONSTITUTION.md ist unantastbar."* Export nach `cron/` aktualisiert (play/research/dev/direktor + OVERVIEW).

### Selbstmodifikation abgesichert
- Snapshot-Branch `pre-autonomy-2026-08-03` gepusht, bleibt liegen.
- Jede Änderung an `~/.hermes/cron/jobs.json` wird nach `cron/` exportiert + committet.

### Verifikation
- `python -m pytest` → **93 passed** (unverändert grün gegenüber Session-Start).
- Scorecard-Baseline deterministisch, reproducable über `python tools/scorecard.py`.

### Wartet auf Peter
- **CONSTITUTION.md** Freigabe (STATUS: Entwurf). Wenn er sie ändert/absegnet, ist der Kern gesetzt.

---
## 2026-08-03 — [Dev] Sprint KW 32 abgearbeitet: 5 🔴 Bugs + R01

### Erledigt (alle 6 Sprint-Tasks)
- **TASK-B01** — FIBER-Quelle: `plant_fiber`-Node (Chance 0.4) in forest_edge ergänzt. Neue Session sammelt FIBER und kann Axt craften (End-to-End-Test).
- **TASK-B02** — pebble-Template in items.json angelegt (STONE/PROJECTILE, durability 0.2). `create_item("pebble")` liefert "Kieselstein" mit Tags statt "Unbekannt".
- **TASK-B03** — Perception-Gates gesenkt: flint_shard 1.5→1.0, berries 2.0→1.0, mushroom 2.0→1.0. Bei Start-perception=1.0 ohne Grind sammelbar.
- **TASK-B04** — `execute_experiment` blockt condition=0-Items mit klarem Feedback ("... ist zerbrochen ...").
- **TASK-B05** — tick_counter initial 36 (6 Uhr). Kein Nacht-Kälte-Penalty beim Start, normale Starttemp.
- **TASK-R01** — processes.py auf JSON: `processes.json` + `ProcessData`/`load_processes()` in loader.py; `get_all_processes()` baut ProcessDefs aus JSON. Keine hartkodierten ProcessDefs mehr. **M0.3 damit abgeschlossen → `[x]`.**

### Ergebnis
- **93/93 Tests grün** (83 bestehend + 10 neu), `python -m pytest` in 0.44s.
- Sprint KW 32 vollständig abgearbeitet — keine offenen Tasks. Review (So 09.08.) plant KW 33 (R02, F01/F02 gemäß PLAN-Notiz).

### Änderungen
- `data/items.json` — pebble-Template
- `data/locations.json` — plant_fiber-Node (forest_edge), Perception-Gates gesenkt
- `engine/core.py` — tick_counter=36, condition=0-Check beim Crafting
- `data/processes.json` (neu), `data/loader.py`, `data/processes.py` — JSON-Loader
- `tests/` — TestBugs (B01–B05) + TestLoadProcesses
- `PLAN.md`, `BACKLOG.md` — Status-Updates

---

## 2026-08-02 — [Review] Weekly Triage + Sprint-Bestätigung (KW 32)

**Kontext:** Der Triage vom 01.08. (`187199c`) hat den KW-32-Sprint bereits vollständig aufgesetzt (5 🔴 Bugs + R01). Der heutige Review liest denselben neuesten QA-Report (`qa/2026-08-01.md`) — das ist ein Prüf-/Bestätigungslauf: Sprint steht, Backlog ist triagiert, seit dem 01.08. ist kein neuer Input dazugekommen.

### Erreicht (KW 31)
- **TASK-M03** (JSON-Loader Refactor) abgeschlossen — 83/83 Tests grün, keine hartkodierten Dicts in items/blueprints/locations.
- **QA-Playtest #1** — Engine stabil (Smoke 30/30, Unit 83/83), aber 5 🔴 Bugs → strukturell unspielbar, dokumentiert in `qa/2026-08-01.md`.
- **Research:** 4/6 Phase-0-Spiele analysiert (URW, CDDA, Ancestors, Neo Scavenger).

### Sprint-Status (KW 32)
- 7 Tasks angesetzt, alle `[ ]`: **TASK-B01…B05** (jeder 🔴 Bug als eigener Task) + **TASK-R01** (processes-Loader).
- Frühester Abarbeitungsbeginn **Mo 03.08. 14:00** — Sprint ist startbereit.
- R02 (Tech-Debt), F01/F02 (Features) bewusst nach **KW 33** verschoben (Bug-first, keine Sprint-Überladung).

### Blockiert
- Nichts extern. Kein neuer Input seit Vortag; der KW-32-Sprint deckt alle offenen 🔴 Bugs ab. Kein Dev-Leerlauf zu erwarten.

### Prioritäten KW 32
1. **Alle 5 🔴 Bugs** (Crafting strukturell unspielbar fixen) — B01 → B05, je eigener Task.
2. **R01** — processes.py auf JSON-Loader (schliesst M0.3 ab).
3. R02/F01/F02 rollen nach KW 33.

### Triage (BACKLOG)
- **🔴 Bugs:** 5/5 im KW-32-Sprint (B01–B05). Keine neuen seit 01.08.
- **🟡 Ideas:** M0.4/M1.x-Kandidaten (Tag-Substitution, Material-Quelle→Eigenschaften, Multi-Faktor-Crafting, Death-as-Legacy) → KW 33; Phase-2/3-Ideen (Condition-Web, Body-Part, Skills, Discovery, Biom, Starting Scenarios) → später.
- **🔵 Tech Debt:** R01 → Sprint KW 32; R02 → KW 33.
- **⚪ Research Leads:** 7 offene M0.2-Kandidaten (> 2) → **keine neuen Recherchen** in diesem Zyklus nötig.
- **Keine Einträge zu archivieren** — jedes Backlog-Item trägt bereits ein Sprint-/Phase-Ziel.

### Entscheidungen
- **Kein Schnitt auf KW 33:** Heute ist der letzte Tag von KW 31, die unmittelbar anstehende Woche ist KW 32 (Mo 03.08.). Der bestehende KW-32-Sprint ist korrekt und unangetastet — Tasks werden nicht vorschnell gerollt.
- **M0.3 bleibt `[~]`** (processes.py steht aus), **M0.2 bleibt `[~]`** (2 Original + 5 Kandidaten offen). Keine Milestone-Marker zu setzen — nichts Neues abgeschlossen seit 01.08.
- **M0.4 (Save/Load)** bleibt nächster Feature-Kandidat nach den Bugs — bereits im Backlog/Plan referenziert.

---

## 2026-08-01 — [Meta] Review-Cap auf 6 Tasks korrigiert — danach als Zahl entfernt

**Kontext:** Sprint-Cap „max 4 Tasks" stammte aus dem alten Dev-Schedule (Mo/Mi/Fr = 3 Sessions + 1 Puffer). Dev läuft jetzt Mo–Sa = 6 Sessions. Weiter verschärft: Dev bündelt jetzt Minifixes → konsumiert mehrere Tasks pro Session.

**Finale Struktur (nach Iteration mit Peter):**
- **Kein fixes Tasks-Cap mehr.** Review füllt den Sprint mit allen offenen 🔴 Bugs + top-priorisierten Refactors/Features, so viele wie sinnvoll und klar definiert — Kriterium ist Qualität, nicht eine Zahl. Nicht abgearbeitete Tasks rollen in die Folgewoche.
- **Dev bündelt Minifixes** (mehrere kleine Tasks/Session), Refactors/Features einzeln. Kein 1-Task-pro-Session-Zwang mehr.
- **Review übernimmt offene Tasks** aus der bisherigen Sprint-Sektion in die neue KW (kein Verlust beim KW-Wechsel).
- Review-Prompt liest den `qa/`-Ordner als Pflicht-Input. Delivery auf `discord:#general` (konsistent zu Research/Dev/QA).
- „Geschätzt"-Zeilen aus dem Task-Format entfernt — der Review muss nicht mehr schätzen.

**Triage-Testlauf (`187199c`):** Flow funktioniert — QA-Report → 5 Bug-Tasks, PLAN.md aktualisiert, committed + gepusht.

---

## 2026-08-01 — [Review] Weekly Triage + Sprint-Planung (KW 32)

**Kontext:** KW 31 lief zu grossen Teilen leer (3× "Sprint leer") — Dev wartete auf Triage. Der QA-Playtest #1 (heute) liefert endlich konkrete Arbeit: 5 🔴 Bugs, Spiel faktisch unspielbar.

### Erreicht (KW 31)
- **TASK-M03 (JSON-Loader Refactor)** abgeschlossen — 83/83 Tests grün, keine hartkodierten Dicts mehr in items/blueprints/locations
- **Research:** 4/6 Referenzspiele analysiert (URW, CDDA, Ancestors, Neo Scavenger)
- **QA-Playtest #1:** Smoke 30/30, Unit 83/83 — Engine stabil, aber Spiel als Ganzes unspielbar (5 🔴 Bugs)

### Blockiert
- Nichts extern. Der Stau war prozessual: keine Sprint-Tasks → Dev-Leerlauf. Jetzt behoben durch QA-Bugs.
- **M0.3 bleibt offen:** `processes.py` noch hartkodiert (Tech Debt), daher Milestone-Marker `[~]` statt `[x]`.

### Prioritäten KW 32
1. **Alle 5 🔴 Bugs** (Crafting strukturell unspielbar) — Vorrang, je eigener Task
2. Restliche Tech-Debt-Refactors (M0.3 abschliessen: processes.py, _create_tool)
3. QA-Balance (Fehlschlag-Feedback, Energie-Regeneration)
4. Research: Don't Starve + Vintage Story (geplant Di 04.08) + 5 neue Kandidaten in M0.2

### Triage (BACKLOG)
- **🔴 Bugs:** 5/5 → Sprint KW 32 (je eigener Task, nicht gebündelt)
- **🟡 Ideas:** tag-Substitution, Material-Quelle→Eigenschaften, Multi-Faktor-Crafting, Death-as-Legacy → nächste Woche (M0.4/M1.x); Rest (Condition-Web, Body-Part, Skills, Discovery, Biom, Starting Scenarios) → später (Phase 2/3)
- **🔵 Tech Debt:** `create_dynamic_item`-Fix in TASK-M03 erledigt; `processes.py` + `_create_tool` → Sprint KW 32
- **⚪ Research Leads:** 5 neue Survival-/Primitive-Tech-Spiele ergänzt (M0.2-Pipeline)

### Entscheidungen
- M0.3 auf `[~]` gesetzt (in Arbeit) — TASK-M03 fertig, processes-Loader steht noch aus.
- M0.2 erweitert: von 6 auf 11 Spiele, da nur noch 2 offen waren.

---

## 2026-07-30 — [Research] Ancestors + Neo Scavenger

### Ancestors: The Humankind Odyssey — Erkenntnisse
1. **Neuronales Entdeckungssystem:** Fähigkeiten durch Handlungen entdeckt und „verstärkt" — kein Tech-Tree-Kauf. Verstärkte Neuronen werden durch Fortpflanzung vererbt. Das ist das Vorbild für PPPs Blueprint-Discovery.
2. **Fear/Dopamin-Pacing:** Unbekannte Biome lösen Angst aus, erfolgreiche Aktionen bauen Dopamin auf. Organisches Gating ohne künstliche Barrieren. Für PPP: Biom-Vertrautheit als Erkundungsmechanik.
3. **Sensorische Discovery-UI:** Keine Minimap, kein Kompass. Sinne (Hören, Riechen, Intelligenz-Scan) ersetzen das HUD. Objekte müssen identifiziert werden, bevor sie nutzbar sind.
4. **Generationen-Lineage:** Tod = Clan-Mitglied-Wechsel, nicht Game Over. Entdecktes Wissen überlebt den Tod. Für PPP: Death-as-Legacy statt Death-as-Failure.
5. **Evolutionäre Physiologie:** Biologische Evolution ändert Mechaniken (Bipedalismus → Hände frei → tragen). Physiologie als Mechanik-Gate.

### Neo Scavenger — Erkenntnisse
1. **Substitutions-Crafting:** Rezepte definieren Kategorien (SHARP, CONTAINER), nicht Item-IDs. Beweist dass PPPs Tag-System im Survival-Genre funktioniert. Unterschiedliche Materialien = unterschiedliche Qualität.
2. **Condition-Web:** Multi-Condition-Metabolismus (Hunger, Durst, Fatigue, Hypothermie, Krankheit, Schmerz) mit Kaskaden. Tod fast nie durch eine Condition — es ist die Kaskade. Vorlage für M2.4.
3. **Permadeath + Spieler-Progression:** Kein XP, kein Leveling. Fortschritt = Spieler-Wissen. Philosophischer Beweis für PPPs Discovery-Ansatz.
4. **Abilities & Flaws:** Permanente Start-Traits definieren den Run. Für PPP: Starting Scenarios als Replayability-Multiplikator.
5. **Detailliertes Wundensystem:** Wunden mit Lokalisation, Typ, Infektionsstatus. Zeitdruck durch Infektions-Timer. Erweitert URWs Body-Part-System um systemische Konsequenzen.

### Für PPP adaptierbar (Top 5, spielübergreifend)
1. **Tag-basierte Item-Substitution** (NS) → Blueprints mit Tag-Slots statt Item-IDs — das Kernversprechen von PPP, durch NS validiert
2. **Neuronales Discovery-System** (Anc) → Blueprints durch wiederholte Experimente entdecken, nicht kaufen/finden
3. **Condition-Web** (NS) → HP/Energy ersetzen durch vernetzte Conditions mit Kaskaden-Interaktionen
4. **Angst/Dopamin-Pacing** (Anc) → Biom-Vertrautheit als natürliche Erkundungsbremse
5. **Permadeath-als-Legacy** (NS+Anc) → Tod = Wissens-Reset? Nein: entdeckte Blueprints überleben

### Backlog-Einträge
- Siehe BACKLOG.md (Ideas)

### Änderungen
- `research/ancestors.md` — 5 Mechaniken + Top-3-Adaptionen
- `research/neo-scavenger.md` — 5 Mechaniken + Top-3-Adaptionen
- `research/INDEX.md` — Querverweise für beide Spiele aktualisiert (4/6 analysiert)

### Nächster Schritt
- **Di 04.08. 10:00** — Research: Don't Starve + Vintage Story (letzte Research-Session von Phase 0)

---

## 2026-08-01 — [QA] Weekly Playtest #1

**Status:** Erster QA-Durchlauf. 83/83 Unit Tests grün, Smoke-Test 30/30 bestanden. Engine selbst stabil — keine Crashes, alle Edge Cases sauber behandelt.

**Kritisches Ergebnis: Spiel ist faktisch unspielbar.** Kein Blueprint im normalen Spielverlauf craftbar. Fünf 🔴 Bugs gefunden:

1. **Kein FIBER-Item droppbar:** `plant_fiber` und `reeds` in items.json definiert, aber in keiner Location. Beide Blueprints brauchen FIBER — strukturell unmöglich.
2. **`pebble`-Template fehlt:** `mountain_peak`-Node referenziert `"pebble"`, nicht in items.json → Spieler sammelt nutzlose "Unbekannt"-Items.
3. **Perception-Gates blocken alles:** Start=1.0, flint_shard braucht 1.5, berries 2.0, mushroom 2.0. Kein Weg perception zu erhöhen.
4. **Condition=0-Exploit:** Kaputte Items craften → Ergebnis hat condition=1.0. Kein Condition-Check in `execute_experiment`.
5. **Nachtstart:** tick_counter=0 → hour=0 → night_mod=-10. Effektive Temperatur 5°C. Hypothermie fast sofort.

**Edge Cases:** 12/12 getestet, alle sauber behandelt (keine Crashes). Nur condition=0 ist ein Bug.

**Balance:** Energie-Drain aggressiv (10/gather, 22.5/travel, 30/craft). Gather fühlt sich grindig an (nur 1 Item-Typ droppbar). Feedback `"Nichts passiert."` absolut uninformatisch.

**Änderungen:**
- `qa/_smoke_test.py` — 30-Check Engine-Smoke-Test
- `qa/_scenario_test.py` — New-Player-Szenario + 10 Edge Cases
- `qa/2026-08-01.md` — QA-Report
- `BACKLOG.md` — 5 🔴 Bugs
- `JOURNAL.md` — dieser Eintrag

---

## 2026-08-01 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) weiterhin leer. TASK-M03 abgeschlossen. Dritter Leerlauf in Folge.

**Aktion:** Keine Implementierung. Review morgen (So 02.08. 18:00) muss zwingend neue Tasks liefern — nächste Dev-Session Mo 04.08.

**Notiz:** M0.4 (Save/Load-System), M1.1 (Tag-Hierarchien), und M1.2 (Item-Content ×5) sind nächste priorisierbare Kandidaten. Phase 0 hängt ohne neue Tasks.

---

## 2026-07-31 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) weiterhin leer. TASK-M03 abgeschlossen, keine neuen Tasks hinzugefügt. Zweiter Leerlauf in Folge.

**Aktion:** Keine Implementierung. Warte auf Review (So 02.08. 18:00).

**Notiz:** M0.4 (Save/Load-System) und M1.1 (Tag-Hierarchien) stehen als nächste Kandidaten bereit. Review sollte zügig neue Sprint-Tasks priorisieren, sonst läuft Dev bis KW 33 leer.

---

## 2026-07-30 — [Dev] Sprint leer

**Status:** Sprint Tasks (KW 31) vollständig abgearbeitet. TASK-M03 ist `[x]`, keine weiteren offenen Tasks.

**Aktion:** Keine Implementierung. Warte auf Review (So 02.08. 18:00) für Triage und nächste Sprint-Planung.

**Offene Milestones in PLAN.md:**
- M0.3 (Datenmodell refactorn) — `[ ]` in Milestones, aber TASK-M03 hat die Akzeptanzkriterien bereits erfüllt. Milestone-Marker vermutlich veraltet.
- M0.4 (Save/Load-System) — `[ ]`, nächster Kandidat für Sprint-Aufnahme.

---

## 2026-07-29 — [Dev] TASK-M03: JSON-Loader Refactor (Session 1/3)

### Erreicht
- **JSON-Daten erstellt:** `data/items.json`, `data/blueprints.json`, `data/locations.json` — alle 1:1 aus den alten hartkodierten Dicts extrahiert
- **Loader-Modul:** `data/loader.py` mit pydantic-Validierung (ItemTemplate, BlueprintData, LocationData, ResourceNodeData)
- **data/items.py refactored:** `TEMPLATE_DB` jetzt aus `load_items()` statt hartkodiert — `create_item()` nutzt pydantic-Model-Attributzugriff
- **data/blueprints.py refactored:** `get_all_blueprints()` aus `load_blueprints()`
- **data/locations.py refactored:** `get_all_locations()` aus `load_locations()` — ResourceNode/LocationDef-Dataclasses bleiben als API erhalten
- **Bugfix:** `engine/crafting.py:create_dynamic_item` — hardcoded `components["head"]`/`components["handle"]` entfernt. Dynamische Suche nach sharpness und Name-Building
- **Neue Tests:** `tests/test_loader.py` — 18 Tests (Load, Validation, Roundtrip): fehlende Datei, invalides JSON, fehlende Pflichtfelder, falsche Typen

### Ergebnis
- **83/83 Tests grün** (65 bestehend + 18 neu), `python -m pytest` in 0.39s
- Alle Items, Blueprints, Locations verhalten sich identisch zur alten Version
- Keine hartkodierten Dicts mehr in `data/items.py`, `data/blueprints.py`, `data/locations.py`

### Notizen
- `data/processes.py` hat noch hartkodierte ProcessDefs — nicht im Task-Scope, aber konsistent wäre ein `processes.json` → BACKLOG
- `engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — hat Fallback aber inkonsistent mit fix in crafting.py → BACKLOG
- pydantic 2.13.4 verfügbar, Validierung funktioniert sauber

### Nächster Schritt
- TASK-M03 ist vollständig (alle Akzeptanzkriterien erfüllt). Review entscheidet ob Session 2/3 nötig.

---

## 2026-07-28 — [Research] UnReal World + Cataclysm: Dark Days Ahead

### UnReal World — Erkenntnisse
1. **Body-Part-Schaden:** Jeder Körperteil eigener Zustand (Frostbite, Bruch, Wunde). Lokalisierte Konsequenzen statt globaler HP. Direkt relevant für PPP M2.4.
2. **Material-Herkunft:** Fell-Qualität hängt vom Tier ab (Bär > Fuchs). Emergente Vielfalt durch Quell-Tags — kein Template-Overhead.
3. **Skill → Qualität:** 28 Skills, verbessern sich durch Nutzung (auch bei Fehlschlag!), modulieren Output-Qualität. Hardcap 95%, Softcap 5%. Learning from failure als Kernmechanik.
4. **Jahreszeiten-Welt:** Klima bestimmt Ressourcen-Verfügbarkeit, Prozesse (Trocknen nur bei >5°C), Tierverhalten. Winter-Survival fundamental anders als Sommer.
5. **Kein Geld:** Reine Tausch-Ökonomie. Fortschritt durch Selbstversorgung, nicht durch Kauf. Passt zu PPPs Discovery-Philosophie.

### CDDA — Erkenntnisse
1. **Nested Requirements:** Crafting = Rohstoffe + Tools + Skill + Proficiencies + Rezeptwissen + Umwelt (Licht/Werkbank/Gesundheit). Das Multi-Faktor-Modell für PPP-Blueprints.
2. **Proficiency-System:** `prof_carving`, `prof_welding` etc. — Sub-Skills unter generellen Skills. Lernen durch Wiederholung, reduzieren Fehlschlag-Rate. Bindeglied zwischen "kann generell" und "kann genau das".
3. **Known-Blueprints:** Rezepte sind nicht automatisch bekannt — müssen durch Bücher/Experimente entdeckt werden. Für PPP: `known_blueprints: set` auf Player.
4. **Komponenten-Fahrzeuge:** Fahrzeuge aus Einzelteilen (Frame, Rad, Motor) statt als Ganzes. Gleiches Prinzip für Gebäude. Relevant für M2.2 Shelter-System.
5. **Farming mit Pflanzenphysiologie:** Wachstumsrate × Temperatur × Dünger × Skill = Yield. Design-Vorlage für Phase 4.

### Für PPP adaptierbar (Top 5)
1. **Body-Part-System** (URW) → M2.4 Gesundheit, ggf. schon in M1.1 Tags vorbereiten
2. **Material-Quelle → Eigenschaften** (URW) → Tags wie `BEAR_FUR`, `OAK_WOOD` als Qualitäts-Multiplikatoren
3. **Multi-Faktor-Crafting** (CDDA) → M1.3 Blueprint-Conditions (Licht, Werkbank, Körperzustand)
4. **Proficiencies** (CDDA) → Sub-Skills, die Fehlschlag-Rate bei spezifischen Aktionen modulieren
5. **Known-Blueprints** (CDDA) → Discovery-System: nur craften, was vorher entdeckt wurde

### Backlog-Einträge
- Siehe BACKLOG.md (Research Leads + Ideas)

---

### Änderungen
- `tests/`-Ordner mit `conftest.py`, `__init__.py` angelegt
- `test_components.py` — 20 Tests: Item, Inventory, ToolBlueprint, Player
- `test_crafting.py` — 11 Tests: Blueprint, try_combine (Permutation, Multi-Tag, Mismatch), create_dynamic_item
- `test_data.py` — 13 Tests: create_item für alle 8 Templates, Edge Cases, Tag-Isolation
- `test_engine.py` — 21 Tests: execute_experiment (Axt/Messer), Eat, Travel, Weather, Thermodynamik
- 65/65 Tests grün, `python -m pytest` läuft in 0.31s

### Notizen
- `create_dynamic_item` in `crafting.py` ist hardcoded auf `components["head"]` — crasht bei generischen Blueprints ohne "head"-Slot. Tests dokumentieren das Verhalten, Refactor in M0.3.
- `_update_weather` triggert auch bei tick_counter=0 (0 % 12 == 0), also initialer Wetter-Random schon beim Start.
- `_get_ambient_temp` berechnet bei tick_counter=0 Nacht (hour=0 < 6) → night_mod=-10, daher 5°C statt 15°C.

### Nächster Schritt
- M0.3 — Datenmodell refactorn (JSON-Loader). Jetzt mit Test-Safety-Net.

---

## 2026-07-26 — [Setup] Projektübernahme & Initialisierung

- Repo von GitHub geklont, analysiert (~400 Zeilen, 8 Items, 2 Blueprints, 3 Orte)
- Stärke: Tag-basiertes Emergent Crafting als Kernmechanik
- Schwächen: kein Save/Load, Content-arm, keine Gefahren, keine Persistenz
- Vision festgelegt: Primitive Technology Discovery Game (Steinzeit → Eisenzeit)
- 4-Phasen-Plan über ~12 Wochen erstellt
- 3 Cron-Jobs eingerichtet: Research (Di+Do), Dev (Mo+Mi+Fr), Review (So)
- Repo: ~/projects/primal-process/, Remote: Pappet/Project-Primal-Process

## 2026-07-26 — [Review] Weekly #1

### Erreicht
- Repo geklont, analysiert, 4-Phasen-Plan erstellt
- Projekt-Dokumentation: PLAN.md, ANALYSIS.md, JOURNAL.md, BACKLOG.md
- Cron-Job-Struktur definiert: 3 Jobs (Research Di+Do, Dev Mo+Mi+Fr, Review So)
- Claude-Review-Feedback eingearbeitet (Session-State, Tests M0.2b, Review-Guardrails)
- M0.1 abgeschlossen ✓

### Backlog-Triage
- Backlog ist leer — Projekt ist brandneu, keine Einträge
- Einträge bereinigt: 0 archived, 0 deleted

### Blockiert/Probleme
- Nichts blockiert. Projektstart verlief sauber.

### Entscheidungen
- M0.2b (pytest) vor M0.3 (Datenmodell-Refactor) priorisiert — Claude hatte recht, Refactor ohne Tests = gefährlich
- Research: 2 Spiele pro Session statt 3 — Task-Granularität beachten
- research/INDEX.md als leeres Template angelegt, erste Session Di 28.07.

### Nächste Woche
- **Mo 27.07.** Dev: M0.2b pytest-Grundgerüst + Smoke-Tests
- **Di 28.07.** Research: UnReal World + CDDA analysieren
- **Mi 29.07.** Dev: Nächster Task (M0.2b fortsetzen oder M0.3 beginnen)
- **Do 30.07.** Research: Ancestors + Neo Scavenger
- **Fr 31.07.** Dev: Nächster Task

### Notizen
- Phase 0 läuft bis KW 33 (Mitte August). Genug Puffer für 6 Spiele + Test-Setup + Refactor + Save/Load.
- Keine ❓ an Peter nötig — alles im Plan.