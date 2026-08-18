"""Tests for data/loader.py — JSON loading and validation."""
import pytest
from pathlib import Path

from data.loader import (
    load_items,
    load_blueprints,
    load_locations,
    load_processes,
    ItemTemplate,
    ItemTemplatesDB,
    BlueprintData,
    ResourceNodeData,
    LocationData,
    ProcessData,
    _load_json,
)


class TestLoadItems:
    def test_loads_all_templates(self):
        items = load_items()
        assert isinstance(items, dict)
        assert "stick" in items
        assert "flint_shard" in items
        assert "berries" in items
        assert "pebble" in items
        # SPEC-001: Prozess-Output-Templates (sharp_stone, tinder, fire_pit)
        assert "sharp_stone" in items
        assert "tinder" in items
        assert "fire_pit" in items
        # SPEC-002: Knochen als Werkstoff-Variante (BONE-Axt/Messer)
        assert "bone" in items
        # B06/B07: log_oak (Waldrand, CHOPPING) + clay_lump (Höhle, SHOVEL)
        assert "log_oak" in items
        assert "clay_lump" in items
        # SPEC-007: fur_cloak (CLOTHING/Isolation) — tragbarer Wärmeschutz
        assert "fur_cloak" in items
        assert len(items) == 16

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
        assert len(bps) == 10
        ids = [bp.id for bp in bps]
        assert "axe" in ids
        assert "knife" in ids
        # SPEC-002: 3 Werkzeug-Typen (axt/messer/speer), je ≥ 2 Varianten
        assert "spear" in ids
        assert "spear_bound" in ids

    def test_blueprint_has_correct_slots(self):
        bps = load_blueprints()
        axe = next(bp for bp in bps if bp.id == "axe")
        assert axe.result_name == "Feuersteinaxt"
        assert axe.slots == {"head": "FLINT", "handle": "RIGID", "binding": "FIBER"}
        assert axe.base_efficiency == 1.0
        # B07: Axt trägt SHOVEL → kann Ton graben (Grabwerkzeug, kein neuer Tool)
        assert axe.tool_tags == ["CHOPPING", "SHOVEL"]


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
        assert len(forest.nodes) == 5  # + raw_meat (SPEC-001)

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


class TestLoadProcesses:
    def test_loads_all_processes(self):
        procs = load_processes()
        assert len(procs) == 5
        ids = [p.id for p in procs]
        assert "make_sharp_stone" in ids
        assert "create_tinder" in ids
        assert "start_fire" in ids
        assert "cook_meat" in ids  # SPEC-001: Koch-Prozess
        assert "make_fur_cloak" in ids  # SPEC-007: Fellumhang (Isolation)

    def test_process_has_correct_fields(self):
        procs = load_processes()
        sharp = next(p for p in procs if p.id == "make_sharp_stone")
        assert sharp.name == "Stein schlagen (Knapping)"
        assert sharp.inputs == {"pebble": 2}
        assert sharp.tools == []
        assert sharp.outputs == {"sharp_stone": 1}
        assert sharp.duration_ticks == 2
        assert sharp.required_tag_in_env is None

    def test_create_tinder_uses_tool_tag(self):
        procs = load_processes()
        tinder = next(p for p in procs if p.id == "create_tinder")
        assert tinder.tools == ["CUTTING"]

    def test_process_missing_required_field(self):
        """Processes without 'inputs' should raise validation error."""
        with pytest.raises(ValueError):
            ProcessData.model_validate(
                {"id": "test", "name": "Test", "tools": [], "outputs": {}, "duration_ticks": 1}
            )

    def test_get_all_processes_returns_defs(self):
        """Public API builds ProcessDef objects from JSON (no hardcoded defs)."""
        from data.processes import get_all_processes, ProcessDef
        procs = get_all_processes()
        assert len(procs) == 5
        assert all(isinstance(p, ProcessDef) for p in procs)
        sharp = next(p for p in procs if p.id == "make_sharp_stone")
        assert sharp.inputs == {"pebble": 2}
        assert sharp.outputs == {"sharp_stone": 1}


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

        assert items["flint_shard"].tags == {"HARD": True, "SHARP": True, "FLINT": True}
        assert items["flint_shard"].attributes["sharpness"] == 0.9

        assert items["reeds"].tags == {"RIGID": True, "FIBER": True, "KINDLING": True}

        assert items["berries"].tags["EDIBLE"] == 50

    def test_blueprints_identical_to_old_data(self):
        bps = load_blueprints()
        assert len(bps) == 10
        axe = next(bp for bp in bps if bp.id == "axe")
        knife = next(bp for bp in bps if bp.id == "knife")

        assert axe.slots == {"head": "FLINT", "handle": "RIGID", "binding": "FIBER"}
        assert knife.slots == {"blade": "FLINT", "handle": "RIGID"}

    def test_locations_have_three_nodes(self):
        locs = load_locations()
        assert len(locs) == 3
        assert all(hasattr(loc, "nodes") for loc in locs)