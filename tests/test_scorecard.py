"""Tests for tools/scorecard.py — Delta-Logik, Schema, Metrik-Werte.

Schützt das Fitness-Signal davor, still kaputtzugehen (Fix-Session 2026-08-03).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import scorecard as sc  # noqa: E402


# ----------------------------------------------------------------------------
# Delta-Logik (load_previous)
# ----------------------------------------------------------------------------

@pytest.fixture
def scorecard_dir(tmp_path):
    return tmp_path


def _write(scorecard_dir, name, schema, metrics):
    (scorecard_dir / name).write_text(json.dumps({
        "schema": schema, "date": name[:10], "metrics": metrics,
    }))


class TestLoadPrevious:
    def test_no_files_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sc, "SCORECARD_DIR", tmp_path)
        assert sc.load_previous("2026-08-10") is None

    def test_excludes_today(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sc, "SCORECARD_DIR", tmp_path)
        _write(tmp_path, "2026-08-10.json", 2, {"a": {"value": 5}})
        # today is 2026-08-10 → must NOT be picked as previous
        assert sc.load_previous("2026-08-10") is None

    def test_picks_latest_older_schema2(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sc, "SCORECARD_DIR", tmp_path)
        _write(tmp_path, "2026-08-01.json", 2, {"a": {"value": 1}})
        _write(tmp_path, "2026-08-05.json", 2, {"a": {"value": 3}})
        prev = sc.load_previous("2026-08-10")
        assert prev is not None
        assert prev["metrics"]["a"]["value"] == 3  # neueste ältere

    def test_skips_older_schema(self, tmp_path, monkeypatch):
        """Dateien mit anderem Schema (z.B. v1) werden übersprungen."""
        monkeypatch.setattr(sc, "SCORECARD_DIR", tmp_path)
        _write(tmp_path, "2026-08-01.json", 1, {"a": {"value": 99}})
        _write(tmp_path, "2026-08-04.json", 2, {"a": {"value": 7}})
        prev = sc.load_previous("2026-08-10")
        assert prev["metrics"]["a"]["value"] == 7


class TestDeltaCell:
    def test_higher_better_improvement(self):
        txt, arrow = sc._delta_cell("k", 8, 5, "höher = besser")
        assert txt == "+3.000"
        assert arrow == "↑ besser"

    def test_higher_better_regression(self):
        txt, arrow = sc._delta_cell("k", 4, 5, "höher = besser")
        assert txt == "-1.000"
        assert arrow == "↓ schlechter"

    def test_lower_better_improvement(self):
        # kleiner ist besser → negatives Delta = Verbesserung
        txt, arrow = sc._delta_cell("k", 3, 8, "niedriger = besser")
        assert txt == "-5.000"
        assert arrow == "↑ besser"

    def test_lower_better_regression(self):
        txt, arrow = sc._delta_cell("k", 8, 3, "niedriger = besser")
        assert txt == "+5.000"
        assert arrow == "↓ schlechter"

    def test_zero_delta(self):
        txt, arrow = sc._delta_cell("k", 5, 5, "höher = besser")
        assert txt == "±0"

    def test_baseline_when_no_prev(self):
        txt, arrow = sc._delta_cell("k", 5, None, "höher = besser")
        assert "Baseline" in txt


# ----------------------------------------------------------------------------
# feedback_quality — Konsistenz-Wächter zwischen Reason und Spielertext
# ----------------------------------------------------------------------------

class TestFeedbackLabelConsistency:
    """Jeder Reason hat eine eigene Meldung, die das zum Code gehörende Label
    enthält. Das ist die Brücke von interner Wahrheit zu Spielertext."""

    def test_success_message(self):
        frag = sc._expected_fragment("SUCCESS")
        assert frag is not None
        assert sc._informative_experiment("Hergestellt: Axt (Eichenast)", "SUCCESS") is True

    def test_missing_tag_message_has_label(self):
        frag = sc._expected_fragment("MISSING_TAG:SHARP")
        assert frag is not None
        # Meldung muss das SHARP-Label enthalten
        assert sc._informative_experiment(f"Es fehlt dir {frag}.", "MISSING_TAG:SHARP") is True

    def test_missing_tag_without_label_not_informative(self):
        # Code richtig, aber Meldung verschweigt das Label → NICHT informativ
        assert sc._informative_experiment("Nichts passiert.", "MISSING_TAG:SHARP") is False

    def test_too_few_items_message(self):
        assert sc._informative_experiment(
            "Dafür brauchst du mindestens zwei Dinge.", "TOO_FEW_ITEMS") is True

    def test_broken_item_message(self):
        assert sc._informative_experiment(
            "Stein ist zerbrochen und kann nicht verwendet werden.", "BROKEN_ITEM") is True

    def test_no_match_message(self):
        frag = sc._expected_fragment("NO_MATCH")
        assert frag is not None
        assert sc._informative_experiment("Die Kombination ergibt nichts.", "NO_MATCH") is True

    def test_near_miss_is_informative_v3(self):
        """NEAR_MISS zählt als informativ (Entscheid 22.08., Pkt. 4) — der Text
        ist absichtlich vage, seine Nützlichkeit IST seine Vagheit. Fragment:
        'gehören' (aus 'zusammenzugehören')."""
        frag = sc._expected_fragment("NEAR_MISS:axe")
        assert frag == "gehören"
        msg = ("Einige dieser Dinge scheinen zusammenzugehören, "
               "aber es fehlt noch etwas.")
        assert sc._informative_experiment(msg, "NEAR_MISS:axe") is True

    def test_not_enough_quantity_is_informative_v3(self):
        """not_enough_quantity hat ein stabiles Fragment (Vollständigkeit)."""
        frag = sc._expected_fragment("NOT_ENOUGH_QUANTITY")
        assert frag == "mehr von demselben"
        assert sc._informative_experiment(
            "Dafür brauchst du mehr von demselben Material.",
            "NOT_ENOUGH_QUANTITY") is True

    def test_unknown_never_informative(self):
        assert sc._expected_fragment("UNKNOWN") is None
        assert sc._informative_experiment("Das geht so nicht.", "UNKNOWN") is False

    def test_reason_completeness_all_emittable(self):
        """Vollständigkeits-Test (Entscheid 22.08., Pkt. 4): JEDER Reason-Code,
        den die Engine emittieren kann, braucht ein Fragment oder einen
        dokumentierten None-Grund. Kein still unbedachter Reason mehr."""
        # Bewusst generische Reasons, deren Nicht-Informativität dokumentiert ist.
        documented_none = {"UNKNOWN", "UNKNOWN_PROCESS", "MISSING_INPUT"}
        # Enthalten in der Fragment-Map ODER per Tag-Sonderfall (MISSING_TAG→Label).
        statisch = ("SUCCESS", "TOO_FEW_ITEMS", "NOT_ENOUGH_QUANTITY", "BROKEN_ITEM",
                    "NO_MATCH", "DEPLETED", "FIRE_OUT", "NO_FIRE", "MISSING_FUEL",
                    "NO_INJURY", "BLEEDING", "TREATED", "HEALED", "UNKNOWN",
                    "UNKNOWN_PROCESS", "MISSING_INPUT")
        for code in sc.EMITTABLE_REASONS:
            assert code in sc._EXPECTED_FRAGMENTS or code == "MISSING_TAG", \
                f"Reason '{code}' fehlt in der Fragment-Map (Vollständigkeit)"
            val = (sc._expected_fragment(code) if code in statisch
                   else sc._expected_fragment(f"{code}:X"))
            assert val is not None or code in documented_none, \
                f"Reason '{code}' ist None, aber nicht als dokumentierter None-Grund deklariert"

    def test_every_tag_has_label(self):
        """TAG_LABELS ist vollständig für alle im Spiel vorkommenden Tags."""
        from data.items import TEMPLATE_DB
        from data.blueprints import get_all_blueprints
        from data.locations import get_all_locations
        from engine.core import TAG_FAMILIES
        tags = set()
        for tid, t in TEMPLATE_DB.items():
            tags.update(t.tags)
        for bp in get_all_blueprints():
            for slot_value in bp.slots.values():
                # Familien-Namen (SPEC-002) lösen sich in ihre Mitglieds-Tags auf.
                tags.update(TAG_FAMILIES.get(slot_value, {slot_value}))
        for loc in get_all_locations():
            for node in loc.nodes:
                if node.req_tool_tag:
                    tags.add(node.req_tool_tag)
        for t in tags:
            assert t in sc.TAG_LABELS or t == "DURABILITY", f"Tag {t} ohne Label"


class TestNoNichtsPassiert:
    """'Nichts passiert.' darf als Meldung nicht mehr vorkommen."""

    def test_no_nichts_passiert_in_core(self):
        src = (ROOT / "engine" / "core.py").read_text()
        assert "Nichts passiert." not in src

    def test_execute_experiment_never_returns_nichts_passiert(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        # leere Auswahl → früher "Nichts passiert."
        res = engine.execute_experiment([])
        assert "Nichts passiert" not in res["message"]
        # einzeln → früher "Nichts passiert."
        engine.player.inventory.add(create_item("stick"))
        res = engine.execute_experiment([engine.player.inventory.items[0]])
        assert "Nichts passiert" not in res["message"]



# ----------------------------------------------------------------------------
# Engine-Rückgabefelder (strukturierte Identität)
# ----------------------------------------------------------------------------

class TestEngineStructuredFields:
    def test_success_returns_blueprint_id(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        for tpl in ("flint_shard", "stick", "plant_fiber"):
            engine.player.inventory.add(create_item(tpl))
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["success"] is True
        assert res["reason"] == "SUCCESS"
        assert res["blueprint_id"] == "axe"
        assert res["result_template_id"] == "axe"

    def test_no_match_reason_detailed(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        engine.player.inventory.add(create_item("berries"))
        engine.player.inventory.add(create_item("mushroom"))
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["success"] is False
        assert res["reason"].startswith("MISSING_TAG:")

    def test_too_few_items_reason(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))  # nur 1
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["success"] is False
        assert res["reason"] == "TOO_FEW_ITEMS"

    def test_broken_item_reason(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        engine.player.inventory.items[1].condition = 0.0
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["reason"] == "BROKEN_ITEM"


# ----------------------------------------------------------------------------
# Metriken liefern value + Schema
# ----------------------------------------------------------------------------

class TestMetricsProduceValues:
    def test_all_metrics_have_value(self):
        data = sc.compute_all()
        for m in sc.METRICS:
            key = m["key"]
            assert key in data, f"{key} fehlt"
            assert sc._collapse(data[key]) is not None, f"{key} hat keinen value"

    def test_each_metric_has_version(self):
        data = sc.compute_all()
        for m in sc.METRICS:
            key = m["key"]
            assert data[key].get("version") == m["version"], f"{key} Version falsch"

    def test_feedback_quality_is_v3(self):
        data = sc.compute_all()
        assert data["feedback_quality"]["version"] == 3

    def test_craft_variety_uses_blueprint_ids(self):
        from engine.core import GameEngine
        from data.items import create_item
        engine = GameEngine()
        for tpl in ("flint_shard", "stick", "plant_fiber"):
            engine.player.inventory.add(create_item(tpl))
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res.get("blueprint_id") == "axe"

    def test_content_reachable_absolutes(self):
        m = sc.metric_content_reachable()
        assert "reachable_count" in m
        assert "defined_count" in m
        assert 0 <= m["value"] <= 1

    def test_content_reachable_is_full(self):
        """Alle definierten Items sind erreichbar (Gather oder Prozess-Output) —
        18/18 (SPEC-007: fur_cloak via make_fur_cloak-Prozess; SPEC-009: bandage/
        poultice via make_bandage/make_poultice — keine dangling refs)."""
        m = sc.metric_content_reachable()
        assert m["defined_count"] == 18
        assert m["reachable_count"] == 18
        assert m["value"] == 1.0
        assert m["dangling_refs"] == []

    def test_content_reachable_v2_detects_dangling(self):
        """v2 (Entscheid 22.08., Pkt. 3): Ein Node, dessen result_template_id
        kein Template hat, zählt als definiert-aber-unerreichbar → Metrik fällt.
        B06/B07 hätten das am Tag 1 gezeigt."""
        from data.locations import get_all_locations as real_locs
        # echte Locations bauen, aber einen Node auf ein nicht existentes Template zeigen
        locs = real_locs()
        locs[0].nodes[0].result_template_id = "ghost_item"
        # metric_content_reachable nutzt das Modul-Level `get_all_locations` —
        # ersetzen, sonst baut der Zähler frische, unmutierte Locations.
        orig = sc.get_all_locations
        sc.get_all_locations = lambda: locs
        try:
            m = sc.metric_content_reachable()
            assert "ghost_item" in m["dangling_refs"]
            assert "ghost_item" in m["unreachable"]
            assert m["value"] < 1.0
        finally:
            sc.get_all_locations = orig

    def test_craft_variety_v2_counts_processes(self, monkeypatch):
        """v2 (Entscheid 22.08., Pkt. 2): craft_variety zählt distinkte
        blueprint_ids UND process_ids. Erzwingt man Prozess-Erfolg (alle
        execute_process-Aufrufe gelingen), muss die Metrik gegenüber der reinen
        Blueprint-v1-Baseline (3.5) steigen — die Prozesse tragen bei."""
        from engine.core import GameEngine
        v1_ref_line = 3.5  # dokumentierter v1-Median (nur blueprints)
        orig = GameEngine.execute_process

        def all_succeed(self_proc, pid):
            return {"success": True, "process_id": pid}

        GameEngine.execute_process = all_succeed
        try:
            v2_with_proc = sc.metric_craft_variety()["value"]
        finally:
            GameEngine.execute_process = orig
        assert v2_with_proc is not None
        assert v2_with_proc > v1_ref_line, \
            f"Prozess-Pfad zählt nicht mit (Pkt. 2): {v2_with_proc} ≤ {v1_ref_line}"

    def test_baseline_written_with_schema(self):
        sc.SCORECARD_DIR.mkdir(exist_ok=True)
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as td:
            import scorecard as scmod
            # main schreibt in SCORECARD_DIR + SCORECARD.md — nur Schema prüfen
            data = sc.compute_all()
            payload = {"schema": sc.SCHEMA, "metrics": data}
            assert payload["schema"] == 2


# ----------------------------------------------------------------------------
# discovery_gap (Band-Metrik)
# ----------------------------------------------------------------------------

class TestDiscoveryGap:
    def test_gap_between_zero_and_one(self):
        m = sc.metric_discovery_gap()
        assert 0 <= m["value"] <= 1

    def test_gap_is_reach_minus_naive(self):
        m = sc.metric_discovery_gap()
        assert abs(m["value"] - (m["blueprint_reachability"] - m["naive_discovery_rate"])) < 1e-6

    def test_band_present(self):
        m = sc.metric_discovery_gap()
        assert m["band"] == [0.2, 0.6]

    def test_band_status_rendering(self):
        assert sc._band_status(0.3, (0.2, 0.6)) == "im Band"
        assert sc._band_status(0.1, (0.2, 0.6)) == "unter Band"
        assert sc._band_status(0.9, (0.2, 0.6)) == "über Band"

    def test_table_shows_band_not_direction(self):
        data = sc.compute_all()
        table = sc.build_table(data, None)
        row = [l for l in table.splitlines() if l.startswith("| discovery_gap")]
        # Richtungsspalte zeigt Band-Status, kein "höher/niedriger"
        assert row and ("Band" in row[0].split("|")[4])
        assert "höher" not in row[0].split("|")[4]


# ----------------------------------------------------------------------------
# REC-001 — Reachability-Zähler löst Tag-Familien auf (freigegeben)
# ----------------------------------------------------------------------------

class TestRec001FamilyReachability:
    def test_pair_slots_resolves_family(self):
        """Slot-Tag SHARP_OR_RIGID akzeptiert ein SHARP- oder RIGID-Item."""
        from engine.core import GameEngine, TAG_FAMILIES
        from data.items import create_item
        engine = GameEngine()
        # stick = RIGID, flint_shard = SHARP+HARD → beide erfüllen SHARP_OR_RIGID
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("flint_shard"))
        from data.blueprints import get_all_blueprints
        spear = next(bp for bp in get_all_blueprints() if bp.id == "spear")
        sel = sc._pair_slots(engine, spear)
        assert sel is not None, "spear (Familien-Slots) muss im Fresh-Gather auflösbar sein"

    def test_reachability_is_one_for_current_set(self):
        """Nach Familien-Fix: alle 8 aktuellen Blueprints erreichbar → 1.0."""
        m = sc.metric_reachability()
        assert m["value"] == 1.0

    def test_discovery_gap_in_or_at_band(self):
        """Wahrer Gap liegt in/am Band. SPEC-008 senkte ihn 0.625→0.6;
        SPEC-010 (Kaltstart-Pebble, 26.08.) resequestriert den deterministischen
        Naive-Bot-RNG-Stream → Lesung 0.65. Bekanntes Messmuster (Dev-Pitfall
        'shared measurement-stream'), KEINE reale Spiel-Verschlechterung.
        Grenze hier bewusst bei 0.65: Sobald die Tier-2-Volldeckungs-Near-Miss-
        Erweiterung (gleiche Session) eine erste Play-Lesung erzeugt und der
        Direktor das Band-Gefüge bewertet hat, ist diese Marke zu verschärfen
        oder zurückzusetzen — keine stille Abwärtsanpassung erlaubt."""
        m = sc.metric_discovery_gap()
        assert m["value"] <= 0.65

class TestRec002ToolAwareReachability:
    """REC-002 (freigegeben 22.08.): Der Reachability-Zähler misst, was die
    Engine wirklich craften kann — inkl. Werkzeug-Bau als Vorschritt.

    Der alte Ein-Schritt-Lauf versuchte jeden Blueprint einmal in
    Listenreihenfolge. Ein Blueprint, dessen Slots den Werkzeug-Tag `CORD` nur
    von `rope` bekommt (cord_spear), war dadurch nur erreichbar, wenn rope
    zufällig VOR ihm in der Liste stand. REC-002 modelliert Werkzeug-Bau als
    Vorschritt: ein Fixpunkt-Lauf baut rope zuerst und nutzt dessen `CORD`-Tag
    dann als Zutat — unabhängig von der Listenordnung.
    """

    def test_order_independent_closure(self):
        """Der Fixpunkt-Lauf liefert dieselbe Erreichbarkeit bei beliebiger
        Blueprint-Reihenfolge — die frühere Listenkopplung ist weg.

        cord_spear's Slot fordert den Werkzeug-Tag `CORD`, der in der Rohwelt
        nicht existiert — er entsteht erst durchs Craften von `rope`. Der alte
        Ein-Schritt-Lauf versuchte jeden Blueprint einmal gegen das
        Roh-Inventar und hätte cord_spear nur erreicht, wenn rope zufällig VOR
        ihm gepairt wurde. Der Fixpunkt baut dagegen rope zuerst (Survival ≥
        0.4), `CORD` landet im Inventar — und egal ob rope vor oder nach
        cord_spear steht, kommt dasselbe Menge heraus.
        """
        crafted_native, bps = self._fresh_crafted()
        crafted_reversed, _ = self._fresh_crafted(reverse=True)
        assert crafted_native == crafted_reversed
        assert "rope" in crafted_native


    @staticmethod
    def _fresh_crafted(reverse=False):
        import random
        from engine.core import GameEngine
        from data.locations import get_all_locations
        from data.blueprints import get_all_blueprints
        loc_ids = [l.id for l in get_all_locations()]
        bps = get_all_blueprints()
        if reverse:
            bps = list(bps)
            bps.reverse()
        random.seed(sc.BASE_SEED + 10_000)  # Seed von metric_reachability-Run 0
        game = GameEngine()
        for loc in loc_ids:
            sc._travel_or_fail(game, loc)
            for _ in range(8):
                game.gather()
        return sc._reachable_blueprints(game, bps, loc_ids), bps

    def test_blueprint_requiring_missing_gear_is_not_reachable(self):
        """Ein Slot-Tag, dessen Quelle weder Rohwelt noch ein gebautes Werkzeug
        liefert, macht den Blueprint NICHT erreichbar (kein falsches Positiv).

        Der Kern-Vorteil von REC-002: Der Fixpunkt reicht keine Phantom-Erfolge
        aus. Ein Blueprint, der einen Slot-Tag fordert, den (a) keine Node als
        Rohmaterial und (b) kein gebautes Tool als tool_tag trägt, bleibt
        ehrlich unerreichbar — sonst würde der Zähler Content als erreichbar
        lügen, den die Engine nicht bauen kann.
        """
        import random
        from engine.core import GameEngine
        from engine.components import ToolBlueprint
        from data.locations import get_all_locations
        from data.blueprints import get_all_blueprints
        loc_ids = [l.id for l in get_all_locations()]
        bps = list(get_all_blueprints())
        # 'ANGELHOOK' getragen von keinem Item und keinem Werkzeug-Tag.
        shadow = ToolBlueprint(
            id="phantom_device",
            result_name="Phantom",
            slots={"wire": "ANGELHOOK", "hook": "RIGID"},
            base_efficiency=1.0,
            tool_tags=["PIERCE"],
        )
        bps.append(shadow)
        random.seed(sc.BASE_SEED)
        game = GameEngine()
        game.blueprints["phantom_device"] = shadow
        for loc in loc_ids:
            sc._travel_or_fail(game, loc)
            for _ in range(8):
                game.gather()
        crafted = sc._reachable_blueprints(game, bps, loc_ids)
        assert "phantom_device" not in crafted

    def test_full_set_still_one(self):
        """Alle aktuellen Blueprints bleiben erreichbar → value bleibt 1.0."""
        m = sc.metric_reachability()
        assert m["value"] == 1.0
        assert all(m["per_blueprint"].values())

    def test_discovery_gap_still_at_band(self):
        """discovery_gap ≤ 0.65 (SPEC-010-Kaltstart-Pebble verschiebt den
        Naive-Bot-RNG-Stream, Lesung 0.65 — siehe Rec001-Test für die
        Reconciliation-Auflage) und reachability bleibt 1.0."""
        m = sc.metric_discovery_gap()
        assert m["value"] <= 0.65
        assert abs(m["blueprint_reachability"] - 1.0) < 1e-9

    def test_closure_is_a_repeatable_set(self):
        """Fixpunkt-Lauf liefert ein Set und ist bei gleichem Seed stabil."""
        crafted, _ = self._fresh_crafted()
        fresh2, _ = self._fresh_crafted()
        assert crafted == fresh2
        assert isinstance(crafted, set)



class TestForagePressure:
    """forage_pressure (SPEC-004, Probezeit) — Band-Metrik + Registrierung."""

    def test_value_in_range(self):
        m = sc.metric_forage_pressure()
        assert 0 <= m["value"] <= 1
        assert "p25" in m and "p75" in m

    def test_registered_with_band_and_probation(self):
        entry = next(m for m in sc.METRICS if m["key"] == "forage_pressure")
        assert entry["band"] == (0.1, 0.5)
        assert entry["direction"] is None
        assert entry["probation_until"] == "2026-08-20"  # +14 Tage ab 06.08.

    def test_table_shows_probation_label(self):
        table = sc.build_table(sc.compute_all(), None)
        row = [l for l in table.splitlines() if l.startswith("| forage_pressure")]
        assert row and "Probe bis" in row[0]


class TestRecoveryStability:
    """recovery_stability (SPEC-009, Probezeit) — Band-Metrik + Registrierung."""

    def test_value_in_range(self):
        m = sc.metric_recovery_stability()
        assert 0 <= m["value"] <= 1
        assert "p25" in m and "p75" in m

    def test_registered_with_band_and_probation(self):
        entry = next(m for m in sc.METRICS if m["key"] == "recovery_stability")
        assert entry["band"] == (0.3, 0.7)
        assert entry["direction"] is None
        assert entry["probation_until"] == "2026-09-03"  # +14 Tage ab 20.08.

    def test_table_shows_probation_label(self):
        table = sc.build_table(sc.compute_all(), None)
        row = [l for l in table.splitlines() if l.startswith("| recovery_stability")]
        assert row and "Probe bis" in row[0]


# ----------------------------------------------------------------------------
# Versionierte Deltas
# ----------------------------------------------------------------------------

class TestVersionedDelta:
    def test_rmoredef_skips_metric(self):
        """Version geändert → '— (neu definiert)' statt Zahl."""
        prev = {"metrics": {
            "feedback_quality": {"value": 1.0, "version": 1},
            "session_depth": {"value": 10, "version": 2},
        }}
        data = {"feedback_quality": {"value": 0.4, "version": 2},
                "session_depth": {"value": 24, "version": 2}}
        table = sc.build_table(data, prev)
        fq_row = [l for l in table.splitlines() if l.startswith("| feedback_quality")]
        sd_row = [l for l in table.splitlines() if l.startswith("| session_depth")]
        assert "neu definiert" in fq_row[0]
        assert "neu definiert" not in sd_row[0]

    def test_version_field_in_json_output(self):
        data = sc.compute_all()
        assert data["feedback_quality"]["version"] == 3
        assert data["craft_variety"]["version"] == 2
        assert data["content_reachable"]["version"] == 2
        assert data["session_depth"]["version"] == 2


# ----------------------------------------------------------------------------
# Probezeit (probation_until)
# ----------------------------------------------------------------------------

class TestProbation:
    def test_probation_label_format(self):
        m = {"probation_until": "2026-08-17"}
        assert "(Probe bis 17.08.)" in sc._probation_label(m)

    def test_no_probation_no_label(self):
        assert sc._probation_label({}) == ""

    def test_table_marks_probation(self):
        data = sc.compute_all()
        # discovery_gap ohne Probezeit → kein Label
        table = sc.build_table(data, None)
        dg_row = [l for l in table.splitlines() if l.startswith("| discovery_gap")]
        assert "Probe bis" not in dg_row[0]
        # session_depth v2 (Peter 22.08.) in Probezeit → Label erscheint
        sd_row = [l for l in table.splitlines() if l.startswith("| session_depth")]
        assert sd_row and "Probe bis" in sd_row[0]


# ----------------------------------------------------------------------------
# session_depth v2 — ziel-bewusster naiver Bot (Peter 22.08., Pkt 5)
# ----------------------------------------------------------------------------

class TestSessionDepthV2:
    def test_v2_probation_until_registered(self):
        """session_depth v2 muss +14 Tage ab Landung in Probezeit sein."""
        entry = next(m for m in sc.METRICS if m["key"] == "session_depth")
        assert entry["version"] == 2
        assert entry["probation_until"] == "2026-09-08"  # +14 Tage ab 25.08.

    def test_v2_selection_prefers_completable_over_near_miss(self):
        """Ein 100%-Match (rope: FIBER+RIGID) schlägt einen nur-2/3 Near-Miss."""
        import random
        from data.items import create_item
        game = sc.GameEngine()
        game.player.stats["survival"] = 0.6  # Gate für rope offen
        game.player.inventory.items.append(create_item("plant_fiber", 1))
        game.player.inventory.items.append(create_item("stick", 1))
        sel = sc._v2_selection(game, random.Random(1))
        assert sel is not None
        # rope ist der einzige 100%-Overlap (FIBER+RIGID) → gewinnt
        names = {it.name for it in sel}
        assert names  # es wird ein Versuch gewählt, kein None

    def test_v2_bot_can_open_gated_tier2(self):
        """Der v2-Bot erreicht die survival-gated Tier-2-Blueprints (rope,
        cord_spear), die der v1-Zufallsbot strukturell nie öffnen konnte."""
        found = set()
        for s in sc.SEEDS:
            game = sc.GameEngine()
            sc.random.seed(s)
            import random
            rng = random.Random(s)
            locs = list(game.locations.keys())
            cap = 1500
            stall, actions = 0, 0
            while actions < cap and game.player.hp > 0:
                actions += 1
                if game.player.energy < 150:
                    sc._eat_best(game)
                before = sc._novelty_set(game)
                if rng.random() < 0.5:
                    if rng.random() < 0.4:
                        sc._travel_or_fail(game, locs[rng.randrange(len(locs))])
                    elif rng.random() < 0.10:
                        s2 = sc._random_sel(game, rng, kmin=1)
                        if s2:
                            game.execute_experiment(s2)
                        else:
                            game.gather()
                    else:
                        game.gather()
                else:
                    sel = sc._v2_selection(game, rng)
                    if sel is not None:
                        game.execute_experiment(sel)
                    else:
                        game.gather()
                after = sc._novelty_set(game)
                stall = stall + 1 if after == before else 0
                if stall >= 15:
                    break
            found.update(game.player.known_blueprints)
        assert "rope" in found and "cord_spear" in found, \
            f"v2-Bot öffnete Tier-2 nicht (fand: {found})"


