"""Tests for engine.components — Item, Inventory, Player, ToolBlueprint."""
import pytest
from engine.components import Item, Inventory, Player, ToolBlueprint


class TestItem:
    def test_create_basic(self):
        item = Item(name="Stein", base_weight=1.0)
        assert item.name == "Stein"
        assert item.base_weight == 1.0
        assert item.quantity == 1
        assert item.condition == 1.0
        assert item.tags == {}
        assert item.attributes == {}

    def test_create_with_tags(self):
        item = Item(name="Feuerstein", base_weight=0.4, tags={"HARD": True, "SHARP": True})
        assert "HARD" in item.tags
        assert "SHARP" in item.tags
        assert item.tags["HARD"] is True

    def test_create_with_attributes(self):
        item = Item(name="Axt", base_weight=2.0, attributes={"durability": 0.8, "power": 1.5})
        assert item.get_attr("durability") == 0.8
        assert item.get_attr("power") == 1.5

    def test_get_attr_default(self):
        item = Item(name="Stein", base_weight=1.0)
        assert item.get_attr("nonexistent") == 0.0
        assert item.get_attr("nonexistent", 5.0) == 5.0

    def test_total_weight_single(self):
        item = Item(name="Stein", base_weight=1.0, quantity=1)
        assert item.total_weight == 1.0

    def test_total_weight_multiple(self):
        item = Item(name="Stein", base_weight=1.0, quantity=3)
        assert item.total_weight == 3.0

    def test_condition_default(self):
        item = Item(name="Stein", base_weight=1.0)
        assert item.condition == 1.0


class TestInventory:
    def test_empty(self):
        inv = Inventory()
        assert inv.current_weight == 0.0
        assert len(inv.items) == 0

    def test_add_single(self):
        inv = Inventory()
        item = Item(name="Stein", base_weight=1.0)
        assert inv.add(item) is True
        assert len(inv.items) == 1
        assert inv.current_weight == 1.0

    def test_add_stacking(self):
        inv = Inventory()
        item1 = Item(name="Stein", base_weight=1.0)
        item2 = Item(name="Stein", base_weight=1.0)
        inv.add(item1)
        inv.add(item2)
        assert len(inv.items) == 1
        assert inv.items[0].quantity == 2

    def test_add_no_stack_different_condition(self):
        inv = Inventory()
        item1 = Item(name="Stein", base_weight=1.0, condition=1.0)
        item2 = Item(name="Stein", base_weight=1.0, condition=0.5)
        inv.add(item1)
        inv.add(item2)
        assert len(inv.items) == 2

    def test_add_over_capacity(self):
        inv = Inventory(capacity_kg=1.0)
        item = Item(name="Felsbrocken", base_weight=2.0)
        assert inv.add(item) is False
        assert len(inv.items) == 0

    def test_find_item_by_tag(self, stocked_inventory):
        found = stocked_inventory.find_item_by_tag("HARD")
        assert found is not None
        assert found.name == "Feuersteinsplitter"

    def test_find_item_by_tag_missing(self, stocked_inventory):
        found = stocked_inventory.find_item_by_tag("NONEXISTENT")
        assert found is None

    def test_find_item_by_tag_broken(self):
        inv = Inventory()
        broken = Item(name="Kaputte Axt", base_weight=1.0, tags={"CHOPPING": True}, condition=0.0)
        inv.add(broken)
        assert inv.find_item_by_tag("CHOPPING") is None

    def test_total_insulation(self):
        inv = Inventory()
        fur = Item(name="Fell", base_weight=1.0, tags={"CLOTHING": True}, attributes={"insulation": 0.5})
        inv.add(fur)
        assert inv.get_total_insulation() == 0.5

    def test_total_insulation_no_clothing(self, stocked_inventory):
        assert stocked_inventory.get_total_insulation() == 0.0


class TestToolBlueprint:
    def test_create(self):
        bp = ToolBlueprint(id="axe", result_name="Axt", slots={"head": "HARD", "handle": "RIGID"}, base_efficiency=1.0)
        assert bp.id == "axe"
        assert bp.result_name == "Axt"
        assert bp.slots == {"head": "HARD", "handle": "RIGID"}
        assert bp.base_efficiency == 1.0
        assert bp.min_survival_req == 0.0


class TestPlayer:
    def test_create(self):
        p = Player("Test")
        assert p.name == "Test"
        assert p.energy == 800.0
        assert p.hp == 100.0
        assert p.body_temp == 37.0
        assert isinstance(p.inventory, Inventory)
        assert p.known_blueprints == set()

    def test_stats_default(self):
        p = Player("Test")
        assert p.stats["perception"] == 1.0
        assert p.stats["strength"] == 1.0
        assert p.stats["survival"] == 0.0