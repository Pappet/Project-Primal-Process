"""Tests für T2 — Direktor-Entscheid B10: `stick` → +WOOD (Data-Touch).

Befund-Cluster (Play 07.09./09.09./11.09.): die Nacht braucht ~64 Brennstoff-
Ticks; KINDLING-Quellen (reeds hidden_cave-only, tinder Prozess-Output) tragen
die Dauer im natürlichen Verlauf nicht. Der Ast — das naheliegendste „Holz" —
trug das Tag nicht: eine stille Datenlücke, kein Design-Wunsch.

Entscheid (Direktor, 13.09.): `stick` bekommt `"WOOD": true` (data/items.json,
ein Tag). Spiel-Logik: ein Ast IST Holz. Der WOOD-Fuel-Pfad über
`_find_fuel_item` existiert bereits (WOOD vor KINDLING, fire_pit nie) —
stoke_fire mit stick liefert STOKE_FUEL = 8 Ticks, quantity--.

Akzeptanz: Präferenz-Reihenfolge WOOD vor KINDLING verankert; fire_pit
(KINDLING-Template) wird nie verbrannt; stoke mit stick funktioniert; die
Zünd-Kette (start_fire braucht tinder+stick als Template-Inputs) bleibt
unangetastet; kein Blueprint-Slot matcht WOOD (Crafting-Pfade unverändert).
"""

import json
import os

import pytest

from engine.core import STOKE_FUEL, GameEngine
from data.items import create_item


def engine_with(items=()):
    e = GameEngine()
    for tid, qty in items:
        e.player.inventory.add(create_item(tid, qty))
    return e


class TestStickCarriesWood:
    """Der Data-Touch selbst: der Ast ist Holz — Template- und Instanz-Ebene."""

    def test_stick_template_has_wood_tag(self):
        with open(os.path.join("data", "items.json")) as f:
            data = json.load(f)
        assert data["stick"]["tags"].get("WOOD") is True
        assert data["stick"]["tags"].get("RIGID") is True  # unangetastet

    def test_stick_instance_carries_wood(self):
        stick = create_item("stick", 1)
        assert "WOOD" in stick.tags

    def test_no_blueprint_slot_matches_wood(self):
        """Blueprint-Touch-Gefahr (Task-Akzeptanz): kein Slot matcht WOOD —
        der Data-Touch darf die Crafting-Pfade nicht verschieben."""
        data = json.load(open(os.path.join("data", "blueprints.json")))
        for bp in data:
            assert "WOOD" not in json.dumps(bp.get("slots", {})), (
                f"Blueprint {bp['id']} matcht WOOD — Go/No-Go neu bewerten!")


class TestStokeWithStick:
    """stoke_fire mit stick: STOKE_FUEL, quantity--, Zünd-Kette unangetastet."""

    def test_stoke_with_stick_adds_fuel_and_consumes_one(self):
        e = engine_with([("stick", 3)])
        e._light_fire()
        fuel0 = e.current_location.fire_fuel
        res = e.stoke_fire()
        assert res["success"] is True
        assert e.current_location.fire_fuel == pytest.approx(
            fuel0 + STOKE_FUEL - 1)  # +8, −1 Tick Verbrennen
        assert e._count_template("stick") == 2  # quantity-- verbraucht einen

    def test_stoke_single_stick_consumes_item(self):
        e = engine_with([("stick", 1)])
        e._light_fire()
        res = e.stoke_fire()
        assert res["success"] is True
        assert e._count_template("stick") == 0  # letzter Stick weg


class TestFuelPreference:
    """`_find_fuel_item`-Präferenz-Reihenfolge: WOOD vor KINDLING, fire_pit
    nie — mit stick im WOOD-Pool bleibt die Ordnung unangetastet."""

    def test_wood_preferred_over_kindling(self):
        e = engine_with([("tinder", 2), ("stick", 1)])
        fuel = e._find_fuel_item()
        assert fuel is not None
        assert fuel.template_id == "stick"  # WOOD schlägt KINDLING

    def test_log_oak_wood_preferred_over_tinder(self):
        e = engine_with([("tinder", 2), ("log_oak", 1)])
        fuel = e._find_fuel_item()
        assert fuel is not None and fuel.template_id == "log_oak"

    def test_kindling_fallback_without_wood(self):
        e = engine_with([("tinder", 2)])
        fuel = e._find_fuel_item()
        assert fuel is not None and fuel.template_id == "tinder"

    def test_fire_pit_is_never_fuel(self):
        e = engine_with([("fire_pit", 1)])
        assert e._find_fuel_item() is None

    def test_fire_pit_not_burned_even_with_wood_pool(self):
        """fire_pit (KINDLING-Template) bleibt unverbrannt, auch wenn WOOD
        und anderes KINDLING fehlen — die Feuergrube ist das Feuer, nicht
        Brennstoff."""
        e = engine_with([("fire_pit", 1), ("reeds", 1)])
        fuel = e._find_fuel_item()
        assert fuel is not None and fuel.template_id == "reeds"


class TestZundeKetteUnangetastet:
    """Der Touch kürzt nichts ab: start_fire braucht weiter tinder + stick
    (Template-Inputs), die Feinheit tinder/reeds bleibt."""

    def test_start_fire_still_needs_tinder_and_stick(self):
        e = engine_with([("stick", 2)])
        res = e.execute_process("start_fire")
        assert res["success"] is False  # tinder fehlt — kein Weg dran vorbei

    def test_start_fire_works_with_tinder_and_sticks(self):
        e = engine_with([("tinder", 1), ("stick", 2)])
        res = e.execute_process("start_fire")
        assert res["success"] is True
        assert e.current_location.fire_active is True

    def test_wood_tag_changes_no_experiment(self):
        """(stick, stick) → spear bleibt; der WOOD-Tag matcht keinen
        Blueprint-Slot, also darf das Experiment-Ergebnis identisch sein.
        (Getrennte Item-Objekte — Inventory.add mergt zu einem Stack, und
        dasselbe Stack-Objekt kann nicht 2 Slots füllen: SPEC-005.)"""
        e = engine_with()
        items = [create_item("stick"), create_item("stick")]
        res = e.execute_experiment(items)
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"
