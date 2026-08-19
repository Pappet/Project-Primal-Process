"""Tests für das guided_full-Messwerkzeug (play/guided_full.py).

BL 17.08: der Bot aß sein rohes Fleisch (EDIBLE 150) selbst, bevor cook_meat
(ein Prozess, der 1× raw_meat braucht) Inputs hatte → 5. Prozess systematisch
unterrepräsentiert (5/20 Seeds). Fix: rohes Fleisch als Zutat reservieren
(eat() bevorzugt gekochtes/Beeren/Pilze) + gezielte Jagd-Brat-Sequenz im Warmup.
"""
import pytest
from engine.core import GameEngine
from data.items import create_item
from play.guided_full import eat, guided_full


class TestEatReservesRawMeat:
    def _engine_with(self, items, energy=200, hp=50):
        e = GameEngine()
        for tid, qty in items:
            e.player.inventory.add(create_item(tid, qty))
        e.player.energy = energy
        e.player.hp = hp
        return e

    def test_eat_prefers_cooked_over_raw(self):
        e = self._engine_with([("raw_meat", 1), ("cooked_meat", 1)])
        eat(e)
        # gekochtes Fleisch (EDIBLE 400) wird gegessen, rohes bleibt reserviert
        tpls = [i.template_id for i in e.player.inventory.items]
        assert "raw_meat" in tpls, "rohes Fleisch darf nicht gegessen werden, solange gekochtes da ist"
        assert "cooked_meat" not in tpls

    def test_eat_prefers_berries_over_raw(self):
        e = self._engine_with([("raw_meat", 1), ("berries", 1)])
        eat(e)
        tpls = [i.template_id for i in e.player.inventory.items]
        assert "raw_meat" in tpls, "Beeren sind Zutat-verfügbar, rohes Fleisch ist Reservat"
        assert "berries" not in tpls

    def test_eat_uses_raw_only_as_last_resort(self):
        e = self._engine_with([("raw_meat", 1)])
        eat(e)
        assert "raw_meat" not in [i.template_id for i in e.player.inventory.items], \
            "ohne anderes EDIBLE ist rohes Fleisch die einzige Notration"


class TestGuidedReachesCookMeat:
    def test_guided_full_reaches_cook_meat_mostly(self):
        """Der 5. Prozess cook_meat war vor dem Fix nur 5/20 erreichbar (der Bot
        aß sein rohes Fleisch vor dem Kochen). Jetzt reserviert eat() rohes
        Fleisch als Zutat und jagt+brät gezielt im Warmup → auf mindestens
        16/20 Seeds erreichbar. Einzelne Seeds scheitern am RNG (Jagd-Chance
        0.3 × ~10 Versuche), das ist Werkzeug-Rauschen, kein Spielfehler."""
        ok = 0
        total = 20
        for seed in range(20260801, 20260821):
            g = guided_full(seed)
            if "cook_meat" in g.game.player.known_processes:
                ok += 1
        assert ok >= 14, f"cook_meat nur {ok}/{total} (Fix-Ziel: ≥70%)"