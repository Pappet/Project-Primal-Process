"""Tests for data/items.py — template creation."""
import pytest
from data.items import create_item, TEMPLATE_DB
from engine.components import Item


class TestCreateItem:
    def test_create_stick(self):
        item = create_item("stick")
        assert item.name == "Eichenast"
        assert item.base_weight == 0.5
        assert "RIGID" in item.tags
        assert item.get_attr("durability") == 0.8

    def test_create_flint_shard(self):
        item = create_item("flint_shard")
        assert item.name == "Feuersteinsplitter"
        assert "HARD" in item.tags
        assert "SHARP" in item.tags
        assert item.get_attr("sharpness") == 0.9

    def test_create_plant_fiber(self):
        item = create_item("plant_fiber")
        assert item.name == "Pflanzenfaser"
        assert "FIBER" in item.tags
        assert item.base_weight == 0.05

    def test_create_reeds(self):
        item = create_item("reeds")
        assert item.name == "Schilfrohr"
        assert "RIGID" in item.tags
        assert "FIBER" in item.tags

    def test_create_berries(self):
        item = create_item("berries")
        assert item.name == "Waldbeeren"
        assert "EDIBLE" in item.tags
        assert item.tags["EDIBLE"] == 50

    def test_create_mushroom(self):
        item = create_item("mushroom")
        assert item.name == "Wildpilz"
        assert item.tags["EDIBLE"] == 30

    def test_create_raw_meat(self):
        item = create_item("raw_meat")
        assert item.name == "Rohes Fleisch"
        assert item.tags["EDIBLE"] == 150

    def test_create_cooked_meat(self):
        item = create_item("cooked_meat")
        assert item.name == "Gebratenes Fleisch"
        assert item.tags["EDIBLE"] == 400

    def test_create_unknown_template(self):
        item = create_item("nonexistent")
        assert item.name == "Unbekannt"
        assert item.base_weight == 0.1

    def test_create_with_quantity(self):
        item = create_item("stick", quantity=5)
        assert item.quantity == 5
        assert item.total_weight == 2.5

    def test_tags_are_independent(self):
        """Modifying a created item's tags should not affect the template."""
        item1 = create_item("stick")
        item2 = create_item("stick")
        item1.tags["NEW_TAG"] = True
        assert "NEW_TAG" not in item2.tags

    def test_all_templates_creatable(self):
        for template_id in TEMPLATE_DB:
            item = create_item(template_id)
            assert isinstance(item, Item)
            assert item.name != "Unknown"