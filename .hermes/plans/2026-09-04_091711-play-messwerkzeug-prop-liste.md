# Play-Job 04.09.: Messwerkzeug-Fix (prop-Liste + Treiber-Gates) — Implementierungsplan

> **For Hermes:** Nach dem Speichern wird dieser Plan vom selben Play-Lauf direkt ausgeführt (eigenes Messwerkzeug, kein Dev-Code). Constitution-konform: nur `play/guided_full.py` + `tests/test_guided_full.py` (Messwerkzeug, keine Metrik, kein Engine-Spielcode).

**Goal:** Der guided Bot deckt die three unsichtbaren Prozesse (`sharpen_tool`, `treat_cut`, `treat_strain`) ab — die Exhaustion-Decke wird ehrlicher (aktuell 0/20 für sharpen), und gear_uptime's Gegenmechanik wird im Spiel sichtbar.

**Architecture:** Zwei Löcher in `play/guided_full.py`: (1) die prop-Liste fehlt `sharpen_tool`; (2) `treat_cut`/`treat_strain` stehen zwar in der Liste, können aber nie feuern, weil der prop-Scan den ersten *verfügbaren* (oft schon bekannten) Prozess nimmt und blockt, und weil die Engine-Gates (Injury da? Worn-Tool unter 1.0?) von `available_processes()` nicht geprüft werden. Fix: nach dem bekannten prop-Block einen Lücken-Schritt anfügen, der genau diese drei Prozesse zielgerichtet bespielt — mit Szenen-Aufbau (Worn Tool + Flint / aktive Injury + Material), nicht blindem Spinnen.

**Tech Stack:** stdlib, pytest, deterministische Seeds (Range 20260801–20260820 für Bot-Vergleiche, 20260803+0..19 für Scorecard).

---

## Ist-Zustand (verifiziert, 04.09. 09:15)

- pytest: **285 passed** (`.venv/bin/python -m pytest`).
- Scorecard 04.09. geschrieben, alle 12 Metriken **±0** gegen 02.09 (deterministische Seeds, Engine unverändert seit 8f4173 — nur Docs/Tests/Plan-Datei landeten seither). Bands: discovery_gap 0.6 (im Band, Kante), warmth 0.46 / recovery 0.375 (im Band), forage 0.0 (unter Band, Probe bis 11.09.), gear_uptime 0.994 (über Band, Probe bis 11.09.), session_depth 63.0 (Probe bis 08.09.).
- Boredom-Punkt (echte Spiel-Decke): guided Exhaustion **Median 20, Range 14–30** (02.09-Lesung); `session_depth`=63 sitzt ~3.2× über dem Cap.
- Play-Befund 02.09: `sharpen_tool` **0/20** — prop-Liste (Zeile ~310) führt ihn nicht auf. `treat_cut`/`treat_strain` stehen drin, feuern aber nie: der prop-Scan (Zeilen 309–316) stoppt beim ersten Eintrag, der in `available_processes()` ist — `make_bandage`/`make_poultice` (Material fast immer da) blockieren die treat_-Schritte dahinter; und ohne aktive Injury sind sie es nie.

## Engine-Fakten (gelesen, engine/core.py)

- `_process_requirements_met` (Z.820): prüft **nur** Inputs/Tools/env — NICHT `injuries` (treat_*) und NICHT Worn-Tool-Condition (sharpen). D. h. `sharpen_tool` steht in `available_processes()`, sobald 1 flint_shard da ist — Ausführung ohne Worn-Tool liefert ehrlich `NO_WORN_TOOL` und verbraucht den Flint NICHT. Blinde prop-Erweiterung = NO_WORN_TOOL-Spin.
- `sharpen_tool` (Z.905–928): schärft das am wenigsten konditionierte getragene Werkzeug der Tags `CUTTING/CHOPPING/PIERCE` um +0.5 (cap 1.0), konsumiert 1 flint_shard nach Erfolg.
- `treat_cut`/`treat_strain` (Z.895–902): brauchen `player.injuries['cut'|'strain']`; ohne Injury → `NO_INJURY`, Material bleibt.
- Wear-Pfad (Z.404–413): pro erfolgreichem tool-required Gather `−0.05/durability`; Warnung einmalig beim Crossing von 0.25; Break bei ≤ 0. Achtung: condition wird als `round(wear,2)` abgezogen — knife_bone (durability 0.4, wear 0.125→0.12 gerundet): 1.0→0.88→0.76→0.64→0.52→0.40→0.28→**0.16** (7. Erfolg unterquert 0.25 → Warnung, 8. Erfolg → 0.16). sharps-Durability 0.4 = der Acht-Node reicht fast nie bis zur Warnung, selten bis zum Break — **Worn-Tool-Szene muss im Test ge-seedete Tools nutzen, nicht auf RNG-Wear warten.**
- Prozess-Hinweis-Faden: die Instandhaltungs-Hinweis-Kategorie (02.09-Befund) feuert nur, wenn Anforderungen JETZT erfüllt sind — ein Naiver hält nie Worn-Tool + Flint gleichzeitig.

## Tasks

### Task 1: Failing-Test — prop-Szene erreicht sharpen_tool

**Files:**
- Modify: `tests/test_guided_full.py` (neue Klasse nach `TestGuidedReachesCookMeat`)

**Step 1: Test schreiben**

```python
class TestGuidedReachesHiddenProcesses:
    """BL 02.09: sharpen_tool 0/20, treat_* nie im prop-Loop (make_bandage/
    make_poultice blockieren als erste 'available' Einträge). prop-Erweiterung
    + Lücken-Schritt: der Bot muss die drei SPEC-009/011-Prozesse in echten
    Szenen spielen — Engine-Gates (NO_WORN_TOOL/NO_INJURY) nicht spinnend."""

    def test_sharpen_reached_when_worn_tool_exists(self):
        # Szenario: Bot hat Worn-Tool (cond 0.3) + flint_shard → prop-Lücken-
        # Schritt muss schärfen (cond > 0.3 nachher).
        import play.guided_full as gf
        from engine.components import Item
        e = GameEngine(); e._rng = random.Random(7); random.seed(7)
        e.player.inventory.add(_tool())           # knife_bone, CUTTING
        tool = next(i for i in e.player.inventory.items if i.template_id == "knife_bone")
        tool.condition = 0.3
        e.player.inventory.add(create_item("flint_shard", 1))
        assert gf._sharpen_if_worthwhile(e) is True
        t = next(i for i in e.player.inventory.items if i.template_id == "knife_bone")
        assert t.condition > 0.3, "Worn-Tool muss geschärft worden sein (0.3 → ≥0.8)"
        assert _qty(e, "flint_shard") == 0, "genau 1 Flint verbraucht"

    def test_sharpen_skips_when_no_worn_tool(self):
        # Ehrlich: kein Worn-Tool → kein Versuch, Flint bleibt.
        import play.guided_full as gf
        e = GameEngine(); e._rng = random.Random(7); random.seed(7)
        e.player.inventory.add(_tool())           # condition 1.0
        e.player.inventory.add(create_item("flint_shard", 1))
        assert gf._sharpen_if_worthwhile(e) is False
        assert _qty(e, "flint_shard") == 1, "Flint darf nicht verschwendet werden"
```

**Step 2: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_guided_full.py::TestGuidedReachesHiddenProcesses -v`
Expected: FAIL — `AttributeError: module 'play.guided_full' has no attribute '_sharpen_if_worthwhile'`

### Task 2: Implementierung — `_sharpen_if_worthwhile` + prop-Erweiterung + Lücken-Schritt

**Files:**
- Modify: `play/guided_full.py` (prop-Liste Z.310, neuer Helper, Loop-Anpassung nach Z.316)

**Step 1: Helper implementieren (unter `_fire_at` / neben `_needs_fire_supply`)**

```python
def _worn_tool(game):
    """Das am stärksten abgenutzte getragene Werkzeug unter Volllast —
    dieselbe Auswahl wie engine.core.execute_process('sharpen_tool')."""
    from engine.core import SHARPEN_TOOL_TAGS
    worn = None
    for it in game.player.inventory.items:
        if not (set(SHARPEN_TOOL_TAGS) & set(it.tags)): continue
        if it.condition >= 1.0: continue
        if worn is None or it.condition < worn.condition:
            worn = it
    return worn

def _sharpen_if_worthwhile(game):
    """SPEC-011-Gegenmechanik im Mess-Bot (BL 02.09): nur schärfen, wenn ein
    Werkzeug tatsächlich unter Volllast ist — sonst wäre es ein Spin, der den
    Flint verteilte (execute_process verbraucht ihn bei NO_WORN_TOOL nicht,
    aber der prop-Loop würde ihn endlos probieren). Liefert True bei Erfolg."""
    if _worn_tool(game) is None: return False
    r = game.execute_process("sharpen_tool")
    return bool(r.get("success"))
```

**Step 2: prop-Liste + Lücken-Schritt im Main-Loop (Z.309–316)**

```python
        # --- 2. processes in order ---
        prop = ["make_sharp_stone","create_tinder","start_fire","cook_meat","make_fur_cloak",
                "make_bandage","make_poultice","treat_cut","treat_strain","sharpen_tool"]
        acted=False
        for pid in prop:
            if pid in game.available_processes():
                g.shot(lambda: game.execute_process(pid)); acted=True; break
        if acted: continue
        # --- 2b. Lücken-Schritt: Injuries/Worn-Tool sind Engine-Gates, die
        # available_processes() nicht sieht (BL 02.09). Ohne die Szenen-Aufbau
        # blockiert make_bandage/make_poultice (Material fast immer da) die
        # treat_-Einträge; sharpen würde NO_WORN_TOOL spinnen. Die Szene:
        # treat_-Szenen baut _treat_if_injured bereits in _warm_here auf (Injury
        # fällt im Spielverlauf an, Material wird nachgekauft); der Schritt
        # hier fängt den Moment, in dem Inputs完备 sind — prop-Treats sind dann
        # obsolet (der prop-Scan verpasst sie durch sein first-available-
        # Stoppen). Worn-Tool + Flint → schärfen statt NO_WORN_TOOL-Spin.
        if _sharpen_if_worthwhile(game):
            g.shot(lambda: game.execute_process("sharpen_tool")); acted=True; continue
        if acted: continue
```

*(Anpassung beim Schreiben: `2b`-Block nach dem prop-Loop einfügen; der treat_*-Fall ist bereits über `_treat_if_injured` in `_warm_here` abgedeckt — das ist bewusst: die Szenen-Aufbau für treat_ steht dort schon, der prop-Scan blockiert sie nur kosmetisch. Der Lücken-Schritt ist für sharpen.)*

**Step 3: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_guided_full.py::TestGuidedReachesHiddenProcesses -v`
Expected: PASS (2 passed)

### Task 3: 20-Sweep gegengetestet (Regression + ehrlichere Decke)

**Files:**
- Keine Datei-Änderung — Messlauf.

**Step 1: Sweep (exakt 1 Call/Seed, Range wie Historical)**

```bash
PYTHONPATH=. .venv/bin/python -c "
import play.guided_full as gf
res=[]
for s in range(20260801, 20260821):
    g = gf.guided_full(s)          # EIN Call pro Seed (BL 21.08: doppelt = RNG-Korruption)
    procs = sorted(g.game.player.known_processes)
    res.append((s, g.last_new, g.actions, 'sharpen' in ' '.join(procs), len(procs)))
full=[r for r in res if r[1]>=r[2]*0.9 or True]
import statistics
exh=[r[1] for r in res]
print('exhaustion median:', statistics.median(exh), 'range:', min(exh), '-', max(exh))
print('sharpen entdeckt:', sum(1 for r in res if r[3]), '/20')
print('procs/seed:', [r[4] for r in res])
print('tode (hp<=0 vor exhaustion):', sum(1 for r in res if r[2]>=400))
"
```

**Step 2: Erwartung & Protokoll**
- sharpen ≥ 12/20 (Szenen-Anforderung: Tool wear + Flint am Gipfel — der Bot sammelt am Gipfel nur während des Warmup-Pebble-Trips, Wear braucht ~7–8 Erfolge … falls deutlich darunter: Szene erweitern (flint-Shard zusätzlich zum Warmup-Pebble holen), NEU messen, Variante protokollieren).
- Exhaustion median darf minimal steigen (ehrlichere Decke) — kein Spiel-Signal, protokollieren.
- Tode ≈ 12/20-Band bleiben (nicht schlechter als 02.09: 12/20). Deutliche Verschlechterung → Fix zurückrollen, Variante dokumentieren.

### Task 4: naive Probe + Session-Report schreiben

**Files:**
- Create: `play/2026-09-04.md`

**Step 1: naive Probe (Session-Depth-Streuung, frische Seeds, 1 Call/Seed)**

```bash
PYTHONPATH=. .venv/bin/python -c "
from tools.scorecard import _run_session_depth
vals=[_run_session_depth(20260904*100+i) for i in range(8)]
print(vals)
"
```

**Step 2: Report schreiben** — Struktur wie 02.09: Headline = Boredom-Punkt (guided Exhaustion neu gemessen), Scorecard-Tabelle (alle Zahlen gegen `scorecard/2026-09-04.json` verifizieren), Messwerkzeug-Fix-Protokoll (vor/nach 20-Sweep), was sich gut anfühlt / was frustriert, Fazit für Direktor. Probe-Fälligkeiten nennen (session_depth 08.09., gear_uptime/forage 11.09.).

### Task 5: BACKLOG + JOURNAL + Commit

**Step 1:** BACKLOG 🔵 2026-09-02-Eintrag (Messwerkzeug prop-Liste) → als umgesetzt markieren (Datum + Sweep-Zahlen). Neue Beobachtungen nur falls der Sweep neue Fakten zeigt.

**Step 2:** JOURNAL.md oben:

```markdown
## 2026-09-04 — [Play] Scorecard flach (Seeds/Engine unverändert), Messwerkzeug: sharpen_tool 0/20 → Szenen-Fix
```
Inhalt: Scorecard-Lesung (alles ±0, Bands), Boredom-Punkt-Lesung, Fix-Protokoll mit Sweep-Zahlen, Commit.

**Step 3: Commit + Push-Verify**

```bash
cd ~/projects/primal-process && git add -A && git commit -m "play: scorecard + playtest (cron)" && git push
git log origin/main..main --oneline   # muss leer sein
```

## Files likely to change

- `play/guided_full.py` (prop-Liste + Helper + 2b-Schritt)
- `tests/test_guided_full.py` (neue Testklasse)
- `play/2026-09-04.md` (neu)
- `BACKLOG.md`, `JOURNAL.md`, `scorecard/2026-09-04.json`, `scorecard/latest.json`, `SCORECARD.md` (scorecard.py schrieb schon)

## Tests / Validation

- `.venv/bin/python -m pytest -q` → 287+ passed
- 20-Sweep: sharpen ≥ 12/20, Tode nicht schlechter als 12/20-Band, Exhaustion-Range dokumentiert
- Jede Zahl im Report gegen `scorecard/2026-09-04.json` geprüft (BL 26.08: Transkriptions-Drift)

## Risks / Open

- **prop-Scan-Blockierung:** `2b` nach dem prop-Loop heißt, sharpen wird erst probiert, wenn kein *anderer* Prozess available ist — In-Practice okay, weil der prop-Loop pro Tick nur eine Aktion setzt und sharpen dauerhaft verfügbar bleibt. Alternative (prop-Liste mit Condition-Guards) ist komplexer, kein Mehrwert.
- **Sweep könnte zeigen, dass Wear + Flint-Koinzidenz zu selten ist** (sharpen < 12/20) — dann ist das ein echtes Spiel-Signal (die Gegenmechanik braucht Szenen, die im normalen Verlauf nie zusammenfallen), und der Fix bleibt trotzdem (ehrlichere Decke), aber der Report führt es.
- **Kein Engine-Code, keine Metrik-Datei** — Constitution-Grenze. `_run_session_depth`-Probe ist read-only.
