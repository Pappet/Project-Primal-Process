"""Tests für SPEC-016 — Glut: der Feuerort erinnert sich (Ortsbindung).

Befund (Research-Explore 17.09.): FIRE_OUT löscht den Feuerort byte-identisch
mit Neuland — die Welt hat kein Gedächtnis für die Arbeit des Spielers. Der
28.08.-Befund (Reparatur nach Kollaps strikt schlechter, 19/20 vs. 12/20)
zeigt das Loch: der eine Ort mit beisammen-gewesener Infrastruktur bewertet
als Jungfrau-Terrain. fire_pit (KINDLING, wird nie verbrannt) ist der stille
Beleg der Design-Absicht „Feuerstelle als Ort".

Mechanik (UnReal World / Don't Starve / TLD): FIRE_OUT hinterlässt Glut
(LocationDef.embers = EMBER_RESIDUE); Verfall 0.1/Tick (~60-Ticks-Fenster);
Re-Zündung am Glut-Ort braucht 1× WOOD — tinder/stick (die volle Zünd-Kette)
ausdrücklich NICHT. Unter EMBER_REVIVE_MIN ist der Ort wieder Neuland.
Kein Data-Touch, keine neuen RNG-Würfe (getstate-Assertion), start_fire
unangetastet.
"""

import random

import pytest

from engine.core import (
    EMBER_DECAY_PER_TICK,
    EMBER_RESIDUE,
    EMBER_REVIVE_MIN,
    GameEngine,
)
from data.items import create_item


def engine_with(items=()):
    e = GameEngine()
    for tid, qty in items:
        e.player.inventory.add(create_item(tid, qty))
    return e


def burn_out(e, fuel=1.0):
    """Ein Feuer am Waldrand, das im nächsten Tick erlischt."""
    e.travel("forest_edge")
    e._light_fire()
    e.current_location.fire_fuel = fuel
    e.rest()  # läuft über _advance_time — FIRE_OUT dort
    return e


class TestEmbersFromFireOut:
    """Akzeptanz 1: Glut entsteht nur aus FIRE_OUT; Verfall deterministisch."""

    def test_active_fire_has_no_embers(self):
        e = engine_with()
        e.travel("forest_edge")
        e._light_fire()
        assert e.current_location.embers == 0.0

    def test_fresh_engine_location_has_no_embers(self):
        assert GameEngine().current_location.embers == 0.0

    def test_fire_out_leaves_ember_residue(self):
        e = burn_out(engine_with())
        loc = e.current_location
        assert loc.fire_active is False
        assert loc.embers == pytest.approx(EMBER_RESIDUE)

    def test_decay_deterministic_per_tick(self):
        e = burn_out(engine_with())
        loc = e.current_location
        base = loc.embers
        random.seed(1)
        e.rest()  # REST_TICKS Ticks — reine Verfalls-Zeit
        assert loc.embers == pytest.approx(
            max(0.0, base - EMBER_DECAY_PER_TICK * 4))
        # Verfall-Fenster (RESIDUE/DECAY = 60 Ticks = 15 Rests à 4) läuft leer
        for _ in range(15):
            e.rest()
        assert loc.embers == 0.0

    def test_zero_embers_is_virgin_terrain_again(self):
        """Bei 0 ist der Ort byte-identisch mit nie-befeuerter Location."""
        e2 = engine_with()
        e2.travel("forest_edge")
        e2.current_location.embers = 0.3  # weniger als ein Rest-Fenster Verfall
        random.seed(3)
        e2.rest()
        assert e2.current_location.embers == 0.0

    def test_full_start_fire_swallows_embers(self):
        """Volles start_fire setzt den Glut-Zustand zurück (kein Cross-Over)."""
        e = engine_with()
        e.travel("forest_edge")
        e.current_location.embers = EMBER_RESIDUE
        e._light_fire()
        assert e.current_location.embers == 0.0


class TestReviveNeedsWoodOnly:
    """Akzeptanz 2: Re-Zündung aus Glut braucht WOOD, nicht die Zünd-Kette."""

    def test_revive_with_wood_only(self):
        """tinder ausdrücklich NICHT nötig — Gegenprobe mit leerem tinder-Konto."""
        e = engine_with([("stick", 1)])  # stick trägt WOOD; kein tinder im Inventar
        e.travel("forest_edge")
        e.current_location.embers = EMBER_RESIDUE
        random.seed(4)
        res = e.stoke_fire()
        assert res["success"] is True
        loc = e.current_location
        assert loc.fire_active is True
        # EMBER_RESIDUE abzüglich des einen Zeit-Ticks, den die Re-Zündung
        # kostet (das neue Feuer brennt schon, während die Zeit vergeht).
        assert loc.fire_fuel == pytest.approx(EMBER_RESIDUE - 1.0)
        assert loc.embers == 0.0  # Glut in das Feuer übergegangen
        assert e._count_template("stick") == 0  # 1× WOOD verbraucht

    def test_revive_without_wood_is_missing_fuel(self):
        """KINDLING (tinder) allein zündet die Glut NICHT — Zünd-Kette bleibt."""
        e = engine_with([("tinder", 2)])
        e.travel("forest_edge")
        e.current_location.embers = EMBER_RESIDUE
        res = e.stoke_fire()
        assert res["success"] is False
        assert res["reason"] == "MISSING_FUEL"
        assert e.current_location.fire_active is False
        assert e._count_template("tinder") == 2  # nichts verbraucht

    def test_below_min_is_no_fire(self):
        """Ohne Glut: NO_FIRE-Pfad bleibt — kein Autokast."""
        e = engine_with([("stick", 1)])
        e.travel("forest_edge")
        e.current_location.embers = EMBER_REVIVE_MIN - 0.01
        res = e.stoke_fire()
        assert res["success"] is False
        assert res["reason"] == "NO_FIRE"
        assert e._count_template("stick") == 1  # unangetastet


class TestEmberWindow:
    """Akzeptanz 3: das Glut-Fenster ist endlich und lesbar."""

    def test_window_is_finite_about_60_ticks(self):
        window = EMBER_RESIDUE / EMBER_DECAY_PER_TICK
        assert window == pytest.approx(60.0)

    def test_revive_impossible_after_window(self):
        e = engine_with([("stick", 1)])
        e.travel("forest_edge")
        e.current_location.embers = 0.5  # unter MIN — Fenster verstrichen
        res = e.stoke_fire()
        assert res["reason"] == "NO_FIRE"


class TestAllPathsThroughTick:
    """Akzeptanz 4: Verfall hängt an _advance_time — Rast/Reisen verdringen
    die Glut gleichermaßen (Nacht ohne Feuer tickt das Fenster ehrlich)."""

    def test_rest_decays_embers(self):
        e = burn_out(engine_with())
        loc = e.current_location
        base = loc.embers
        random.seed(5)
        e.rest()
        assert loc.embers < base

    def test_travel_away_then_back_keeps_window_ticking(self):
        """Glut ist Zustand am Ort — sie verfällt auch, während man woanders ist."""
        e = burn_out(engine_with())
        embers_at_leave = e.current_location.embers
        random.seed(6)
        e.travel("hidden_cave")
        e.rest()
        e.travel("forest_edge")
        assert e.current_location.embers < embers_at_leave


class TestNoNewRandomDraws:
    """Akzeptanz 5: keine neuen RNG-Würfe (Verfall deterministisch, Revive
    ist Gütercheck + Zustandswechsel) — getstate-Assertion, Muster
 test_fire_comfort_cap.py."""

    def test_decay_window_draws_nothing(self):
        random.seed(7)
        e = burn_out(engine_with())
        state = random.getstate()
        for _ in range(5):
            e.rest()
        assert random.getstate() == state

    def test_revive_draws_nothing(self):
        random.seed(8)
        e = engine_with([("stick", 1)])
        e.travel("forest_edge")
        e.current_location.embers = EMBER_RESIDUE
        state = random.getstate()
        e.stoke_fire()
        assert random.getstate() == state


class TestGuardsUntouched:
    """Akzeptanz 6 (struktur): start_fire-Kette unangetastet — ein volles
    start_fire braucht nach wie vor tinder+stick (Prozess-Inputs), Glut ist
    die gelernte Verkürzung, nicht der Default."""

    def test_ember_constants_are_engine_level(self):
        """Konstanten ohne Text: kein Rezept-Leak (RESIDUE/MIN sind Ticks-
        Äquivalente, keine Item-Namen)."""
        assert EMBER_RESIDUE == 6.0
        assert EMBER_REVIVE_MIN == 1.0
        assert EMBER_DECAY_PER_TICK == 0.1
