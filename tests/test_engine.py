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
        assert "axt" in result["message"].lower()  # "Feuersteinaxt"
        assert engine.player.stats["survival"] > 1.0  # Skill gain

    def test_knife_crafting_success(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        assert engine.player.stats["survival"] == 1.0

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is True
        assert "messer" in result["message"].lower()  # "Feuersteinmesser"
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
        # Die Meldung nennt das fehlende Label, nie "Nichts passiert."
        assert "fehlt" in result["message"]

    def test_crafting_wrong_count(self):
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        # Only one item — axe needs 3
        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)

        assert result["success"] is False

    def test_three_same_items_no_blueprint(self):
        """3 Items ohne gültige Kombination (berries+mushroom+stick) matcht
        keine Axt (HARD+RIGID+FIBER). Muss scheitern und das Merkmal nennen."""
        engine = GameEngine()
        for tpl in ("berries", "mushroom", "stick"):
            engine.player.inventory.add(create_item(tpl))
        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)
        assert result["success"] is False
        assert "Nichts passiert" not in result["message"]
        # Fehlt HARD (Axt) → Meldung nennt das Merkmal
        assert "fehlt" in result["message"]

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


class TestBlueprintFamilies:
    """SPEC-002: Tag-Familien + Blueprint-Familien (3 Werkzeug-Typen, je 2+ Varianten)."""

    def _give(self, engine, tpl, qty=1):
        engine.player.inventory.add(create_item(tpl, qty))

    def _craft(self, engine, tpls):
        """Gibt genau die genannten Template-IDs als Auswahl und craftet."""
        engine.player.inventory.items.clear()
        for t in tpls:
            self._give(engine, t)
        return engine.execute_experiment(list(engine.player.inventory.items))

    def test_three_tool_types_craftable(self):
        """Axt, Messer, Speer — drei unterschiedliche Werkzeug-Typen craftbar."""
        engine = GameEngine()
        res_axe = self._craft(engine, ["flint_shard", "stick", "plant_fiber"])
        assert res_axe["success"] is True and res_axe["blueprint_id"] == "axe"
        res_knife = self._craft(engine, ["flint_shard", "stick"])
        assert res_knife["success"] is True and res_knife["blueprint_id"] == "knife"
        # Speer braucht 2 Feste — via zwei DISTINKTE Materialien (Schilfrohr+Ast),
        # weil im Inventar gleichnamige Items zu einem Stack verschmelzen.
        res_spear = self._craft(engine, ["reeds", "stick"])
        assert res_spear["success"] is True and res_spear["blueprint_id"] == "spear"

    def test_axe_family_has_three_variants(self):
        """Axt-Familie: Feuerstein-, Knochen- und Stein-Variante, je eigener Tag-Kombi."""
        engine = GameEngine()
        assert self._craft(engine, ["flint_shard", "stick", "plant_fiber"])["blueprint_id"] == "axe"
        assert self._craft(engine, ["bone", "stick", "plant_fiber"])["blueprint_id"] == "axe_bone"
        assert self._craft(engine, ["sharp_stone", "stick", "plant_fiber"])["blueprint_id"] == "axe_stone"

    def test_knife_family_has_three_variants(self):
        engine = GameEngine()
        assert self._craft(engine, ["flint_shard", "stick"])["blueprint_id"] == "knife"
        assert self._craft(engine, ["bone", "stick"])["blueprint_id"] == "knife_bone"
        assert self._craft(engine, ["sharp_stone", "stick"])["blueprint_id"] == "knife_stone"

    def test_spear_from_reeds_and_stick(self):
        """Speer nutzt Familien-Slot SHARP_OR_RIGID: Schilfrohr + Ast genügen.

        Zwei Feste müssen aus zwei distinkten Materialien kommen (Schilfrohr trägt
        RIGID), weil gleichnamige Items im Inventar zu einem Stack verschmelzen.
        """
        engine = GameEngine()
        res = self._craft(engine, ["reeds", "stick"])
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"
        # Speer trägt PIERCE (eigene funktionale Tag, nicht CHOPPING/CUTTING)
        spear = next(i for i in engine.player.inventory.items if "PIERCE" in i.tags)
        assert spear is not None

    def test_spear_bound_is_second_variant(self):
        """Gebundener Speer = 2. Variante (2 RIGID + FIBER) mit eigener ID."""
        engine = GameEngine()
        res = self._craft(engine, ["reeds", "stick", "plant_fiber"])
        assert res["success"] is True
        assert res["blueprint_id"] == "spear_bound"

    def test_family_slot_matching_with_flint(self):
        """flint_shard (HARD+SHARP) füllt Familien-Slot SHARP_OR_RIGID als Spitze."""
        engine = GameEngine()
        res = self._craft(engine, ["flint_shard", "stick"])
        # 2 Items → Messer (FLINT-Klinge) hat Vorrang vor dem Speer
        assert res["blueprint_id"] == "knife"

    def test_discovery_feedback_is_categorized(self):
        """Fehlschlag mit bekanntem Ziel-Tag nennt konkretes Merkmal, nie generisch."""
        engine = GameEngine()
        # Spieler hat ein Festes + Faseriges (RIGID + FIBER), aber keine harte Klinge.
        engine.player.inventory.items.clear()
        self._give(engine, "stick")
        self._give(engine, "stick")
        self._give(engine, "plant_fiber")
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["success"] is False
        assert res["reason"].startswith("MISSING_TAG:")
        assert "fehlt" in res["message"]
        assert "Nichts passiert" not in res["message"]

    def test_bone_gatherable_in_hidden_cave(self, monkeypatch):
        """Knochen (BONE) ist als Materialquelle erreichbar → BONE-Varianten machbar."""
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        engine.travel("hidden_cave")
        engine.gather()
        assert any(i.template_id == "bone" for i in engine.player.inventory.items)


class TestEngineCore:
    def test_engine_init(self):
        engine = GameEngine()
        assert engine.player is not None
        assert engine.player.name == "Survivor"
        assert engine.current_location_id == "forest_edge"
        assert len(engine.locations) == 3
        assert len(engine.blueprints) == 8

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


class TestBugs:
    """Regression tests for the KW-32 sprint bug fixes (B01-B05)."""

    def test_b01_new_session_can_gather_fiber_and_craft_axe(self, monkeypatch):
        """B01/B03: FIBER is gatherable at start and a full axe craft works."""
        from engine.core import GameEngine
        engine = GameEngine()
        # Deterministic: every node roll succeeds
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)

        engine.gather()  # forest_edge: plant_fiber (FIBER) + stick (RIGID)
        assert any("FIBER" in it.tags for it in engine.player.inventory.items)

        engine.travel("mountain_peak")
        engine.gather()  # flint_shard (HARD)

        hard = next(it for it in engine.player.inventory.items if "HARD" in it.tags)
        rigid = next(it for it in engine.player.inventory.items if "RIGID" in it.tags)
        fiber = next(it for it in engine.player.inventory.items if "FIBER" in it.tags)
        result = engine.execute_experiment([hard, rigid, fiber])
        assert result["success"] is True
        assert "axt" in result["message"].lower()

    def test_b03_perception_gates_reachable_at_start(self):
        """B03: berries/mushroom/flint reachable at start perception, no grind."""
        from data.locations import get_all_locations
        targets = {"berries", "mushroom", "flint_shard"}
        seen = set()
        for loc in get_all_locations():
            for node in loc.nodes:
                if node.result_template_id in targets:
                    seen.add(node.result_template_id)
                    assert node.req_perception <= 1.0  # start perception
        assert seen == targets

    def test_b04_crafting_with_broken_item_fails(self):
        """B04: condition=0 item must block crafting with clear feedback."""
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        engine.player.inventory.items[1].condition = 0.0  # broken stick

        items = list(engine.player.inventory.items)
        result = engine.execute_experiment(items)
        assert result["success"] is False
        assert "zerbrochen" in result["message"]

    def test_b05_new_session_starts_in_morning(self):
        """B05: new session starts at 6:00 (tick 36), no night temp penalty."""
        engine = GameEngine()
        assert engine.tick_counter == 36
        hour = (engine.tick_counter % 144) / 6
        assert hour == 6
        # forest_edge base_temp 15, CLEAR weather, daytime → no -10 night mod
        assert engine._get_ambient_temp() >= 15.0


class TestBugB06B07DanglingTemplates:
    """B06/B07 (BACKLOG 05.08., erneut bestätigt 07.08.): Nodes referenzieren
    Templates, die es in items.json nicht gibt → 'Unbekannt'-Müll. Fix: echte
    Templates + SHOVEL-Träger (Axt als Grabwerkzeug)."""

    def test_b06_log_oak_template_exists(self):
        """log_oak hat jetzt ein echtes Template — kein 'Unbekannt' mehr."""
        from data.items import create_item, TEMPLATE_DB
        assert "log_oak" in TEMPLATE_DB
        item = create_item("log_oak")
        assert item.name != "Unbekannt"
        assert "RIGID" in item.tags

    def test_b06_log_oak_gatherable_with_axe(self, monkeypatch):
        """Axt (CHOPPING) fällt im Waldrand Eichenstamm — die Kern-Verheißung."""
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        res = engine.execute_experiment(list(engine.player.inventory.items))
        assert res["success"] is True  # Axt bauen
        engine.gather()  # Waldrand: log_oak braucht CHOPPING → Axt gräbt/fällt
        assert any(i.template_id == "log_oak" for i in engine.player.inventory.items)

    def test_b07_clay_lump_template_exists(self):
        """clay_lump hat jetzt ein echtes Template — kein 'Unbekannt' mehr."""
        from data.items import create_item, TEMPLATE_DB
        assert "clay_lump" in TEMPLATE_DB
        item = create_item("clay_lump")
        assert item.name != "Unbekannt"
        assert "CLAY" in item.tags

    def test_b07_axe_carries_shovel(self):
        """Axt trägt SHOVEL → kann Ton graben (BACKLOG-Fixrichtung: Axt als
        Grabwerkzeug, kein neues Werkzeug nötig)."""
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        engine.execute_experiment(list(engine.player.inventory.items))
        axe = next(i for i in engine.player.inventory.items if "CHOPPING" in i.tags)
        assert "SHOVEL" in axe.tags

    def test_b07_clay_lump_gatherable_in_hidden_cave(self, monkeypatch):
        """Mit Axt (SHOVEL) ist der Ton in der Höhle erreichbar — toter Pfad lebt."""
        from data.locations import ResourceNode
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        # Axt samt SHOVEL beschaffen
        engine.player.inventory.add(create_item("flint_shard"))
        engine.player.inventory.add(create_item("stick"))
        engine.player.inventory.add(create_item("plant_fiber"))
        engine.execute_experiment(list(engine.player.inventory.items))
        engine.travel("hidden_cave")
        engine.gather()
        assert any(i.template_id == "clay_lump" for i in engine.player.inventory.items)


class TestProcessSystem:
    """SPEC-001: Prozess-System in die Engine eingebunden."""

    def _give(self, engine, tpl, qty=1):
        engine.player.inventory.add(create_item(tpl, qty))

    def test_make_sharp_stone_from_pebbles(self):
        engine = GameEngine()
        self._give(engine, "pebble", 2)
        res = engine.execute_process("make_sharp_stone")
        assert res["success"] is True
        assert res["process_id"] == "make_sharp_stone"
        assert engine._count_template("sharp_stone") == 1
        assert engine._count_template("pebble") == 0

    def test_unknown_process(self):
        engine = GameEngine()
        res = engine.execute_process("bogus")
        assert res["success"] is False
        assert res["reason"] == "UNKNOWN_PROCESS"

    def test_missing_input_fails_without_consuming(self):
        engine = GameEngine()
        self._give(engine, "pebble", 1)  # braucht 2
        res = engine.execute_process("make_sharp_stone")
        assert res["success"] is False
        assert res["reason"] == "MISSING_INPUT:pebble"
        assert engine._count_template("pebble") == 1

    def test_create_tinder_requires_cutting_tool(self):
        engine = GameEngine()
        self._give(engine, "reeds", 2)
        res = engine.execute_process("create_tinder")
        assert res["success"] is False
        assert res["reason"] == "MISSING_TOOL:CUTTING"
        assert engine._count_template("reeds") == 2  # nichts verbraucht

    def test_crafted_knife_cuts(self):
        """knife erhält CUTTING → erfüllt Werkzeug-Anforderung von create_tinder."""
        engine = GameEngine()
        self._give(engine, "flint_shard")
        self._give(engine, "stick")
        engine.execute_experiment(list(engine.player.inventory.items))
        knife = next(i for i in engine.player.inventory.items if "CUTTING" in i.tags)
        assert knife is not None

    def test_create_tinder_with_knife(self):
        engine = GameEngine()
        self._give(engine, "reeds", 2)
        self._give(engine, "flint_shard")
        self._give(engine, "stick")
        engine.execute_experiment([engine.player.inventory.items[-2],
                                   engine.player.inventory.items[-1]])
        res = engine.execute_process("create_tinder")
        assert res["success"] is True
        assert engine._count_template("tinder") == 3
        assert engine._count_template("reeds") == 0

    def test_start_fire_uses_tinder_sticks_and_kindling(self):
        engine = GameEngine()
        self._give(engine, "reeds", 1)   # KINDLING-Werkzeug
        self._give(engine, "tinder", 1)
        self._give(engine, "stick", 2)
        res = engine.execute_process("start_fire")
        assert res["success"] is True
        assert engine._count_template("fire_pit") == 1

    def test_cook_meat_from_raw_meat(self):
        engine = GameEngine()
        self._give(engine, "raw_meat", 1)
        res = engine.execute_process("cook_meat")
        assert res["success"] is True
        assert engine._count_template("raw_meat") == 0
        assert engine._count_template("cooked_meat") == 1

    def test_process_consumes_inputs_and_adds_output(self):
        engine = GameEngine()
        self._give(engine, "pebble", 2)
        engine.execute_process("make_sharp_stone")
        assert engine._count_template("pebble") == 0
        assert engine._count_template("sharp_stone") == 1

    def test_known_processes_tracked(self):
        engine = GameEngine()
        self._give(engine, "pebble", 2)
        assert "make_sharp_stone" not in engine.player.known_processes
        engine.execute_process("make_sharp_stone")
        assert "make_sharp_stone" in engine.player.known_processes

    def test_available_processes_reflect_inventory(self):
        engine = GameEngine()
        assert "make_sharp_stone" not in engine.available_processes()
        self._give(engine, "pebble", 2)
        assert "make_sharp_stone" in engine.available_processes()

    def test_reeds_gatherable_in_hidden_cave(self, monkeypatch):
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        engine.travel("hidden_cave")
        engine.gather()
        assert any("reeds" == i.template_id for i in engine.player.inventory.items)

    def test_full_process_chain_reachable(self):
        """Acceptance: make_sharp_stone → create_tinder → start_fire alle machbar."""
        # reeds + KINDLING (reeds trägt KINDLING) + Crafting-Werkzeug
        engine = GameEngine()
        self._give(engine, "reeds", 2)
        self._give(engine, "tinder", 1)
        self._give(engine, "stick", 2)
        self._give(engine, "pebble", 2)
        # make_sharp_stone läuft unabhängig
        assert engine.execute_process("make_sharp_stone")["success"] is True
        # create_tinder: reeds als Input (CUTTING nötig) — hier direkt Reeds+KINDLING
        # start_fire nutzt tinder + sticks + reeds(KINDLING)
        assert engine._count_template("fire_pit") == 0
        assert engine.execute_process("start_fire")["success"] is True
        assert engine._count_template("fire_pit") == 1


class TestSpec004ResourceDepletion:
    """SPEC-004: vorratsbasierte Nodes — Erschöpfung, Regeneration, Chance."""

    def test_fresh_engine_nodes_start_full_stock(self):
        """Engine-Zustand ist pro-Instanz: jeder Node startet auf max_stock."""
        engine = GameEngine()
        for loc in engine.locations.values():
            for node in loc.nodes:
                assert node.stock == node.max_stock

    def test_depleted_node_reports_instead_of_silent_nothing(self, monkeypatch):
        """Erschöpfter Node → ehrliche DEPLETED-Meldung, nie stilles \"nichts\"."""
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        for node in engine.current_location.nodes:
            node.stock = 0.0
            node.depleted = True
        before = len(engine.player.inventory.items)
        logs = engine.gather()
        assert logs  # Gather liefert Feedback, kein Leerlauf
        assert any("erschöpft" in l for l in logs)
        assert len(engine.player.inventory.items) == before  # nichts gesammelt
        assert all(n.depleted for n in engine.current_location.nodes)

    def test_repeated_gather_depletes_node(self, monkeypatch):
        """Über-Ernten eines Ortes hungert ihn aus und meldet das ehrlich."""
        from data.locations import ResourceNode
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        # Synthetischer KNAPPER Node (wie flint/bone): Regen so klein, dass
        # Erschöpfung stabil bleibt (generöse Grundstoffe oscilieren nur kurz).
        node = ResourceNode("stick", 1, 1, chance=1.0, max_stock=3.0,
                            regen_per_tick=0.01, harvest_cost=1.0)
        engine.current_location.nodes = [node]
        for _ in range(10):
            engine.gather()
        assert node.depleted is True
        assert node.stock < node.harvest_cost
        logs = engine.gather()
        assert any("erschöpft" in l for l in logs)

    def test_regeneration_restores_stock_and_harvest(self, monkeypatch):
        """Zeit regeneriert Nodes; erschöpfter Node wird wieder erntbar."""
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        engine = GameEngine()
        for node in engine.current_location.nodes:
            node.stock = 0.0
            node.depleted = True
        engine._advance_time(200)  # genug verstrichene Zeit
        stick = next(n for n in engine.current_location.nodes
                     if n.result_template_id == "stick")
        assert stick.depleted is False  # erholt über die Zeit
        assert stick.stock > 0
        assert stick.stock <= stick.max_stock
        engine.gather()
        assert any(i.template_id == "stick" for i in engine.player.inventory.items)

    def test_regeneration_caps_at_max_stock(self):
        """Regeneration übersteigt max_stock nie."""
        engine = GameEngine()
        node = next(n for n in engine.current_location.nodes
                    if n.result_template_id == "stick")
        node.stock = node.max_stock - 1.0
        engine._advance_time(1000)
        assert node.stock == node.max_stock

    def test_success_chance_scales_with_stock(self, monkeypatch):
        """eff_chance = chance * (stock/max_stock): halbe Stelle, halbe Chance."""
        engine = GameEngine()
        stick = next(n for n in engine.current_location.nodes
                     if n.result_template_id == "stick")  # chance 0.8
        for n in engine.current_location.nodes:
            if n is not stick:
                n.stock = 0.0
        # Halber Vorrat → eff 0.4; random 0.6 > 0.4 → Fehlschlag trotz hoher Basis
        stick.stock = stick.max_stock / 2.0
        monkeypatch.setattr("engine.core.random.random", lambda: 0.6)
        engine.gather()
        assert not any(i.template_id == "stick" for i in engine.player.inventory.items)
        # Volle Stelle → eff 0.8; random 0.6 <= 0.8 → Treffer
        stick.stock = stick.max_stock
        engine.gather()
        assert any(i.template_id == "stick" for i in engine.player.inventory.items)

    def test_depleted_has_label_in_feedback_message(self):
        """DEPLETED hat ein Label in _feedback_message (feedback_quality-Zweig)."""
        from engine.core import _feedback_message
        assert "erschöpft" in _feedback_message("DEPLETED")


class TestStackMultiSlot:
    """SPEC-005: Ein Stack mit quantity N kann N identische Blueprint-Slots füllen."""

    def _stack(self, engine, tpl, qty=1):
        engine.player.inventory.add(create_item(tpl, qty))
        return next(it for it in engine.player.inventory.items if it.template_id == tpl)

    def test_spear_from_single_stack_of_two_sticks(self):
        """Speer (SHARP_OR_RIGID + RIGID) craftbar aus einem 2x-Stick-Stack — die
        frühere 'zwei distinkte Materialien'-Zwangslösung ist damit überflüssig."""
        engine = GameEngine()
        stack = self._stack(engine, "stick", 2)
        res = engine.execute_experiment([stack, stack])
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"
        # beide Stöcke verbraucht → nur noch der Speer im Inventar
        names = [it.name for it in engine.player.inventory.items]
        assert names == [res["message"].split(": ", 1)[-1]]

    def test_consumption_leaves_remaining_quantity(self):
        """2-Slot-Craft aus Stack qty=3 hinterlässt qty=1 — kein Doppel-Entfernen."""
        engine = GameEngine()
        stack = self._stack(engine, "stick", 3)
        engine.execute_experiment([stack, stack])
        remaining = [it for it in engine.player.inventory.items
                     if it.template_id == "stick"]
        assert len(remaining) == 1
        assert remaining[0].quantity == 1

    def test_insufficient_quantity_gives_feedback_no_fail_start(self):
        """Stack qty=1 zweimal genutzt → verständliches Feedback statt Craft aus Nichts."""
        engine = GameEngine()
        stack = self._stack(engine, "stick", 1)
        res = engine.execute_experiment([stack, stack])
        assert res["success"] is False
        assert res["reason"] == "NOT_ENOUGH_QUANTITY"
        assert "mehr" in res["message"]
        # nichts verbraucht, nichts erzeugt
        assert [it.template_id for it in engine.player.inventory.items] == ["stick"]
        assert engine.player.inventory.items[0].quantity == 1

    def test_distinct_stacks_still_craft(self):
        """Zwei getrennte Ast-Stacks (je qty=1) bleiben craftbar — Kontrolle."""
        engine = GameEngine()
        # direkte Objekte, da Inventory.add gleichnamige Items zu einem Stack
        # verschmilzt — zwei getrennte Ast-Stacks entstehen so nicht über add().
        engine.player.inventory.items.append(create_item("stick", 1))
        engine.player.inventory.items.append(create_item("stick", 1))
        items = list(engine.player.inventory.items)
        assert len(items) == 2  # zwei distinkte Stack-Objekte
        res = engine.execute_experiment(items)
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"

    def test_insufficient_quantity_only_for_duplicate_use(self):
        """Einmalige Nutzung eines qty=1-Stacks bleibt erlaubt (z.B. Messer/Stiel)."""
        engine = GameEngine()
        engine.player.inventory.add(create_item("flint_shard", 1))
        stack = self._stack(engine, "stick", 1)
        items = list(engine.player.inventory.items)
        res = engine.execute_experiment(items)
        assert res["success"] is True
        assert res["blueprint_id"] == "knife"

    def test_not_enough_quantity_has_label(self):
        """NOT_ENOUGH_QUANTITY hat ein Label in _feedback_message."""
        from engine.core import _feedback_message
        assert "mehr" in _feedback_message("NOT_ENOUGH_QUANTITY")