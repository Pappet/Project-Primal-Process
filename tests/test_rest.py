"""Tests für SPEC-015 — Rast: Zeit als investierbare Ressource.

Ein Verb, das REST_TICKS Ticks über den bestehenden `_advance_time`-Pfad
verstreichen lässt, mit reduziertem Effort (REST_EFFORT statt gather-2.0).
Kein paralleler Simulations-Pfad, keine neuen RNG-Würfe: Feuer, Wetter,
SPEC-014-Warnungen, Heilung und Node-Regen laufen durch den Tick-Pfad.

Akzeptanz (Spec): rest-Ticks/Effort-Vertrag, Heil-Kette über Rast (am Feuer
ja, ohne Feuer nein), FIRE_OUT/UNTERKÜHLUNG während Rast ehrlich, keine-Draws,
Menü-Regression ([r]), kein Rezept-Leak.
"""
import random

import pytest

from engine.core import (GameEngine, REST_EFFORT, REST_HEAL_BONUS,
                         REST_TICKS)
from data.items import create_item


def engine_with(items=()):
    e = GameEngine()
    for tid, qty in items:
        e.player.inventory.add(create_item(tid, qty))
    return e


class TestRestContract:
    """Kriterium 1: Rast existiert als Verb — REST_TICKS/REST_EFFORT-Vertrag."""

    def test_constants_match_spec(self):
        assert REST_TICKS == 4
        assert REST_EFFORT == 0.4
        assert REST_HEAL_BONUS == 1.0  # bewusste Reserve, nicht verdrahtet

    def test_rest_exists_and_returns_success(self):
        e = engine_with()
        res = e.rest()
        assert res["success"] is True
        assert res["reason"] == "SUCCESS"
        assert "rastest" in res["message"].lower()

    def test_rest_advances_exactly_rest_ticks(self):
        e = engine_with()
        t0 = e.tick_counter
        e.rest()
        assert e.tick_counter == t0 + REST_TICKS

    def test_rest_effort_is_reduced_not_full(self):
        """80 Rast-Ticks kosten 160 Energie statt gather-Effort-2.0 → 800
        (Spec-Zahlen, Kriterium 1: verifizierbar über Energie-Delta)."""
        e = engine_with()
        e0 = e.player.energy
        for _ in range(20):  # 20 Rast-Zyklen × 4 Ticks = 80 Ticks
            e.rest()
        assert e0 - e.player.energy == pytest.approx(80 * 5.0 * REST_EFFORT)

    def test_rest_repeats_freely(self):
        """Rast ist ein kurzer Zeitsprung, den man wiederholen muss —
        kein einmaliger Sleep-Skip bis Morgen."""
        e = engine_with()
        t0 = e.tick_counter
        for _ in range(10):
            assert e.rest()["success"] is True
        assert e.tick_counter == t0 + 10 * REST_TICKS


class TestRestNoNewDraws:
    """Kriterium 4 (Stream-Disziplin): Rast würfelt nur die bestehenden
    %-12-Wetter-Crossings von _advance_time — kein eigener RNG-Kontakt."""

    def test_no_draws_outside_weather_crossings(self):
        e = engine_with()
        e.tick_counter = 36  # % 12 != 0 → nächstes _advance_time würfelt nicht
        e.current_weather = "CLEAR"
        state0 = random.getstate()
        e.rest()
        # Ohne Crossing kein einziger Wurf aus dem Hauptstrom.
        assert random.getstate() == state0

    def test_only_crossing_ticks_touch_main_rng(self):
        e = engine_with()
        e.tick_counter = 8  # 4 Ticks später: 12 → genau ein Crossing
        state0 = random.getstate()
        rng_probe = random.Random()
        rng_probe.setstate(state0)
        e.rest()
        # Genau ein random.choice-Wurf (Wetter-Crossing) verbraucht Zustand.
        expected = rng_probe.choice(list(e.weather_types.keys()))
        assert e.current_weather == expected


class TestRestThroughTickPath:
    """Kriterium 2: alle Systeme laufen durch den Tick-Pfad — Feuer brennt ab,
    Wetter würfelt, SPEC-014-Warnungen feuern, Node-Regen läuft."""

    def test_fire_fuel_burns_during_rest(self):
        e = engine_with()
        e._light_fire()
        e.current_location.fire_fuel = 50.0
        e.rest()
        assert e.current_location.fire_fuel == pytest.approx(50.0 - REST_TICKS)

    def test_fire_out_during_rest_is_honest(self):
        e = engine_with()
        e._light_fire()
        e.current_location.fire_fuel = 2.0  # < REST_TICKS → kippt in der Rast
        res = e.rest()
        assert e.current_location.fire_active is False
        assert "FIRE_OUT" in res["message"]

    def test_fire_dying_hint_fires_during_rest(self):
        e = engine_with()
        e._light_fire()
        e.current_location.fire_fuel = 10.0  # Crossing < FIRE_LOW_FUEL (8)
        res = e.rest()
        assert "Das Feuer wird schwach" in res["message"]

    def test_cold_hint_fires_during_rest_without_fire(self):
        """SPEC-014-Warnungen feuern auch während der Rast — Rast-Zeit ist
        ehrliche Zeit, keine Hint-freie Blase. (Mountain-Peak-Nacht: der
        4-Tick-Rast-Chunk kippt unter die Schmerzgrenze 35.0 → dort spricht
        UNTERKÜHLUNG statt der Warnung; Shelter verläuft flacher.)"""
        e = engine_with()
        e.travel("mountain_peak")  # base_temp 2.0, exposure 1.0, kein Feuer
        e.tick_counter = 36        # Tag (CLEAR-Tag: 37.0 → 36.1 je 4 Ticks)
        e.current_weather = "CLEAR"
        e.player.body_temp = 36.5  # Crossing unter COLD_WARN_THRESHOLD (36.0)
        res = e.rest()
        assert "Die Kälte nagt" in res["message"]

    def test_nodes_regen_during_rest(self):
        e = engine_with()
        node = e.current_location.nodes[0]
        node.stock = 0.0
        node.depleted = True
        node.regen_per_tick = 0.5
        node.harvest_cost = 1.0
        node.max_stock = 10.0
        e.rest()
        # REST_TICKS × 0.5 = 2.0 ≥ harvest_cost → depleted wieder frei
        assert node.stock == pytest.approx(REST_TICKS * 0.5)
        assert node.depleted is False

    def test_weather_can_change_during_rest(self):
        e = engine_with()
        e.tick_counter = 8  # REST_TICKS → Crossing bei Tick 12
        e.rest()
        assert e.current_weather in e.weather_types


class TestRestHealingChain:
    """Kriterium 2 (Heil-Kette): behandelte Wunde heilt über Rast-Zyklen am
    Feuer / sheltered — ohne beides nie. Rast macht die bestehende
    `treated + _resting_warm()`-Bedingung anwendbar, kein Auto-Heal.
    (Behandlung braucht Verband — make_bandage geht voraus.)"""

    def test_treated_wound_heals_via_rest_at_fire(self):
        e = engine_with([("plant_fiber", 4)])
        e._inflict("cut")
        e._light_fire()
        e.current_location.fire_fuel = 500.0
        e.execute_process("make_bandage")
        e.execute_process("treat_cut")
        for _ in range(5):  # Probe: verheilt nach 5 Rast-Zyklen (20 Ticks)
            e.rest()
        assert "cut" not in e.player.injuries

    def test_treated_wound_heals_via_rest_in_shelter(self):
        e = engine_with([("plant_fiber", 4)])
        e._inflict("cut")
        e.travel("hidden_cave")  # exposure 0.1 ≤ REST_EXPOSURE → Rast-Bedingung
        e.execute_process("make_bandage")
        e.execute_process("treat_cut")
        for _ in range(5):  # Probe: verheilt im 5. Rast-Zyklus (severity 0.65
            e.rest()        # nach treat-ticks → +4×0.05/Zyklus ≤ 0.05)
        assert "cut" not in e.player.injuries

    def test_treated_wound_does_not_heal_resting_exposed(self):
        e = engine_with([("plant_fiber", 4)])
        e._inflict("cut")
        e.travel("mountain_peak")  # exposure 1.0, kein Feuer → nie _resting_warm
        e.current_weather = "CLEAR"
        e.execute_process("make_bandage")
        e.execute_process("treat_cut")
        for _ in range(10):
            e.rest()
        assert "cut" in e.player.injuries

    def test_untreated_wound_never_heals_via_rest(self):
        e = engine_with()
        e._inflict("cut")
        e._light_fire()
        e.current_location.fire_fuel = 500.0
        for _ in range(10):
            e.rest()
        assert "cut" in e.player.injuries  # Rast ersetzt Behandlung nicht


class TestRestIsNoFreeSleep:
    """Kriterium 3: Nacht-Rast ohne Brennstoff-Nachlegen friert — Rast
    verschiebt das Kälte-Problem nicht, es macht es planbar."""

    def test_night_rest_without_fire_freezes_player(self):
        """Gipfel-Nacht ohne Feuer: bt fällt pro 4er-Rast ~1.7°, nach 2-3
        Rasten unter 35.0 → UNTERKÜHLUNG-Drain (Probe: 34.19 → 32.50 → …)."""
        e = engine_with()
        e.travel("mountain_peak")  # base_temp 2.0, Nacht-Mod −10
        e.current_weather = "CLEAR"
        e.tick_counter = 132  # 22:00 → Stunde 3.0 < 6 = Nacht
        bt0 = e.player.body_temp
        hp0 = e.player.hp
        for _ in range(3):
            e.rest()
        assert e.player.body_temp < bt0
        assert e.player.body_temp < 35.0   # UNTERKÜHLUNG-Drain lief
        assert e.player.hp < hp0           # ehrlicher Schaden, keine Blase

    def test_night_rest_survivable_with_stocked_fire(self):
        """Planbarkeit: Feuer vor der Nacht sichern (Brennstoff nachlegen) →
        die Nacht ist überstehbar. Kein Sleep-Skip: kostet laufend Brennstoff
        und Hunger-Ticks (Probe: bt pendelt 36-42, kein UNTERKÜHLUNG)."""
        e = engine_with()
        e.travel("forest_edge")
        e._light_fire()
        e.current_location.fire_fuel = 500.0
        e.tick_counter = 132  # Nacht
        e.current_weather = "CLEAR"
        for _ in range(30):  # 120 Rast-Ticks = eine Nacht am Feuer
            if not e.current_location.fire_active:
                break
            e.rest()
        assert e.player.body_temp >= 35.0  # kein UNTERKÜHLUNG-Tick
        assert e.player.energy > 0         # Hunger lief, aber dosiert


class TestMenuRegression:
    """Kriterium 6: [r] ist im Menü, der Parser bricht nicht, Handler
    musterkonform zu [w]ärmen; Kriterium 7: kein Rezept-Leak."""

    def test_menu_line_lists_rest(self):
        import inspect

        import main
        src = inspect.getsource(main.main)
        assert "[r]asten" in src
        assert "game.rest()" in src

    def test_rest_message_is_generic_no_leak(self):
        e = engine_with()
        res = e.rest()
        low = res["message"].lower()
        for leak in ("bandage", "poultice", "flint", "speere", "speer",
                     "faser", "holz", "feuerholz", "schlinge", "snare"):
            assert leak not in low

    def test_rest_reports_world_messages_not_silent(self):
        """Weltzustands-Meldungen (UNTERKÜHLUNG/FIRE_OUT) bleiben sichtbar —
        Rast ist keine Hint-freie Blase."""
        e = engine_with()
        e.travel("mountain_peak")
        e.tick_counter = 132  # 22:00 → Nacht
        e.current_weather = "CLEAR"
        res = e.rest()
        assert res["success"] is True
        if e.player.body_temp < 35.0:  # Meldung, wenn zutreffend (Probe: ja)
            assert "UNTERKÜHLUNG" in res["message"]
