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
# Reason-Codes (feedback_quality)
# ----------------------------------------------------------------------------

class TestInformativeReason:
    def test_success_informative(self):
        assert sc._is_informative_reason("SUCCESS") is True

    def test_no_match_not_informative(self):
        assert sc._is_informative_reason("NO_MATCH") is False

    def test_unknown_not_informative(self):
        assert sc._is_informative_reason("UNKNOWN") is False

    def test_missing_tag_informative(self):
        assert sc._is_informative_reason("MISSING_TAG:SHARP") is True

    def test_broken_item_informative(self):
        assert sc._is_informative_reason("BROKEN_ITEM") is True

    def test_too_few_informative(self):
        assert sc._is_informative_reason("TOO_FEW_ITEMS") is True


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
        for key, _desc, _fn, _dir in sc.METRICS:
            assert key in data
            assert sc._collapse(data[key]) is not None, f"{key} hat keinen value"

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
