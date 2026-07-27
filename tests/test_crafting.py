"""Tests for engine.crafting — Blueprint matching and dynamic item creation."""
import pytest
from engine.crafting import Blueprint, try_combine, create_dynamic_item
from engine.components import Item


def _make_item(name, weight, tags, attrs=None):
    return Item(name=name, base_weight=weight, tags=tags, attributes=attrs or {})


class TestBlueprint:
    def test_create(self):
        bp = Blueprint(id_name="axe", result_name="Axt", slots={"head": "HARD", "handle": "RIGID"})
        assert bp.id == "axe"
        assert bp.result_name == "Axt"
        assert bp.slots == {"head": "HARD", "handle": "RIGID"}


class TestTryCombine:
    def test_exact_match_axe(self):
        """Axe blueprint: head=HARD, handle=RIGID, binding=FIBER."""
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        items = [
            _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.9}),
            _make_item("Ast", 0.5, {"RIGID": True}, {"durability": 0.8}),
            _make_item("Faser", 0.1, {"FIBER": True}, {"durability": 0.5}),
        ]
        result = try_combine(items, [bp])
        assert result is not None
        assert "Axt" in result.name

    def test_permutation_match(self):
        """Items in wrong order should still match via permutation."""
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        # Order: binding, handle, head — not matching slot order
        items = [
            _make_item("Faser", 0.1, {"FIBER": True}, {"durability": 0.5}),
            _make_item("Ast", 0.5, {"RIGID": True}, {"durability": 0.8}),
            _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.9}),
        ]
        result = try_combine(items, [bp])
        assert result is not None

    def test_item_with_multiple_tags(self):
        """An item with multiple tags should satisfy any matching slot."""
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        # Schilfrohr has both RIGID and FIBER — can fill handle or binding
        items = [
            _make_item("Stein", 1.0, {"HARD": True, "SHARP": True}, {"sharpness": 0.9}),
            _make_item("Schilfrohr", 0.1, {"RIGID": True, "FIBER": True}, {"durability": 0.1}),
            _make_item("Faser", 0.1, {"FIBER": True}, {"durability": 0.5}),
        ]
        result = try_combine(items, [bp])
        assert result is not None

    def test_no_match_missing_tag(self):
        bp = Blueprint("test", "Ergebnis", {"slot_a": "HARD", "slot_b": "FIBER"})
        items = [
            _make_item("Stein", 1.0, {"HARD": True}),
            _make_item("Ast", 0.5, {"RIGID": True}),  # No FIBER
        ]
        result = try_combine(items, [bp])
        assert result is None

    def test_no_match_wrong_count(self):
        bp = Blueprint("test", "Ergebnis", {"slot_a": "HARD", "slot_b": "RIGID", "slot_c": "FIBER"})
        items = [
            _make_item("Stein", 1.0, {"HARD": True}),
            _make_item("Ast", 0.5, {"RIGID": True}),
        ]
        result = try_combine(items, [bp])
        assert result is None

    def test_matches_first_valid_blueprint(self):
        """If multiple blueprints, first match wins."""
        bp1 = Blueprint("first", "Erstes", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        bp2 = Blueprint("second", "Zweites", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        items = [
            _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.9}),
            _make_item("Ast", 0.5, {"RIGID": True}, {"durability": 0.8}),
            _make_item("Faser", 0.1, {"FIBER": True}, {"durability": 0.5}),
        ]
        result = try_combine(items, [bp1, bp2])
        assert result is not None


class TestCreateDynamicItem:
    def test_durability_from_weakest(self):
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        components = {
            "head": _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.9, "durability": 0.4}),
            "handle": _make_item("Ast", 0.5, {"RIGID": True}, {"durability": 0.8}),
            "binding": _make_item("Faser", 0.1, {"FIBER": True}, {"durability": 0.5}),
        }
        result = create_dynamic_item(bp, components)
        # Weakest is head with durability 0.4
        assert result.get_attr("durability") == 0.4

    def test_name_contains_components(self):
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        components = {
            "head": _make_item("Feuerstein", 1.0, {"HARD": True}, {"sharpness": 0.9}),
            "handle": _make_item("Eichenast", 0.5, {"RIGID": True}, {"durability": 0.8}),
            "binding": _make_item("Pflanzenfaser", 0.1, {"FIBER": True}, {"durability": 0.5}),
        }
        result = create_dynamic_item(bp, components)
        assert "Feuerstein" in result.name
        assert "Eichenast" in result.name
        assert "Axt" in result.name

    def test_weight_sum(self):
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        components = {
            "head": _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.5}),
            "handle": _make_item("Ast", 0.5, {"RIGID": True}),
            "binding": _make_item("Faser", 0.1, {"FIBER": True}),
        }
        result = create_dynamic_item(bp, components)
        assert result.base_weight == 1.0 + 0.5 + 0.1

    def test_power_from_head_sharpness(self):
        bp = Blueprint("axe", "Axt", {"head": "HARD", "handle": "RIGID", "binding": "FIBER"})
        components = {
            "head": _make_item("Stein", 1.0, {"HARD": True}, {"sharpness": 0.7}),
            "handle": _make_item("Ast", 0.5, {"RIGID": True}),
            "binding": _make_item("Faser", 0.1, {"FIBER": True}),
        }
        result = create_dynamic_item(bp, components)
        assert result.tags["CHOPPING"] == 0.7
        assert result.get_attr("power") == 0.7