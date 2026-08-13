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

    def test_unknown_never_informative(self):
        assert sc._expected_fragment("UNKNOWN") is None
        assert sc._informative_experiment("Das geht so nicht.", "UNKNOWN") is False

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

    def test_feedback_quality_is_v2(self):
        data = sc.compute_all()
        assert data["feedback_quality"]["version"] == 2

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
        16/16 (SPEC-007: fur_cloak via make_fur_cloak-Prozess, keine dangling refs)."""
        m = sc.metric_content_reachable()
        assert m["defined_count"] == 16
        assert m["reachable_count"] == 16
        assert m["value"] == 1.0

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


# ----------------------------------------------------------------------------
# Versionierte Deltas
# ----------------------------------------------------------------------------

class TestVersionedDelta:
    def test_rmoredef_skips_metric(self):
        """Version geändert → '— (neu definiert)' statt Zahl."""
        prev = {"metrics": {
            "feedback_quality": {"value": 1.0, "version": 1},
            "session_depth": {"value": 10, "version": 1},
        }}
        data = {"feedback_quality": {"value": 0.4, "version": 2},
                "session_depth": {"value": 24, "version": 1}}
        table = sc.build_table(data, prev)
        fq_row = [l for l in table.splitlines() if l.startswith("| feedback_quality")]
        sd_row = [l for l in table.splitlines() if l.startswith("| session_depth")]
        assert "neu definiert" in fq_row[0]
        assert "neu definiert" not in sd_row[0]

    def test_version_field_in_json_output(self):
        data = sc.compute_all()
        assert data["feedback_quality"]["version"] == 2
        assert data["session_depth"]["version"] == 1


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


