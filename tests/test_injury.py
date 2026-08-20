"""Tests für SPEC-009 — Verletzung & Heilung (Engine-Mechanik).

Deckt die Akzeptanzkriterien ab: persistenter Wund-Zustand (cut blutet über
Zeit, strain = Effort-Malus), handlungsgebundene Entstehung (exponiertes
Sammeln / scharfe Materialien), Behandlung als Prozess (make_bandage/
make_poultice + treat_cut/treat_strain), Behandlung + Ruhe heilt (unbehandelt
nicht), kein Rezept-Leak im Wund-Text.
"""
import pytest
from engine.core import GameEngine
from data.items import create_item


def engine_with(items=()):
    e = GameEngine()
    for tid, qty in items:
        e.player.inventory.add(create_item(tid, qty))
    return e


class TestWoundState:
    def test_cut_bleeds_over_time_untreated(self):
        e = engine_with()
        e.player.injuries["cut"] = {"severity": 1.0, "ticks": 0, "treated": False}
        hp0 = e.player.hp
        e._advance_time(5)
        # unbehandelt: blutet 0.2 HP/Tick → 5 Ticks = 1.0 HP
        assert e.player.hp == pytest.approx(hp0 - 5 * 0.2)
        assert "cut" in e.player.injuries  # Zustand bleibt bestehen

    def test_treated_cut_stops_bleeding(self):
        e = engine_with()
        e.player.injuries["cut"] = {"severity": 1.0, "ticks": 0, "treated": True}
        hp0 = e.player.hp
        e.travel("hidden_cave")  # shelter: behandelt + Rast → heilt, blutet nicht
        e._advance_time(5)
        # treat: keine Blutung mehr (kein 5×0.2=1.0 HP-Verlust); nur unwesentliche
        # Kälte-Neuberechnung denkbar, darum grosszügige Toleranz.
        assert e.player.hp >= hp0 - 0.5

    def test_strain_is_effort_malus(self):
        e = engine_with()
        assert e._injury_effort_malus() == 0.0
        e._inflict("strain")
        assert e._injury_effort_malus() == 1.0  # unbehandelt → Extra-Effort
        e.player.injuries["strain"]["treated"] = True
        assert e._injury_effort_malus() == 0.0  # behandelt → Malus weg


class TestInjurySource:
    def test_gathering_exposed_peak_inflicts(self):
        """Sammeln am exponierten Gipfel (exposure 1.0) mit scharfem Fund kann
        verletzen — Quelle ist Handeln, kein globaler Timer. (injuries_rng auf
        0.0 gezwungen → jeder Wurf feuert; Fund sicher via chance 1.0.)"""
        e = engine_with()
        e.travel("mountain_peak")
        for node in e.current_location.nodes:
            node.stock = node.max_stock
            node.chance = 1.0
        e.injuries_rng.random = lambda: 0.0
        e.gather()
        assert e.player.injuries, "Sammeln am exponierten Ort muss verletzen können"
        # Zerrung: Exposure ≥ 0.8 trifft bei jedem Erfolg
        assert "strain" in e.player.injuries

    def test_inflict_does_not_stack(self):
        e = engine_with()
        assert e._inflict("cut") is True
        assert e._inflict("cut") is False  # schon aktiv → kein Stapeln
        assert e.player.injuries["cut"]["severity"] == 1.0


class TestHealing:
    def test_untreated_wound_never_heals(self):
        e = engine_with()
        e._inflict("cut")
        e.travel("hidden_cave")  # geschützter Rast-Ort, aber UNBEHANDELT
        e._advance_time(60)
        assert "cut" in e.player.injuries, "unbehandelt heilt nicht"

    def test_treated_heals_only_with_rest(self):
        e = engine_with()
        e.player.injuries["cut"] = {"severity": 1.0, "ticks": 0, "treated": True}
        # behandelt, aber NICHT rastend (Gipfel, kein Feuer) → kein Heilen
        e.travel("mountain_peak")
        e.current_weather = "CLEAR"
        e._advance_time(5)
        assert "cut" in e.player.injuries
        # behandelt + Ruhe am Feuer → heilt (Feuer über das Heilfenster halten;
        # sonst brennt ein einzelner _advance_time(25)-Chunk den Brennstoff weg,
        # bevor der Heil-Check läuft — im Spiel stokt der Spieler nach).
        e.travel("forest_edge")
        e._light_fire()
        e.current_location.fire_fuel = 500
        e._advance_time(25)
        assert "cut" not in e.player.injuries


class TestTreatmentProcess:
    def test_make_bandage_then_treat_stops_bleed(self):
        e = engine_with([("plant_fiber", 4)])
        e._inflict("cut")
        assert e.execute_process("make_bandage")["success"] is True
        res = e.execute_process("treat_cut")
        assert res["success"] is True
        assert e.player.injuries["cut"]["treated"] is True

    def test_treat_without_wound_does_not_consume(self):
        e = engine_with([("plant_fiber", 4)])
        e.execute_process("make_bandage")  # 1 Verband vorhanden
        assert e._count_template("bandage") == 1
        res = e.execute_process("treat_cut")  # keine Wunde
        assert res["success"] is False
        assert res["reason"] == "NO_INJURY"
        assert e._count_template("bandage") == 1  # nicht verbraucht

    def test_make_poultice_then_treat_strain(self):
        e = engine_with([("mushroom", 1), ("clay_lump", 1)])
        e._inflict("strain")
        assert e.execute_process("make_poultice")["success"] is True
        res = e.execute_process("treat_strain")
        assert res["success"] is True
        assert e.player.injuries["strain"]["treated"] is True

    def test_no_recipe_leak_in_injury_text(self):
        from engine.core import _feedback_message
        for msg in (_feedback_message("BLEEDING"), _feedback_message("INJURED"),
                    _feedback_message("HEALED")):
            low = msg.lower()
            assert "bandage" not in low and "poultice" not in low
            assert "pflanzenfaser" not in low and "tonklumpen" not in low
