"""Tests für SPEC-014 — Feuer-Wartung lesbar machen: Kälte- und Brennstoff-Signale.

Crossing-basierte, generische richtungsgebende Meldungen in `_advance_time`:
Kälte-Warnung (bt < 36.0, nur ohne aktives Feuer, Guard >= 35.0 gegen
UNTERKÜHLUNG-Doppel) + Feuer-schwach (fire_fuel < 8.0 = weniger als ein
STOKE_FUEL, Lead-Zeit ~8 Ticks vor FIRE_OUT). Konstanten, keine neuen
RNG-Würfe, kein Leak (TAG_LABELS-Vokabelklasse), kein Reason-Code-Eingriff.
"""
import random

import pytest

from engine.core import (GameEngine, COLD_HINT_TEXT, COLD_WARN_THRESHOLD,
                         FIRE_DYING_HINT_TEXT, FIRE_LOW_FUEL)


def _fresh_engine():
    """Engine am Waldrand (base_temp 15.0), tick 36 (6 Uhr, Tagesstart)."""
    return GameEngine()


def _ticks(game, n):
    """n Ticks Vorlauf; Rückgabe: Liste von Log-Zeilen-Listen (eine je Tick)."""
    blocks = []
    for _ in range(n):
        msg = game._advance_time(1)
        blocks.append(msg.split("\n") if msg else [])
    return blocks


def _flat(blocks):
    return [line for block in blocks for line in block]


def _dying_lines(blocks):
    return [l for l in _flat(blocks) if FIRE_DYING_HINT_TEXT in l]


def _cold_lines(blocks):
    return [l for l in _flat(blocks) if COLD_HINT_TEXT in l]


# ---------------------------------------------------------------------------
# Kälte-Warnung: Crossing < 36.0, nur ohne aktives Feuer, Guard >= 35.0
# ---------------------------------------------------------------------------

class TestColdWarning:
    def test_cold_warning_fires_exactly_once_per_falling_pass(self):
        """bt fällt einmal durch 36.0: exakt EINE Kälte-Zeile, danach keine
        weitere, solange bt unter der Schwelle bleibt (kein Spam)."""
        g = _fresh_engine()
        g.current_weather = "CLEAR"
        g.player.body_temp = 40.0
        # bt-Drift: (40-15)*0.01*0.5 ≈ 0.125/tick → Crossing nach ~32 Ticks.
        colds = _cold_lines(_ticks(g, 80))
        assert len(colds) == 1, (
            f"Kälte-Warnung soll genau 1x pro fallendem Durchgang feuern, war {len(colds)}x"
        )

    def test_cold_warning_only_without_active_fire(self):
        """Fire-Gate: mit aktivem Feuer am Ort keine Kälte-Warnung (der Text
        'Ein Feuer würde hier Wärme geben' wäre eine Lüge)."""
        g = _fresh_engine()
        g.current_weather = "CLEAR"
        loc = g.current_location
        loc.fire_active = True
        loc.fire_fuel = 100.0
        g.player.body_temp = 40.0
        blocks = _ticks(g, 80)
        # Feuer brennt durch (100 Ticks > 80), wärmt (FIRE_HEAT 40 → eff. 55):
        # bt steigt Richtung 55 → UNTERKÜHLUNG nie, Kälte-Warnung nie.
        assert _cold_lines(blocks) == [], \
            "Mit aktivem Feuer darf die Kälte-Warnung nicht feuern"
        assert not any("UNTERKÜHLUNG" in l for l in _flat(blocks))
        assert loc.fire_active  # Setup-Verifikation: Feuer brannte durch

    def test_cold_warning_guard_below_pain_threshold(self):
        """Fallender Crossing in einem Tick, der bt auch unter 35.0 zieht:
        UNTERKÜHLUNG spricht — die Warnung nicht ebenfalls (Guard >= 35.0)."""
        g = _fresh_engine()
        g.current_weather = "SNOW"  # -15 °C → drift ≈ 0.365/tick bei bt 36.5
        g.player.body_temp = 36.5
        blocks = _ticks(g, 8)
        pain_idx = [i for i, b in enumerate(blocks)
                    if any("UNTERKÜHLUNG" in l for l in b)]
        cold_idx = [i for i, b in enumerate(blocks)
                    if any(COLD_HINT_TEXT in l for l in b)]
        assert pain_idx, "Setup: bt sollte unter 35.0 fallen (UNTERKÜHLUNG)"
        # Kein Doppel: Warnung und UNTERKÜHLUNG nie im selben Tick.
        assert not (set(cold_idx) & set(pain_idx)), \
            "Crossing-Tick, der unter 35.0 fällt, gehört der UNTERKÜHLUNG"
        # Und: unterhalb der Schmerzgrenze feuert keine Warnung mehr.
        if cold_idx:
            assert max(cold_idx) < min(pain_idx), \
                "Warnung feuert vor der Schmerzgrenze, nicht danach"

    def test_cold_warning_rearms_after_rewarming(self):
        """Re-Wärmen über die Schwelle + erneutes Abkühlen: zweite Warnung
        (einmal pro fallendem Durchgang, nicht einmal pro Spiel)."""
        g = _fresh_engine()
        g.current_weather = "CLEAR"
        g.player.body_temp = 40.0
        assert len(_cold_lines(_ticks(g, 80))) == 1
        g.player.body_temp = 40.0  # Re-Wärmen (synthetisch, über Schwelle)
        assert len(_cold_lines(_ticks(g, 80))) == 1, \
            "Nach Re-Wärmen feuert die Warnung im neuen Durchgang erneut (1x)"

    def test_cold_warning_is_constant_text_no_rng(self):
        """Konstanter Text, keine neuen Würfe: zwei identisch geseedete Läufe
        erzeugen identische Log-Sequenzen, Warnung exakt 1x mit exaktem Text."""
        runs = []
        for _ in range(2):
            random.seed(123456)
            g = _fresh_engine()
            g.player.body_temp = 40.0
            runs.append(_flat(_ticks(g, 60)))
        assert runs[0] == runs[1], "Determinismus: identische Seeds → identische Logs"
        warns = [l for l in runs[0] if COLD_HINT_TEXT in l]
        assert warns == [COLD_HINT_TEXT], (
            f"Erwartet exakt die Konstante 1x, bekommen: {warns!r}"
        )


# ---------------------------------------------------------------------------
# Feuer-schwach: Crossing < 8.0 bei aktivem Feuer und fire_fuel > 0
# ---------------------------------------------------------------------------

class TestFireDyingHint:
    def test_fire_dying_fires_once_per_falling_pass(self):
        """Fuel fällt einmal durch 8.0: exakt eine Feuer-schwach-Zeile,
        ~8 Ticks vor FIRE_OUT, danach bis zum Re-Auffüllen keine weitere."""
        g = _fresh_engine()
        loc = g.current_location
        loc.fire_active = True
        loc.fire_fuel = 20.0
        blocks = _ticks(g, 30)
        dying = _dying_lines(blocks)
        fire_out = [l for l in _flat(blocks) if "FIRE_OUT" in l]
        assert len(dying) == 1, (
            f"Feuer-schwach soll genau 1x feuern, war {len(dying)}x"
        )
        assert len(fire_out) == 1
        # Lead-Zeit: die Andeutung kommt vor FIRE_OUT (FIRE_LOW_FUEL = 8.0).
        assert _flat(blocks).index(dying[0]) < _flat(blocks).index(fire_out[0]), \
            "Feuer-schwach muss vor FIRE_OUT kommen"

    def test_no_dying_hint_in_fire_out_tick(self):
        """Kippt der Fuel-Tick direkt auf 0 (FIRE_OUT), spricht nur die ehrliche
        FIRE_OUT-Meldung — die Andeutung ('am Leben halten') wäre eine Lüge:
        stoke_fire braucht ein aktives Feuer."""
        g = _fresh_engine()
        loc = g.current_location
        loc.fire_active = True
        loc.fire_fuel = 1.0  # kippt im nächsten Tick direkt auf 0
        lines = _ticks(g, 1)[0]
        assert any("FIRE_OUT" in l for l in lines), \
            "Setup: Feuer sollte in diesem Tick erlöschen"
        assert not any(FIRE_DYING_HINT_TEXT in l for l in lines), \
            "Im FIRE_OUT-Tick darf die Andeutung nicht erscheinen (Lüge)"

    def test_dying_hint_only_when_crossing_below_threshold(self):
        """Fuel fällt nicht durch die Schwelle (12 → 7 mit Tick 5, dann
        unter 8 bleibend): genau eine Andeutung, kein Dauertext danach."""
        g = _fresh_engine()
        loc = g.current_location
        loc.fire_active = True
        loc.fire_fuel = 12.0
        blocks = _ticks(g, 12)  # 12 → 0 (FIRE_OUT bei Tick 12)
        dying = _dying_lines(blocks)
        assert len(dying) == 1, (
            f"Ein fallender Durchgang = eine Andeutung, war {len(dying)}x"
        )

    def test_dying_hint_rearms_after_refuel(self):
        """Nachlegen über die Schwelle + erneutes Abfallen: zweite Andeutung."""
        g = _fresh_engine()
        loc = g.current_location
        loc.fire_active = True
        loc.fire_fuel = 20.0
        assert len(_dying_lines(_ticks(g, 15))) == 1  # fällt durch 8, feuert 1x
        loc.fire_fuel = 20.0  # Nachlegen (synthetisch, über die Schwelle)
        assert len(_dying_lines(_ticks(g, 15))) == 1, \
            "Nach Neu-Auffüllen feuert die Andeutung im neuen Durchgang erneut (1x)"


# ---------------------------------------------------------------------------
# Leak-frei-Regression: Vokabelklasse, kein Item/Menge/Prozess/Reason
# ---------------------------------------------------------------------------

class TestNoLeak:
    LEAKS = ("stick", "log_oak", "kindling", "tinder", "wood",
             "Holz", "Zunder", "Reisig",
             "start_fire", "stoke_fire",
             "Rezept", "1x", "2x", "Menge")

    def test_cold_hint_text_has_no_leak(self):
        for leak in self.LEAKS:
            assert leak not in COLD_HINT_TEXT, f"Leak {leak!r} in Kälte-Warnung"

    def test_dying_hint_text_has_no_leak(self):
        for leak in self.LEAKS:
            assert leak not in FIRE_DYING_HINT_TEXT, f"Leak {leak!r} in Feuer-schwach"


# ---------------------------------------------------------------------------
# Konstanten-Vertrag (Spec: exakt die geforderten Werte)
# ---------------------------------------------------------------------------

class TestConstants:
    def test_threshold_values_match_spec(self):
        assert COLD_WARN_THRESHOLD == 36.0   # 1° über Schmerzgrenze → Lead-Zeit
        assert FIRE_LOW_FUEL == 8.0          # weniger als ein STOKE_FUEL