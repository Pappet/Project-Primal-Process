"""Fixtures shared across test modules."""
import pytest
from engine.components import Item, Inventory, Player, ToolBlueprint
from data.items import create_item
from data.blueprints import get_all_blueprints
from data.locations import get_all_locations


@pytest.fixture
def stick():
    return create_item("stick")


@pytest.fixture
def flint_shard():
    return create_item("flint_shard")


@pytest.fixture
def plant_fiber():
    return create_item("plant_fiber")


@pytest.fixture
def reeds():
    return create_item("reeds")


@pytest.fixture
def berries():
    return create_item("berries")


@pytest.fixture
def empty_inventory():
    return Inventory()


@pytest.fixture
def stocked_inventory(stick, flint_shard, plant_fiber):
    inv = Inventory()
    inv.add(stick)
    inv.add(flint_shard)
    inv.add(plant_fiber)
    return inv


@pytest.fixture
def blueprints():
    return get_all_blueprints()


@pytest.fixture
def locations():
    return get_all_locations()