# Cron-Dev Offene Tasks — Implementierungsplan (forage_pressure v2 → guided_full-Rückzug → SPEC-011 → gear_uptime)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Die drei offenen Tasks aus `PLAN.md` (Stand 27.08.) in Reihenfolge von oben nach unten umsetzen — forage_pressure v2 (Metrik, Freigabe 22.08. Pkt. 8), guided_full Kalt-Retreat (Play-Tooling, keine Freigabe nötig), SPEC-011 Werkzeugverschleiß sichtbar machen — plus die zu SPEC-011 gehörende Proof-Metric `gear_uptime` (Constitution erlaubt Ergänzen von Metriken; Probezeit +14 Tage).

**Architecture:** Drei unabhängige Work Packages (A–C) plus eine anschließende Metrik-Registrierung (D). A fasst nur `tools/scorecard.py` an (Zählregel + Registry, Engine unberührt). B fasst nur `play/guided_full.py` an (Messwerkzeug). C verdrahtet den bestehenden, stummen Attrition-Pfad in `engine/core.py:283-335` additiv (graduelle Wirkung, Warnung, MISSING_TOOL-Zeile) und ergänzt einen apply-only-Prozess. D registriert `gear_uptime` laut `metrics/proposed/gear_uptime.md`. Jede Package: TDD, eigener Commit, eigener JOURNAL-Eintrag, PLAN.md-Checkbox.

**Tech Stack:** Python 3 stdlib (+pydantic in data/loader erlaubt), pytest, keine neuen Abhängigkeiten.

---

## Kontext & verbindliche Regeln (für den Implementierer)

- **Repo:** `~/projects/primal-process/`. Suite-Status bei Planstellung: **245 Tests grün** (`python -m pytest`).
- **CONSTITUTION.md ist unantastbar.** Kernpunkt hier: Metriken dürfen ergänzt, nicht entfernt/umdefiniert/abgeschwächt werden; Umdefinitionen brauchen Peters Freigabe. `forage_pressure` v2 ist **freigegeben** (DECISIONS_Response_2026_08_21.md, Pkt. 8, 22.08.): „v2 misst *gefühlte* Knappheit … exakte Schwelle schlägt Dev/Direktor vor, ich gebe sie gegen. Probezeit 14 Tage, beobachtend." Das **Band (0.1, 0.5) wird NICHT geschoben**.
- **Commit pro Package** (nicht pro Mikro-Task): `cd ~/projects/primal-process && git add -A && git commit -m "dev: <task> (cron)" && git push`.
- **JOURNAL.md** pro Package: `## 2026-MM-DD — [Dev] <Titel>`. **BACKLOG.md** nur bei Befunden (Bugs/Ideen/Flags).
- **PLAN.md-Checkboxes** `[~]` beim Start, `[x]` mit Ergebnis-Zeile am Ende der Package (wie bestehende Einträge formatieren).
- **RNG-Strom-Regel (BACKLOG 20.08.):** Neue Mechanik, die RNG in bestehende Verben mischt, bekommt einen eigenen Strom — ODER ändert absichtlich das Outcome-Mapping bestehender Draws. Paket C macht letzteres (dokumentierte Stream-Klasse SPEC-009/SPEC-010): die vollständige `compute_all()`-Delta-Tabelle vor/nach ist **pflichtig** im JOURNAL. Paket A und B verschieben keinen Engine-RNG (A zählt nur um, B ist Messwerkzeug).
- **Erstlesungen = Re-Baselining, kein Fortschritt** (Peters Regel aus PLAN.md): neue/v2-Werte dokumentieren, nicht feiern, nicht aufs Band tunen.
- Suite muss nach **jedem** Commit grün sein: `cd ~/projects/primal-process && python -m pytest -q`.

### Constitution-Check je Package (vor Commit gegenprüfen)

| Package | Verfassungs-Berührung | Status |
|---|---|---|
| A forage_pressure v2 | Umdefinition einer Metrik | ✅ von Peter freigegeben 22.08. (Pkt. 8), Band unverändert, version→2, neue Probezeit |
| B guided_full Retreat | keines (Play-Messwerkzeug, keine Metrik) | ✅ keine Freigabe nötig (Peters „Sonstiges", 22.08.) |
| C SPEC-011 | additive Engine-Verdrahtung | ✅ kein neues Template, kein neuer Experiment-Reason (EMITTABLE_REASONS unberührt), kein Metrik-Kern-Eingriff |
| D gear_uptime | Metrik-Ergänzung | ✅ Constitution erlaubt Ergänzen; `probation_until` = +14 Tage; keine Plan-Ziele vor Probeende |

---

## Work Package A — forage_pressure v2 (gefühlte Knappheit)

**Objective:** Die Metrik zählt statt `stock < max_stock` nur noch Versuche, die an Erschöpfung **verweigert** werden oder **deutlich gemindert** sind. Band (0.1, 0.5) und Policy bleiben unverändert.

**Files:**
- Modify: `tools/scorecard.py:700-741` (`_run_forage_pressure`, `metric_forage_pressure`) und `tools/scorecard.py:930` (METRICS-Eintrag)
- Modify: `tests/test_scorecard.py:533-550` (TestForagePressure)
- Modify: `metrics/proposed/forage_pressure.md` (v2-Status notieren)
- Modify: `PLAN.md` (Checkbox), `JOURNAL.md`

### Task A1: Klassifikations-Helper TDD

**Step 1 — failing tests** in `tests/test_scorecard.py`, neue Klasse **unterhalb** von `TestForagePressure`:

```python
class TestForagePressureV2Classification:
    """forage_pressure v2 (Pkt. 8): verweigert ODER deutlich gemindert = Knappheit."""

    @staticmethod
    def _nodes(*specs):
        from types import SimpleNamespace
        return [SimpleNamespace(stock=s, max_stock=m, depleted=d) for s, m, d in specs]

    def test_denied_when_all_depleted(self):
        nodes = self._nodes((0, 5, True), (2, 5, True))
        assert sc._forage_scarcity_hit(nodes) is True

    def test_diminished_below_half(self):
        nodes = self._nodes((2, 5, False), (9, 10, False))
        assert sc._forage_scarcity_hit(nodes) is True   # 0.4 < 0.5 → deutlich gemindert

    def test_healthy_first_node_not_scarce(self):
        nodes = self._nodes((9, 10, False), (1, 10, False))
        assert sc._forage_scarcity_hit(nodes) is False  # Referenz = erster erntbarer Node (Policy wie v1)

    def test_exact_half_not_scarce(self):
        nodes = self._nodes((5, 10, False))
        assert sc._forage_scarcity_hit(nodes) is False  # "deutlich" = strikt unter 0.5
```

**Step 2 —** `python -m pytest tests/test_scorecard.py::TestForagePressureV2Classification -q` → FAIL (`AttributeError: _forage_scarcity_hit`).

**Step 3 — Implementierung** in `tools/scorecard.py`, Sektion „Metrik 9" (Zeile ~700) ersetzen:

```python
# ----------------------------------------------------------------------------
# Metrik 9 — forage_pressure v2 (gefühlte Knappheit) — SPEC-004 / Pkt. 8, Probezeit
# v1 zählte `stock < max_stock` → jede frisch geerntete Stelle galt als
# "Knappheit" (0.707, definitionsbedingt über Band). v2 (Peters Neudefinition,
# 22.08.): ein Versuch zählt, wenn er an Erschöpfung VERWEIGERT wird (nichts
# erntbar am Ort) oder DEUTLICH GEMINDERT ist (erster erntbarer Node unter
# halbem Vorrat → eff_chance < 50 % der Basis-Chance, gleiche Form wie der
# SPEC-004-Vorratsfaktor). Schwelle 0.5 = Dev-Vorschlag (Pkt. 8: "Schwelle
# schlägt Dev/Direktor vor, ich gebe sie gegen"). Band (0.1, 0.5) NICHT geschoben.
# ----------------------------------------------------------------------------
FORAGE_SCARCE_FRACTION = 0.5


def _forage_scarcity_hit(eligible_nodes) -> bool:
    """v2-Klassifikation eines Gather-Versuchs (siehe _run_forage_pressure)."""
    harvestable = [n for n in eligible_nodes if not (n.stock <= 0 or n.depleted)]
    if not harvestable:
        return True  # (a) verweigert: Erschöpfung, am Ort ist nichts zu holen
    ref = harvestable[0]
    return ref.stock / ref.max_stock < FORAGE_SCARCE_FRACTION  # (b) deutlich gemindert


def _run_forage_pressure(seed, actions=200):
    """v2: Anteil Gather-Versuche, die verweigert oder deutlich gemindert werden.

    Policy byte-identisch zu v1 (erster erntbarer Node, 20 %-Rotation, gleiche
    Breaks) — NUR die Zählregel ist neu. Kein neuer RNG-Konsum gegenüber v1.
    """
    random.seed(seed)
    rng = random.Random(seed)
    game = GameEngine()
    locs = list(game.locations.keys())
    n_attempts, n_scarce = 0, 0
    for _ in range(actions):
        if _drain_check(game):
            break
        eligible = [n for n in game.current_location.nodes
                    if game.player.stats["perception"] >= n.req_perception
                    and (not n.req_tool_tag
                         or game.player.inventory.find_item_by_tag(n.req_tool_tag))]
        if not eligible:
            break
        n_attempts += 1
        if _forage_scarcity_hit(eligible):
            n_scarce += 1
        game.gather()
        if rng.random() < 0.2:
            _travel_or_fail(game, locs[rng.randrange(len(locs))])
    return n_scarce / max(1, n_attempts)
```

(`metric_forage_pressure` bleibt unverändert.)

**Step 4 —** `python -m pytest tests/test_scorecard.py -q` → alle forage-Tests grün.

### Task A2: Registry-Eintrag v2

**Step 1 — failing test:** In `TestForagePressure.test_registered_with_band_and_probation` ersetzen:

```python
    def test_registered_with_band_and_probation(self):
        entry = next(m for m in sc.METRICS if m["key"] == "forage_pressure")
        assert entry["band"] == (0.1, 0.5)                # unverändert — Band wird NICHT geschoben (Pkt. 8)
        assert entry["direction"] is None
        assert entry["version"] == 2
        assert entry["probation_until"] == "2026-09-10"   # +14 Tage ab Umsetzung 27.08.
```

**Step 2 —** Run → FAIL (version noch 1, probation 2026-08-20).

**Step 3 —** `tools/scorecard.py:930` ersetzen:

```python
    {"key": "forage_pressure", "desc": "Anteil Sammel-Versuche, die an Erschöpfung verweigert oder deutlich gemindert werden (gefühlte Knappheit)", "fn": metric_forage_pressure, "direction": None, "version": 2, "band": (0.1, 0.5), "probation_until": "2026-09-10"},
```

> Wenn der implementierende Lauf an einem anderen Tag als dem 27.08. stattfindet: `probation_until` = Implementierungsdatum + 14 Tage (ISO), Testwert entsprechend.

**Step 4 —** `python -m pytest tests/test_scorecard.py -q` → grün (auch `test_table_shows_probation_label` bleibt bestehen: Zeile beginnt weiterhin mit `| forage_pressure (v2) (Probe bis …`).

### Task A3: Erstlesung + Doku + Commit

**Step 1 —** Erstlesung holen und gegen v1 (0.707) vergleichen:
`cd ~/projects/primal-process && python3 -c "import sys; sys.path.insert(0,'tools'); import scorecard as sc; m=sc.metric_forage_pressure(); print(m)"`
Erwartung: Wert **deutlich unter 0.707** (nur echte Verweigerungen/ deutliche Minderung zählen). Ob er im Band (0.1, 0.5) liegt, ist **beobachtend** — nicht tune.

**Step 2 —** `python3 tools/scorecard.py` → SCORECARD.md + scorecard/-JSON regenerieren. Delta-Spalte zeigt automatisch „— (neu definiert)" (Versions-Sprung). Prüfen: alle **anderen** Metrikwerte byte-identisch zur Vorwoche (A darf keine andere Metrik berühren — nur diese Zeile geändert).

**Step 3 —** `metrics/proposed/forage_pressure.md`: oben unter STATUS ergänzen: „v2 umgesetzt am 27.08. (Pkt. 8): verweigert ODER erster erntbarer Node stock/max < 0.5; Schwelle 0.5 = Dev-Vorschlag, Peters Gegen-Vorbehalt offen; Band (0.1, 0.5) unverändert; Erstlesung <WERT>."

**Step 4 —** `PLAN.md`: Checkbox `[x]` mit Ergebniszeile (Erstlesung + „Schwelle 0.5 als Dev-Vorschlag, Gegen-Vorbehalt bei Peter"). `JOURNAL.md`: Eintrag `## 2026-08-27 — [Dev] forage_pressure v2 — gefühlte Knappheit statt stock<max` mit Definition, Schwelle, Erstlesung, Re-Baseline-Hinweis.

**Step 5 — Commit:** `git add -A && git commit -m "dev: forage_pressure v2 — gefuehlte Knappheit, Band unveraendert (cron)" && git push`

---

## Work Package B — PLAY-TOOLING: guided_full Rückzug-Trigger (Kalt-Retreat)

**Objective:** Der Rückzug darf am kalten Ort (mountain_peak, exposure 1.0) nicht mehr durch „Feuer ist aktiv" blockiert werden, wenn der Körper trotzdem unter 35 °C fällt — ohne den strikt schlechteren „retreat egal ob Feuer"-Fix (3/20) zu wiederholen. Chirurgisch: body_temp-Gate **nur am kalten Ort**.

**Files:**
- Modify: `play/guided_full.py:18` (Konstante) und `:97-104` (`_warm_here`)
- Test: `tests/test_guided_full.py` (neue Klasse)
- Modify: `JOURNAL.md`, `BACKLOG.md` (🔍-Eintrag schließen), `PLAN.md`

### Task B0: Baseline-Sweep VOR dem Patch (Pflicht)

**Step 1 —** 20-Sweep-Baseline messen (gleiche Seeds wie `test_guided_full.py`, damit die Zahlen von 19.08./21.08. vergleichbar bleiben):

```bash
cd ~/projects/primal-process && python3 - <<'EOF'
import sys; sys.path.insert(0, '.')
from play.guided_full import guided_full
from data.blueprints import get_all_blueprints
all_ids = {bp.id for bp in get_all_blueprints()}
voll, hp8 = 0, None
for seed in range(20260801, 20260821):
    g = guided_full(seed)
    if all_ids <= g.game.player.known_blueprints:
        voll += 1
    if seed == 20260808:
        hp8 = round(g.game.player.hp, 1)
print(f"BASELINE: voll {voll}/20, seed 20260808 hp={hp8}")
EOF
```

**Step 2 —** Beide Zahlen ins JOURNAL notieren (Erwartung lt. BACKLOG 21.08: ~6/20, seed 20260808 kollabiert Richtung −70 HP).

### Task B1: Fix TDD

**Step 1 — failing tests** in `tests/test_guided_full.py` (Import ergänzen: `from play.guided_full import eat, guided_full, _warm_here`):

```python
class TestColdRetreat:
    """BL 21.08: Kalt-Retreat — aktives, aber ungenügendes Feuer blockiert den
    Rückzug am kalten Ort nicht mehr; warme Orte werden nie wegen body_temp
    allein verlassen (der 'egal ob Feuer'-Fix war strikt schlechter, 3/20)."""

    @staticmethod
    def _at(loc_id, fire_active, fire_fuel, body_temp):
        e = GameEngine()
        e.travel(loc_id)
        e.current_location.fire_active = fire_active
        e.current_location.fire_fuel = fire_fuel
        e.player.body_temp = body_temp
        return e

    def test_retreat_at_cold_site_despite_fire(self):
        # Der Bug: Feuer aktiv (fuel 10 > 0), aber STORM/Gipfel frisst die Wärme
        # → bisher kein Rückzug, ~3 HP/Aktion Verlust (seed 20260808: WP→−70).
        e = self._at("mountain_peak", True, 10, 34.0)
        _warm_here(e)
        assert e.current_location_id == "forest_edge"

    def test_stay_at_cold_site_when_fire_holds(self):
        e = self._at("mountain_peak", True, 10, 36.0)
        _warm_here(e)
        assert e.current_location_id == "mountain_peak"

    def test_stay_at_warm_site_despite_low_temp(self):
        # Regressions-Garde gegen den über-breiten Fix: am warmen Arbeits-Ort
        # (exposure 0.5) zählt body_temp allein NICHT als Rückzugsgrund.
        e = self._at("forest_edge", True, 10, 34.5)
        _warm_here(e)
        assert e.current_location_id == "forest_edge"

    def test_retreat_at_cold_site_without_fire(self):
        e = self._at("mountain_peak", False, 0, 34.0)
        _warm_here(e)
        assert e.current_location_id == "forest_edge"
```

**Step 2 —** `python -m pytest tests/test_guided_full.py::TestColdRetreat -q` → `test_retreat_at_cold_site_despite_fire` FAIL (bleibt auf mountain_peak), die anderen PASS.

**Step 3 — Implementierung.** In `play/guided_full.py` bei `WARM = "forest_edge"` (Zeile 18) ergänzen:

```python
COLD_EXPOSURE = 0.8         # kalter Ort (mountain_peak 1.0) — Schwellwert wie core.py-Strain-Gate
```

`_warm_here` (Zeilen 97-104) ersetzen:

```python
    # Rückzug: am KALTEN Ort (exposure >= COLD_EXPOSURE) zählt der Körper, nicht
    # die Feuer-Flagge — ein aktives, aber ungenügendes Feuer (STORM/Nacht am
    # Gipfel) blockiert den Rückzug nicht mehr (BL 21.08: Bot verblutete mit
    # ~3 HP/Aktion trotz Feuer). An warmen Orten weiterhin: nur ohne
    # funktionierendes Feuer zurückziehen — Work-Site nicht verlassen, solange
    # das Feuer hält (BL 21.08: "retreat egal ob Feuer" war strikt schlechter).
    loc = game.current_location
    fire_ok = loc.fire_active and loc.fire_fuel > 0
    cold_site = getattr(loc, "exposure", 0.0) >= COLD_EXPOSURE
    if game.player.body_temp < 35.0 and (not fire_ok or cold_site):
        _go(game, WARM)
        _fire_at(game)
        for _ in range(6):
            if game.player.body_temp >= 35.5: break
            game._advance_time(1, effort_multiplier=1.0)
```

**Step 4 —** `python -m pytest tests/test_guided_full.py -q` → grün (inkl. bestehendem cook_meat-Sweep-Test ≥14/20).

### Task B2: Gegenprobe über 20-Sweep (Pflicht laut Task)

**Step 1 —** Denselben Sweep wie B0 nach dem Patch laufen lassen.

**Step 2 — Akzeptanz:** `voll_after >= voll_before` und `hp(20260808)_after > hp(20260808)_before` (der Kollaps muss weg sein). Sollte der Sweep regredieren: Fix verwerfen, Variante `body_temp < 34.0` (strenger) am kalten Ort probieren, erneut gegenproben — **niemals** den breiten Fix nehmen. Endzahlen ins JOURNAL.

**Step 3 —** `BACKLOG.md`: 🔵-Eintrag 2026-08-21 (guided_full Rückzug-Trigger) mit Durchstreich-Markierung + „✅ erledigt in Dev-Session 2026-08-27 …" versehen (Format wie Zeile 110/111). `PLAN.md`-Checkbox `[x]`. JOURNAL-Eintrag mit Baseline/After-Zahlen.

**Step 4 — Commit:** `git add -A && git commit -m "dev: guided_full Kalt-Retreat-Trigger, 20-Sweep-Gegenprobe (cron)" && git push`

---

## Work Package C — SPEC-011: Werkzeugverschleiß sichtbar machen

**Objective:** Den bestehenden, stummen Attrition-Pfad (`engine/core.py:283-335`) verdrahten: graduelle Wirkung, einmalige Warnung beim Schwellendurchgang, node-gebundene MISSING_TOOL-Zeile, apply-only-Prozess `sharpen_tool`. Exakte Vorgabe: `specs/SPEC-011-werkzeugverschleiss-sichtbar-machen.md` (Abschnitte A–D, Akzeptanz 1–5).

**Files:**
- Modify: `engine/core.py` (Konstanten oben, `gather()` Zeilen 294-297 + 306-309 + 329-334, `_feedback_message` ~Zeile 142, `execute_process` Block ~Zeile 790-803)
- Modify: `data/processes.json` (ein Prozess)
- Test: `tests/test_wear.py` (neu)
- Modify: `JOURNAL.md` (Delta-Tabelle pflichtig), `BACKLOG.md` (nur falls gap > 0.65), `PLAN.md`

### Task C0: Vorher-Tabelle holen (Pflicht, RNG-Stream-Klasse)

**Step 1 —** Nach A+B, **vor** der ersten C-Änderung:

```bash
cd ~/projects/primal-process && python3 -c "import sys; sys.path.insert(0,'tools'); import scorecard as sc, json; print(json.dumps(sc.compute_all(), indent=1, ensure_ascii=False, sort_keys=True))" | tee /tmp/metrics_before_c.json
```

Diese Datei gehört **unverändert** in den JOURNAL-Eintrag (Tabelle vor/nach).

### Task C1: Graduelle Wirkung (Spec A) + Warnung (Spec B) TDD

**Step 1 — failing tests** — neue Datei `tests/test_wear.py`:

```python
"""Tests für SPEC-011 — Werkzeugverschleiß sichtbar machen."""
import random

from engine.core import GameEngine, WEAR_WARN_THRESHOLD
from engine.components import Item


def _axe(condition, durability=0.8):
    # durability 0.8 → wear = round(0.05/0.8, 2) = 0.06 pro Erfolgs-Tick
    axe = Item(name="Test-Axt", base_weight=1.0, tags={"CHOPPING": 1.0},
               attributes={"durability": durability})
    axe.condition = condition
    return axe


def _gather_n(game, n, seed=7):
    random.seed(seed)
    seen = []
    for _ in range(n):
        game.player.inventory.items.clear()   # Traglast darf das Experiment nicht kapppen
        seen.extend(game.gather())
    return seen


class TestGradualWear:
    def test_warn_fires_exactly_once_per_crossing(self):
        game = GameEngine()
        game.travel("forest_edge")
        game.player.inventory.add(_axe(0.30))   # eine 0.06-Erfolgsernte kreuzt 0.25
        logs = _gather_n(game, 30)
        warns = [l for l in logs if "stark abgenutzt" in l]
        assert len(warns) == 1, f"genau eine Warnung beim fallenden Durchgang erwartet: {warns}"

    def test_no_warn_above_threshold(self):
        game = GameEngine()
        game.travel("forest_edge")
        game.player.inventory.add(_axe(1.0, durability=100.0))  # wear rundet auf 0.0
        logs = _gather_n(game, 15)
        assert not [l for l in logs if "stark abgenutzt" in l]

    def test_gradual_effect_reduces_success(self):
        # Deterministisch (feste Seeds): cond 1.0 vs cond 0.25 → Faktor max(0.25, cond)
        def successes(cond):
            game = GameEngine()
            game.travel("forest_edge")
            game.player.inventory.add(_axe(cond, durability=100.0))
            logs = _gather_n(game, 40, seed=11)
            return sum(1 for l in logs if l.startswith("Gefunden:"))
        high, low = successes(1.0), successes(WEAR_WARN_THRESHOLD)
        assert low < high, f"cond 0.25 ({low}) muss weniger Erfolgsernten liefern als 1.0 ({high})"
        assert low <= 0.75 * high, f"Erwartet: deutliche Dämpfung, got {low} vs {high}"
```

> Hinweis für den Implementierer: Die Seeds sind Startwerte. Beim ersten Lauf die tatsächlichen Zahlen prüfen; wenn `low`/`high` dicht beieinander liegen, N (40) erhöhen oder Seed wechseln — einmal festgelegt ist der Test deterministisch. Das beobachtete Verhältnis als Kommentar dokumentieren.

**Step 2 —** `python -m pytest tests/test_wear.py -q` → FAIL (Warnung existiert nicht; cond hat keinen Effekt).

**Step 3 — Implementierung in `engine/core.py`.** Bei den Modul-Konstanten (nahe `INJURE_*`) ergänzen:

```python
# SPEC-011 — Werkzeugverschleiß sichtbar machen
WEAR_WARN_THRESHOLD = 0.25  # Warnung beim fallenden Durchgang
WEAR_MIN_FACTOR = 0.25      # minimale Wirksamkeit verschlissener Werkzeuge (gleiche Form wie SPEC-004-Vorratsfaktor)
SHARPEN_RESTORE = 0.5       # sharpen_tool: +0.5 condition, cap 1.0
SHARPEN_TOOL_TAGS = {"CUTTING", "CHOPPING", "PIERCE"}
```

In `gather()`, Effekt-Zeile (aktuell 306-309):

```python
            # Erfolgswahrscheinlichkeit skaliert mit dem Vorratsanteil:
            # voller Vorrat = node.chance, geleerter = 0. SPEC-011: ein
            # abgenutztes Werkzeug wirkt graduell — ein Muster, zwei Achsen.
            eff_chance = node.chance * (node.stock / node.max_stock)
            if node.req_tool_tag and used_tool is not None:
                eff_chance *= max(WEAR_MIN_FACTOR, used_tool.condition)
```

Wear-Block (aktuell 329-334):

```python
                    if used_tool:
                        wear = 0.05 / used_tool.get_attr("durability", 0.5)
                        cond_before = used_tool.condition
                        used_tool.condition = max(0, used_tool.condition - round(wear, 2))
                        if used_tool.condition <= 0:
                            self.player.inventory.items.remove(used_tool)
                            logs.append(f"!!! {used_tool.name} zerbrochen !!!")
                        elif cond_before >= WEAR_WARN_THRESHOLD > used_tool.condition:
                            # SPEC-011: einmalig pro fallendem Durchgang — kein
                            # Dauerspam; Schärfen über die Schwelle erlaubt die
                            # nächste Warnung wieder.
                            logs.append(f"!!! {used_tool.name} ist stark abgenutzt !!!")
```

**Step 4 —** `python -m pytest tests/test_wear.py -q` → grün.

### Task C2: Post-break-Feedback (Spec C) TDD

**Step 1 — failing tests** in `tests/test_wear.py`:

```python
class TestMissingToolFeedback:
    def test_missing_tool_line_when_ripe_tool_node(self):
        game = GameEngine()
        game.travel("forest_edge")            # oak-Node (CHOPPING), Vorrat voll
        logs = _gather_n(game, 3)
        assert any("Werkzeug" in l for l in logs), f"MISSING_TOOL-Zeile erwartet: {logs}"

    def test_no_missing_tool_line_without_tool_nodes(self):
        game = GameEngine()
        game.travel("mountain_peak")          # flint/pebble: kein req_tool_tag
        logs = _gather_n(game, 3)
        assert not any("Werkzeug" in l for l in logs)

    def test_no_line_when_node_depleted(self):
        game = GameEngine()
        game.travel("forest_edge")
        for n in game.current_location.nodes:   # oak künstlich leeren
            if n.req_tool_tag:
                n.stock, n.depleted = 0.0, True
        logs = _gather_n(game, 3)
        assert not any("Werkzeug" in l for l in logs)
```

**Step 2 —** Run → FAIL.

**Step 3 — Implementierung.** In `gather()` (aktuell 294-297):

```python
            used_tool = None
            if node.req_tool_tag:
                used_tool = self.player.inventory.find_item_by_tag(node.req_tool_tag)
                if not used_tool:
                    # SPEC-011: post-break Funkstille schließen. Node-gebunden:
                    # nur wenn der Node sonst erntbar wäre (perception ist oben
                    # geprüft, Vorrat vorhanden). Kein neuer Experiment-Reason —
                    # die Meldung lebt nur im gather-Logstream.
                    if node.stock > 0 and not node.depleted:
                        logs.append(_feedback_message("MISSING_TOOL"))
                    continue
```

In `_feedback_message` (vor dem UNKNOWN-Fallback, nach dem `MISSING_ENV`-Zweig):

```python
    if reason == "MISSING_TOOL":
        # SPEC-011: Werkzeugbedarf sichtbar machen (gather-Logstream). Generisch,
        # keine Tag-/Rezept-Nennung.
        return "Du brauchst ein Werkzeug dafür."
```

> Beachte: `execute_process` baut seine `MISSING_TOOL:<tag>`-Meldung inline („Es fehlt dir X als Werkzeug.") und bleibt unverändert; `MISSING_TOOL` steht bereits in `EMITTABLE_REASONS` (scorecard.py:420) — der Vollständigkeits-Test bleibt grün.

**Step 4 —** `python -m pytest tests/test_wear.py tests/test_engine.py -q` → grün.

### Task C3: sharpen_tool (Spec D) TDD

**Step 1 — failing tests** in `tests/test_wear.py`:

```python
from data.items import create_item


class TestSharpenTool:
    def _game_with(self, *items):
        game = GameEngine()
        for it in items:
            game.player.inventory.add(it)
        return game

    def test_success_consumes_shard_and_restores(self):
        axe = _axe(0.4)
        game = self._game_with(axe, create_item("flint_shard"))
        res = game.execute_process("sharpen_tool")
        assert res["success"] is True
        assert axe.condition == 0.9
        assert not any(i.template_id == "flint_shard" for i in game.player.inventory.items)

    def test_caps_at_one(self):
        axe = _axe(0.9)
        game = self._game_with(axe, create_item("flint_shard"))
        game.execute_process("sharpen_tool")
        assert axe.condition == 1.0

    def test_picks_most_worn_tool(self):
        axe, knife = _axe(0.4), _axe(0.6)
        game = self._game_with(axe, knife, create_item("flint_shard"))
        game.execute_process("sharpen_tool")
        assert axe.condition == 0.9 and knife.condition == 0.6

    def test_failure_consumes_nothing(self):
        axe = _axe(1.0)   # nichts verschlissen
        game = self._game_with(axe, create_item("flint_shard"))
        res = game.execute_process("sharpen_tool")
        assert res["success"] is False
        assert axe.condition == 1.0
        assert any(i.template_id == "flint_shard" for i in game.player.inventory.items)

    def test_non_tool_items_not_eligible(self):
        pebble = create_item("pebble")        # PROJECTILE/STONE — kein Schärf-Kandidat
        pebble.condition = 0.5
        game = self._game_with(pebble, create_item("flint_shard"))
        res = game.execute_process("sharpen_tool")
        assert res["success"] is False
        assert any(i.template_id == "flint_shard" for i in game.player.inventory.items)
```

**Step 2 —** Run → FAIL (Prozess unbekannt).

**Step 3 — Implementierung.** `data/processes.json`: ans Listenende anhängen:

```json
  {"id": "sharpen_tool", "name": "Werkzeug schärfen", "inputs": {"flint_shard": 1}, "tools": [], "outputs": {}, "duration_ticks": 1}
```

In `execute_process` den apply-only-Block **vor** der Input-Konsumierung ergänzen (direkt neben `treat_cut`/`treat_strain`, core.py ~794-803):

```python
        # SPEC-011: Werkzeug schärfen (apply-only, Muster wie die Behandlung).
        # Das am stärksten abgenutzte getragene Schneid-/Schlag-/Stich-Werkzeug
        # wird +0.5 geheilt (cap 1.0). Scheitert es — kein verschlissenes
        # Werkzeug getragen — wird NICHTS konsumiert. Kein neuer Reason-Code:
        # "MISSING_TOOL" existiert bereits; die Meldung ist generisch.
        if process_id == "sharpen_tool":
            worn = [it for it in self.player.inventory.items
                    if SHARPEN_TOOL_TAGS & set(it.tags) and it.condition < 1.0]
            if not worn:
                return {"success": False,
                        "message": "Nichts hier, das zu schärfen wäre.",
                        "reason": "MISSING_TOOL"}
            target = min(worn, key=lambda it: it.condition)
            target.condition = min(1.0, target.condition + SHARPEN_RESTORE)
```

(Danach konsumiert der Standardpfad den flint_shard, `_advance_time(1)`, `known_processes`-Discovery läuft wie bei jedem Prozess. Flint gewinnt damit die zweite Rolle Klinge-Quelle UND Schleifmaterial — Node-Ökonomie zahlt in die Wartungsschicht.)

**Step 4 —** `python -m pytest tests/test_wear.py -q` → grün. Auch prüfen: `python -m pytest tests/test_scorecard.py -q` (craft_variety-Bot kann sharpen_tool jetzt als neuen Prozess-Typ entdecken → Wert darf sich bewegen; das ist dokumentierter Seiteneffekt, Spec „erwartete Metrik-Wirkung").

### Task C4: Suite-Invarianten + Delta-Tabelle + Commit

**Step 1 — Invarianten-Tests** in `tests/test_wear.py` anhängen (langsamer Probe-Block, Stil wie `test_scorecard.py`):

```python
class TestSuiteInvariants:
    """SPEC-011 Akzeptanz 5 — Metrik-Kern unberührt (inline-probe)."""

    def test_feedback_quality_stays_1(self):
        import scorecard as sc
        assert sc.metric_feedback_quality()["value"] == 1.0

    def test_reachability_stays_1(self):
        import scorecard as sc
        assert abs(sc.metric_reachability()["value"] - 1.0) < 1e-9

    def test_content_reachable_stays_1(self):
        import scorecard as sc
        assert abs(sc.metric_content_reachable()["value"] - 1.0) < 1e-9
```

(Falls `metric_reachability`/`metric_content_reachable` andere Schlüssel als `"value"` führen: an die bestehenden Assertions in `test_scorecard.py` anlehnen — dort stehen die kanonischen Vergleiche.)

**Step 2 —** `python -m pytest -q` → **komplette Suite grün** (250+ Tests).

**Step 3 — Nachher-Tabelle + Pflicht-Dokumentation:**

```bash
cd ~/projects/primal-process && python3 -c "import sys; sys.path.insert(0,'tools'); import scorecard as sc, json; print(json.dumps(sc.compute_all(), indent=1, ensure_ascii=False, sort_keys=True))" | tee /tmp/metrics_after_c.json
diff /tmp/metrics_before_c.json /tmp/metrics_after_c.json || true
```

**JOURNAL-Pflicht:** vollständige Vor/Nach-Tabelle aller Metriken einstellen (RNG-Stream-Klasse SPEC-009/SPEC-010), mit Einordnung: Verschiebungen durch das geänderte Outcome-Mapping des Erfolgs-Wurfs sind erwartete Stream-Verschiebung, **kein** Tuning. Invarianten: feedback_quality 1.0, reachability 1.0, content_reachable 1.0. **Wenn `discovery_gap` > 0.65:** Direktor-Flag als BACKLOG-Eintrag (Kategorie 🟡/Direktor-Flag, wie 26.08.) **im selben Commit** — nicht still tunen, nicht kompensieren.

**Step 4 —** `PLAN.md`-Checkbox SPEC-011 `[x]` mit Ergebniszeile (Akzeptanz 1–5 je ✓ + Delta- Kurzfassung). JOURNAL-Eintrag `## 2026-08-27 — [Dev] SPEC-011 — Werkzeugverschleiß wird lesbar, wirkt graduell, ist heilbar`.

**Step 5 — Commit:** `git add -A && git commit -m "dev: SPEC-011 Werkzeugverschleiss sichtbar (Warnung/MISSING_TOOL/graduell/sharpen_tool) (cron)" && git push`

---

## Work Package D — gear_uptime registrieren (Proof-Metric zu SPEC-011)

**Objective:** Die in `metrics/proposed/gear_uptime.md` vollständig skizzierte Metrik laut Vorschlag umsetzen und registrieren (Constitution: Ergänzen erlaubt, `probation_until` +14 Tage). Erstlesung dokumentiert die (ehemalige) Unsichtbarkeit — beobachtend, kein Ziel.

**Files:**
- Modify: `tools/scorecard.py` (Runner + METRICS-Eintrag; Import um `WEAR_WARN_THRESHOLD` erweitern)
- Modify: `tests/test_scorecard.py` (Registrierungs-/Range-Tests)
- Modify: `JOURNAL.md`, `PLAN.md`

### Task D1: Runner + Registry

**Step 1 — failing test** in `tests/test_scorecard.py` (neue Klasse):

```python
class TestGearUptime:
    """gear_uptime (SPEC-011, Probezeit) — Band-Metrik + Registrierung."""

    def test_value_in_range(self):
        m = sc.metric_gear_uptime()
        assert m["value"] is None or 0 <= m["value"] <= 1
        assert "p25" in m and "p75" in m

    def test_registered_with_band_and_probation(self):
        entry = next(m for m in sc.METRICS if m["key"] == "gear_uptime")
        assert entry["band"] == (0.70, 0.95)
        assert entry["direction"] is None
        assert entry["version"] == 1
        assert entry["probation_until"] == "2026-09-10"   # +14 Tage ab Umsetzung
```

**Step 2 —** Run → FAIL. **Step 3 — Implementierung** in `tools/scorecard.py`, neue Sektion nach `recovery_stability`, plus Import-Zeile oben (`from engine.core import …, WEAR_WARN_THRESHOLD`):

```python
# ----------------------------------------------------------------------------
# Metrik 12 — gear_uptime (SPEC-011, Probezeit) — metrics/proposed/gear_uptime.md
# "Werkzeugbedarf = Stress, benutzbares Werkzeug >= Warnschwelle = Outcome."
# Erstlesung dokumentiert die Attrition-Sichtbarkeit nach SPEC-011 (beobachtend).
# ----------------------------------------------------------------------------
GEAR_UPTIME_HORIZON = 150
GEAR_ROTATION = ("forest_edge", "mountain_peak", "hidden_cave")


def _run_gear_uptime(seed):
    random.seed(seed)
    game = GameEngine()
    stress = uptime = 0
    for tick in range(GEAR_UPTIME_HORIZON):
        if tick and tick % 40 == 0:
            nxt = GEAR_ROTATION[(tick // 40) % len(GEAR_ROTATION)]
            if game.current_location_id != nxt:
                game.travel(nxt)
        game.gather()
        for node in game.current_location.nodes:
            if (node.req_tool_tag and node.stock > 0 and not node.depleted
                    and game.player.stats["perception"] >= node.req_perception):
                stress += 1
                tool = game.player.inventory.find_item_by_tag(node.req_tool_tag)
                if tool is not None and tool.condition >= WEAR_WARN_THRESHOLD:
                    uptime += 1
    return uptime / stress if stress else None


def metric_gear_uptime():
    return _aggregate(_run_gear_uptime)
```

METRICS-Liste ergänzen (nach `recovery_stability`):

```python
    {"key": "gear_uptime", "desc": "Anteil Werkzeug-Bedarfs-Ticks mit nutzbarem Werkzeug >= Warnschwelle (SPEC-011)", "fn": metric_gear_uptime, "direction": None, "version": 1, "band": (0.70, 0.95), "probation_until": "2026-09-10"},
```

**Step 4 —** `python -m pytest tests/test_scorecard.py -q` → grün. Dann komplette Suite: `python -m pytest -q`.

### Task D2: Erstlesung + Doku + Commit

**Step 1 —** `python3 tools/scorecard.py` regenerieren. Erstlesung im JOURNAL festhalten (Über-Band inkl. 1.0 = „Werkzeuge faktisch unsterblich im Erleben" wäre die ehrliche Vorher-Lücke; nach SPEC-011 erwarten wir Abfall Richtung Band — **alles beobachtend, kein Tuning**, Kein Plan-Ziel vor 2026-09-10). `PLAN.md`: neue Zeile `- [~] *(beobachtend)* **gear_uptime** (Probe bis 2026-09-10) — Erstlesung <WERT>. Kein Ziel.`

**Step 2 — Commit:** `git add -A && git commit -m "dev: gear_uptime metric registriert (Probezeit, SPEC-011) (cron)" && git push`

---

## Abschluss-Task (nach allen Packages)

1. `python -m pytest -q` — komplett grün, Anzahl notieren.
2. `PLAN.md`: alle drei Tasks `[x]`, `gear_uptime` als `[~]` beobachtend.
3. `JOURNAL.md`: vier Einträge (A–D) vorhanden; Delta-Tabellen (C) vollständig.
4. `git status` sauber, alles gepusht.
5. Keine erfundenen Extra-Tasks; wenn keine offene Arbeit mehr da ist: Session ohne weiteren Commit beenden.

## Files likely to change (Gesamt)

- `tools/scorecard.py` (A, D)
- `tests/test_scorecard.py` (A, D)
- `metrics/proposed/forage_pressure.md` (A)
- `play/guided_full.py` (B)
- `tests/test_guided_full.py` (B)
- `engine/core.py` (C)
- `data/processes.json` (C)
- `tests/test_wear.py` (C, neu)
- `PLAN.md`, `JOURNAL.md`, `BACKLOG.md` (Buchhaltung je Package)
- `SCORECARD.md` + `scorecard/*.json` (regeneriert durch A/C/D)

## Tests / Validierung

- Pro Task: gezielter pytest-Lauf (siehe Steps), erwartete FAIL→PASS-Folge dokumentiert.
- Pro Package: `python -m pytest -q` komplett grün.
- B: 20-Sweep Baseline/After (B0/B2) — Zahlen im JOURNAL, Akzeptanz = keine Regression + Seed-20260808-Kollaps weg.
- C: Vorher/Nachher-`compute_all()`-Delta-Tabelle (C0/C4) — Pflicht; Invarianten feedback_quality/reachability/content_reachable = 1.0; `discovery_gap` > 0.65 → Direktor-Flag im selben Commit.
- A/D: Erstlesungen dokumentiert (Re-Baseline, kein Feiern, kein Tuning).

## Risks, Tradeoffs, Open Questions

- **Schwelle 0.5 (A)** ist der Dev-Vorschlag, den sich Peter laut Pkt. 8 ausdrücklich vorbehalten hat („ich gebe sie gegen"). Deshalb prominent in JOURNAL + proposal-Datei vermerken — beim nächsten Play-/Direktor-Lauf bewusst zur Lesung vorlegen. Alternativen bei Veto: 0.4 oder 0.6 (eine Konstante, eine Zeile).
- **forage_pressure v2 Erstlesung** kann außerhalb des Bands liegen (Band bleibt unverändert — Pkt. 8). Kein Tuning; Band-Bewertung ist Sache des Direktors.
- **C verschiebt den deterministischen RNG-Mapping-Stream** aller scorecard-Bots (bekannte Klasse, SPEC-009/SPEC-010). Die Delta-Tabelle ist der disziplinarische Pflicht-Gegenpol; erwartet: craft_variety ↑ leicht (Schärfen als neues Aktionsmuster — von der Spec vorhergesagt), session_depth/gap können schwanken. `discovery_gap` > 0.65 → Flag, nicht fixen.
- **MISSING_TOOL-Zeile wiederholt sich pro Gather**, solange ein reifer Tool-Node ohne Werkzeug da steht — bewusst node-gebunden wie `DEPLETED` (Spec C). Falls der Play-Job es als Spam liest: Dämpfung als eigener Task, nicht ad hoc.
- **sharpen_tool-Failure-Reason** nutzt den bestehenden Code `MISSING_TOOL` (metrisch neutral — feedback_quality wertet nur Experimente aus, verifiziert an `_run_feedback_quality`). Kein neuer Reason-Code, EMITTABLE_REASONS unangetastet.
- **Test 3 (graduelle Wirkung) ist Seed-abhängig deterministisch, nicht analytisch** — Bounds beim ersten Lauf kalibrieren (N/Seed), dann einfrieren. Nicht lockern, um grün zu werden, sondern kalibrieren und das beobachtete Verhältnis kommentieren.
- **B-Sweep kann sich durch geänderte RNG-Konsumenten verschieben** (Retreat ändert Aktionsfolge) — Akzeptanz ist Nicht-Regression + Kollaps-Reparatur, kein Ziellwert.
- **Open:** Ob `gear_uptime`-Band (0.70–0.95) nach der Erstlesung hält, entscheidet der Direktor nach Probezeit (2026-09-10). Ob die MISSING_TOOL-Häufigkeit und der sharpen_tool-Text im Play-Job lesbar sind, zeigt die nächste Play-Session.
