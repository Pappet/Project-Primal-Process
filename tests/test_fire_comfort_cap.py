"""Tests für T1 — B11: Feuer-Komfort-Cutoff (HITZSCHLAG-Falle).

Befund (Play 11.09. + 14.09., re-verifiziert): am aktiven Feuer asymptotiert
`body_temp` gegen `ambient + FIRE_HEAT` (Tag 55 / Nacht 45) — über die
HITZSCHLAG-Grenze 40.0 hinweg. Purer Rest-Loop am 500-fuel-Feuer: 20/20 Tode
exakt @Rest#34 (bt_end 43.3). „Am Feuer ausharren" ist DIE nahegelegte
Antwort auf den Nacht-Bogen (SPEC-015) und tötet ohne richtungsgebendes
Signal.

Fix (T1, Engine-only): `FIRE_COMFORT_CAP = 38.0` — am aktiven Feuer wird
`effective_ambient` auf den Cap gecappt (`min(effective_ambient, CAP)`,
gewired an `fire_warmth > 0`). OHNE Feuer kein Cap — Kälte-Physik unangetastet
(exakt die Zwei-Fälle-Trennung testet test_cap_grips_only_at_fire). Kein
neuer RNG-Wurf, kein Data-Touch, kein Reason-Code, kein Warn-Text.
"""

import random

import pytest

from engine.core import FIRE_COMFORT_CAP, GameEngine, REST_TICKS

# 20 Scorecard-Seeds — exakt die Regression aus Play 14.09. (P1-Probe).
SEEDS = tuple(20260803 + i for i in range(20))


def engine_at_fire(fuel=500.0):
    """Engine am Waldrand-Feuer mit sattem Brennstoff (B11-Setup)."""
    e = GameEngine()
    e.travel("forest_edge")
    e._light_fire()
    e.current_location.fire_fuel = fuel
    return e


class TestB11Regression:
    """Akzeptanz R1/R2: der reine Rest-Loop stirbt nicht mehr — und bt
    pendelt im Komfortfenster (kein untoter Zustand über 40)."""

    def test_rest_loop_500_fuel_60_rests_20_seeds_zero_deaths(self):
        for seed in SEEDS:
            random.seed(seed)
            e = engine_at_fire()
            for _ in range(60):
                e.rest()
                assert e.player.hp > 0, (
                    f"seed {seed}: Tod im Rest-Loop — B11 nicht gefixt")
            # Satter Brennstoff: Feuer muss die volle Regression halten
            assert e.current_location.fire_active is True

    def test_body_temp_stays_below_heatstroke_threshold(self):
        """Kein untoter Zustand: Wärme-Gewinn endet UNTER der 40.0-Grenze —
        bt pendelt im Komfortfenster [35, 40) statt > 40 zu asymptotieren."""
        e = engine_at_fire()
        e.current_weather = "CLEAR"
        for _ in range(60):
            e.rest()
            assert e.player.body_temp < 40.0
        # und es bleibt warm: keinesfalls unter die Kälte-Schwelle gerutscht
        assert e.player.body_temp >= 35.0

    def test_body_temp_converges_toward_cap_not_above(self):
        """Mit Start nahe am Cap bleibt bt am Cap-Soller — der SOLL-WERT der
        Wärme-Dynamik am Feuer ist der Cap (38.0), nicht ambient+FIRE_HEAT."""
        e = engine_at_fire()
        e.current_weather = "CLEAR"
        e.tick_counter = 60  # Tag (kein night_mod) — deterministisches Setup
        for _ in range(40):
            e.rest()
        # unter der HITZSCHLAG-Grenze geblieben, dicht am Cap
        assert e.player.body_temp < 40.0
        assert e.player.body_temp > 37.0


class TestTwoCaseSplit:
    """Akzeptanz R3: der Cap greift NUR am Feuer — die Kälte-Seite (ohne
    Feuer) bleibt byte-unangetastet ehrlich tödlich."""

    def test_cap_grips_only_at_fire(self):
        """Nacht ohne Feuer: bt fällt Richtung kalter Ambient (2.0) — das Cap
        darf die Kälte-Physik nicht berühren (bt klemmt NICHT an 38)."""
        e = GameEngine()
        e.travel("mountain_peak")  # base_temp 2.0, Nacht-Mod −10
        e.current_weather = "CLEAR"
        e.tick_counter = 132  # 22:00 → Nacht (hour 3 < 6)
        bt0 = e.player.body_temp
        for _ in range(6):
            e.rest()
        assert e.player.body_temp < bt0
        assert e.player.body_temp < 35.0   # UNTERKÜHLUNG läuft ehrlich
        # Das Cap hat NICHT geklemmt: ohne Feuer wäre jede Klemmung ein
        # Kälte-Bug — bt muss unter dem Cap weit Richtung ambient fallen.
        assert e.player.body_temp < 34.0

    def test_cap_value_sits_in_comfort_window(self):
        """Konstanten-Vertrag: unter HITZSCHLAG (40.0), über Kälte (35.0)."""
        assert FIRE_COMFORT_CAP == 38.0


class TestStreamDiscipline:
    """Akzeptanz R4: keine neuen RNG-Würfe — der Cap ist eine reine
    min-Klemme in der bestehenden Wärmezeile."""

    def test_no_draws_beyond_weather_crossings(self):
        e = engine_at_fire()
        e.tick_counter = 36  # % 12 != 0 → nächstes _advance_time würfelt nicht
        e.current_weather = "CLEAR"
        state0 = random.getstate()
        e.rest()
        assert random.getstate() == state0

    def test_long_rest_loop_draw_free_outside_crossings(self):
        e = engine_at_fire()
        e.current_weather = "CLEAR"
        # Crossing-freies Fenster: von Tick 37 bis 143 würfelt % 12 nie
        # (die Rasten enden vor 144) — getstate muss unberührt bleiben.
        e.tick_counter = 37
        state0 = random.getstate()
        for _ in range(26):  # 26 × 4 = 104 Ticks → endet bei Tick 141 < 144
            e.rest()
        assert random.getstate() == state0


class TestIntegrationWithExistingSystems:
    """Kein Regressions-Drag auf SPEC-014/FIRE_OUT/Heil-Kette: der Cap
    hängt nur an `fire_warmth > 0` und berührt die Restpfade nicht."""

    def test_fire_out_mid_rest_still_honest(self):
        """Brennstoff kippt in der Rast: fire_warmth wird 0 → kein Cap, die
        ehrliche FIRE_OUT-Meldung bleibt, Kälte nimmt ihren Lauf."""
        e = engine_at_fire(fuel=2.0)
        e.current_weather = "CLEAR"
        res = e.rest()
        assert e.current_location.fire_active is False
        assert "FIRE_OUT" in res["message"]

    def test_cold_hint_fires_during_rest_without_fire(self):
        """SPEC-014-Kälte-Warnung feuert weiter (ohne Feuer, fallend unter
        36.0) — der Cap-Guard leert sich mit fire_warmth."""
        e = GameEngine()
        e.travel("mountain_peak")
        e.tick_counter = 132  # Nacht
        e.current_weather = "CLEAR"
        res = e.rest()
        assert e.player.body_temp < 36.0
        assert "UNTERKÜHLUNG" in res["message"]

    def test_treated_wound_still_heals_at_fire(self):
        """Heil-Kette (_resting_warm liest _fire_lit, nicht bt) bleibt intakt."""
        e = engine_at_fire()
        e.player.injuries["cut"] = {"ticks": 0, "treated": True,
                                    "severity": 1.0}
        for _ in range(5):
            e.rest()
        assert "cut" not in e.player.injuries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
