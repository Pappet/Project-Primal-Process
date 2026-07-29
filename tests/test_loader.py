"""Tests for data/loader.py — JSON loading and validation."""
import pytest
from pathlib import Path

from data.loader import (
    load_items,
    load_blueprints,
    load_locations,
    ItemTemplate,
    ItemTemplatesDB,
    BlueprintData,
    ResourceNodeData,
    LocationData,
    _load_json,
)


class TestLoadItems:
    def test_loads_all_templates(self):
        items = load_items()
        assert isinstance(items, dict)
        assert "stick" in items
        assert "flint_shard" in items
        assert "berries" in items
        assert len(items) == 8

    def test_template_has_correct_fields(self):
        items = load_items()
        stick = items["stick"]
        assert stick.name == "Eichenast"
        assert stick.weight == 0.5
        assert stick.tags == {"RIGID": True}
        assert stick.attributes == {"durability": 0.8}

    def test_edible_tag_is_numeric(self):
        items = load_items()
        assert items["berries"].tags["EDIBLE"] == 50
        assert items["raw_meat"].tags["EDIBLE"] == 150

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError, match="nonexistent"):
            _load_json("nonexistent.json")


class TestLoadBlueprints:
    def test_loads_all_blueprints(self):
        bps = load_blueprints()
        assert len(bps) == 2
        ids = [bp.id for bp in bps]
        assert "axe" in ids
        assert "knife" in ids

    def test_blueprint_has_correct_slots(self):
        bps = load_blueprints()
        axe = next(bp for bp in bps if bp.id == "axe")
        assert axe.result_name == "Axt"
        assert axe.slots == {"head": "HARD", "handle": "RIGID", "binding": "FIBER"}
        assert axe.base_efficiency == 1.0


class TestLoadLocations:
    def test_loads_all_locations(self):
        locs = load_locations()
        assert len(locs) == 3
        loc_ids = [loc.id for loc in locs]
        assert "forest_edge" in loc_ids
        assert "mountain_peak" in loc_ids
        assert "hidden_cave" in loc_ids

    def test_location_has_nodes(self):
        locs = load_locations()
        forest = next(loc for loc in locs if loc.id == "forest_edge")
        assert forest.name == "Waldrand"
        assert forest.base_temp == 15.0
        assert forest.exposure == 0.5
        assert len(forest.nodes) == 3

    def test_resource_node_has_fields(self):
        locs = load_locations()
        forest = next(loc for loc in locs if loc.id == "forest_edge")
        stick_node = next(n for n in forest.nodes if n.result_template_id == "stick")
        assert stick_node.min_qty == 1
        assert stick_node.max_qty == 3
        assert stick_node.chance == 0.8
        assert stick_node.req_perception == 0.0
        assert stick_node.req_tool_tag is None

    def test_resource_node_with_tool_req(self):
        locs = load_locations()
        cave = next(loc for loc in locs if loc.id == "hidden_cave")
        clay_node = next(n for n in cave.nodes if n.result_template_id == "clay_lump")
        assert clay_node.req_tool_tag == "SHOVEL"


class TestValidationErrors:
    def test_invalid_json_raises(self):
        """A file with invalid JSON content should raise ValueError."""
        data_dir = Path(__file__).parent.parent / "data"
        tmp_path = data_dir / "_test_invalid.json"
        tmp_path.write_text("{invalid json")
        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                _load_json("_test_invalid.json")
        finally:
            tmp_path.unlink()

    def test_item_missing_required_field(self):
        """Items without 'name' should raise validation error."""
        with pytest.raises(ValueError):
            ItemTemplate.model_validate({"weight": 0.5, "tags": {}})

    def test_blueprint_missing_required_field(self):
        """Blueprints without 'slots' should raise validation error."""
        with pytest.raises(ValueError):
            BlueprintData.model_validate(
                {"id": "test", "result_name": "Test"}
            )

    def test_location_missing_required_field(self):
        """Locations without 'base_temp' should raise validation error."""
        with pytest.raises(ValueError):
            LocationData.model_validate(
                {"id": "test", "name": "Test", "description": "...", "exposure": 0.5}
            )

    def test_item_wrong_type(self):
        """Weight should be float, not string."""
        with pytest.raises(ValueError):
            ItemTemplate.model_validate(
                {"name": "Test", "weight": "heavy", "tags": {}}
            )


class TestLoaderRoundtrip:
    """Ensure data loaded from JSON is behaviour-identical to old hardcoded dicts."""

    def test_items_identical_to_old_data(self):
        """Each item from JSON must match old TEMPLATE_DB expectations."""
        items = load_items()
        # Check key items match the old hardcoded values
        assert items["stick"].name == "Eichenast"
        assert items["stick"].weight == 0.5
        assert items["stick"].tags == {"RIGID": True}
        assert items["stick"].attributes == {"durability": 0.8}

        assert items["flint_shard"].tags == {"HARD": True, "SHARP": True}
        assert items["flint_shard"].attributes["sharpness"] == 0.9

        assert items["reeds"].tags == {"RIGID": True, "FIBER": True}

        assert items["berries"].tags["EDIBLE"] == 50

    def test_blueprints_identical_to_old_data(self):
        bps = load_blueprints()
        assert len(bps) == 2
        axe = next(bp for bp in bps if bp.id == "axe")
        knife = next(bp for bp in bps if bp.id == "knife")

        assert axe.slots == {"head": "HARD", "handle": "RIGID", "binding": "FIBER"}
        assert knife.slots == {"blade": "SHARP", "handle": "RIGID"}

    def test_locations_have_three_nodes(self):
        locs = load_locations()
        assert len(locs) == 3
        assert all(hasattr(loc, "nodes") for loc in locs)