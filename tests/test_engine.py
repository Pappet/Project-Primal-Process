"""Tests for engine.core — GameEngine crafting and core mechanics."""
import pytest
from engine.core import GameEngine
from engine.components import Item
from data.items import create_item


class TestEngineCrafting:
    def test_axe_crafting_success(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        assert engine.player.stats["survival"] == 1.0

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is True
        assert "Axt" in result["message"]
        assert engine.player.stats["survival"] > 1.0  # Skill gain

    def test_knife_crafting_success(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        assert engine.player.stats["survival"] == 1.0

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is True
        assert "Messer" in result["message"]
        assert engine.player.stats["survival"] > 1.0

    def test_crafting_consumes_ingredients(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is True
        # Ingredients should be consumed; only the crafted tool remains
        assert len(engine.player.inventory.items) == 1

    def test_crafting_no_match(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("berries"))
        engine.player.inventory.add(create_item("mushroom"))

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is False
        assert result["message"] == "Nichts passiert."

    def test_crafting_wrong_count(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        # Only one item — axe needs 3
        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is False

    def test_known_blueprints_tracked(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))

        assert "knife" not in engine.player.known_blueprints

        items = list(engine.player.inventory.items)
        engine.execute_experiment(items)

        assert "knife" in engine.player.known_blueprints

    def test_known_blueprint_already_known(self):
        """Crafting a known blueprint again should not re-add or re-grant skill."""
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))

        # First craft
        items = [engine.player.inventory.items[0], engine.player.inventory.items[1]]
        result = engine.execute_experiment(items)
        assert result["success"] is True
        survival_after_first = engine.player.stats["survival"]

        # Second craft
        items = [engine.player.inventory.items[0], engine.player.inventory.items[1]]
        result = engine.execute_experiment(items)
        assert result["success"] is True
        # Skill should not increase again (already known)
        assert engine.player.stats["survival"] == survival_after_first


class TestEngineCore:
    def test_engine_init(self):
        engine = GameEngine()
        assert engine.player is not None
        assert engine.player.name == "Survivor"
        assert engine.current_location_id == "forest_edge"
        assert len(engine.locations) == 3
        assert len(engine.blueprints) == 2

    def test_current_location(self):
        engine = GameEngine()
        loc = engine.current_location
        assert loc.name == "Waldrand"

    def test_ambient_temp(self):
        engine = GameEngine()
        # Set tick to daytime (hour 12 = tick 72)
        engine.tick_counter = 72
        temp = engine._get_ambient_temp()
        # Should be around base temp (15°C) with clear weather, daytime
        assert 10.0 <= temp <= 25.0

    def test_eat_edible(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("berries", quantity=1))
        initial_energy = engine.player.energy
        result = engine.eat(0)
        assert engine.player.energy > initial_energy
        assert "Waldbeeren" in result

    def test_eat_inedible(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("stick"))
        result = engine.eat(0)
        assert "nicht essbar" in result

    def test_eat_consumes_item(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("berries", quantity=3))
        assert engine.player.inventory.items[0].quantity == 3
        engine.eat(0)
        assert engine.player.inventory.items[0].quantity == 2

    def test_eat_last_item_removes(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("berries", quantity=1))
        assert len(engine.player.inventory.items) == 1
        engine.eat(0)
        assert len(engine.player.inventory.items) == 0

    def test_travel_valid(self):
        engine = GameEngine()
        result = engine.travel("mountain_peak")
        assert "Gipfelkamm" in result
        assert engine.current_location_id == "mountain_peak"

    def test_travel_invalid(self):
        engine = GameEngine()
        result = engine.travel("atlantis")
        assert result == "Unbekannt."

    def test_weather_update(self):
        engine = GameEngine()
        # At tick 5 (not a multiple of 12), weather should not change
        engine.tick_counter = 5
        engine._update_weather()
        assert engine.current_weather == "CLEAR"
        # At tick 12, weather should update
        engine.tick_counter = 12
        engine._update_weather()
        assert engine.current_weather in engine.weather_types

    def test_advance_time_drains_energy(self):
        engine = GameEngine()
        initial_energy = engine.player.energy
        engine._advance_time(10, effort_multiplier=1.0)
        assert engine.player.energy < initial_energy

    def test_advance_time_starvation(self):
        engine = GameEngine()
        engine.player.energy = 0
        initial_hp = engine.player.hp
        engine._advance_time(5, effort_multiplier=1.0)
        assert engine.player.hp < initial_hp

    def test_advance_time_hypothermia(self):
        engine = GameEngine()
        engine.current_location_id = "mountain_peak"
        engine.current_weather = "SNOW"
        engine.player.body_temp = 37.0
        engine._advance_time(50, effort_multiplier=1.0)
        # Body temp should drop significantly
        assert engine.player.body_temp < 37.0

    def test_gather_basic(self):
        engine = GameEngine()
        # forest_edge has stick at 80% chance, req_perception 0
        results = engine.gather()
        # Should find something most of the time (stochastic but high chance)
        assert isinstance(results, list)

    def test_locations_have_nodes(self):
        engine = GameEngine()
        for loc in engine.locations.values():
            assert hasattr(loc, "nodes")
            assert isinstance(loc.nodes, list)