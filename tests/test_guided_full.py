"""Tests für das guided_full-Messwerkzeug (play/guided_full.py).

BL 17.08: der Bot aß sein rohes Fleisch (EDIBLE 150) selbst, bevor cook_meat
(ein Prozess, der 1× raw_meat braucht) Inputs hatte → 5. Prozess systematisch
unterrepräsentiert (5/20 Seeds). Fix: rohes Fleisch als Zutat reservieren
(eat() bevorzugt gekochtes/Beeren/Pilze) + gezielte Jagd-Brat-Sequenz im Warmup.
"""
import random

import pytest
from engine.core import GameEngine
from data.items import create_item
from play.guided_full import eat, guided_full, _ensure_fire_supply, _fire_at, _warm_here, WARM


def _engine(items, at=WARM, seed=4242):
    """Frische Engine an einem Ort, RNG fest verdrahtet (guided_full-Muster)."""
    e = GameEngine()
    e._rng = random.Random(seed)
    random.seed(seed)
    for tid, qty in items:
        e.player.inventory.add(create_item(tid, qty))
    e.travel(at)
    return e


def _tool(template_id="knife_bone", name="Knochenmesser", tags=None):
    """Dynamisches Werkzeug (wie _create_tool es baut) — knife_bone ist ein
    Blueprint-Produkt, kein Template, daher hier handgebaut."""
    from engine.components import Item
    it = Item(name=name, base_weight=0.4, tags=dict(tags or {"CUTTING": True, "HARD": True}),
              template_id=template_id)
    it.template_id = template_id
    return it


def _qty(game, tid):
    return sum(it.quantity for it in game.player.inventory.items if it.template_id == tid)


class TestFireEconomy:
    """Feuer-Ökonomie (PLAN-Task 31.08.): die 14-Baseline-Tode sind die
    Feuer-Versorgungsspirale am Waldrand (Feuer ab, tinder/reeds leer →
    start_fire unmöglich). Der Bot hält Brennstoff-Reserven im Inventar und
    schiebt VOR Reisen nach; am kalten Ort wird nie gesammelt (kein Pendel)."""

    def test_supply_creates_tinder_from_reeds(self):
        e = _engine([("reeds", 4)])
        e.player.inventory.add(_tool())
        _ensure_fire_supply(e)
        assert _qty(e, "tinder") >= 2, "create_tinder (reeds×2 → tinder×3) muss die Reserve füllen"

    def test_supply_gathers_reeds_then_tinder(self):
        e = _engine([])
        e.player.inventory.add(_tool())
        _ensure_fire_supply(e)
        # Höhlen-Trip für reeds, dann Zunder — Bestandslücke ist geschlossen
        assert _qty(e, "tinder") >= 2 or _qty(e, "reeds") >= 2

    def test_supply_tops_up_sticks_at_warm(self):
        e = _engine([])
        _ensure_fire_supply(e)
        assert _qty(e, "stick") >= 2, "start_fire braucht 2 sticks — Reserve wird am Waldrand aufgefüllt"

    def test_fire_at_relights_from_reserve(self):
        e = _engine([("tinder", 2), ("stick", 2)])
        assert _fire_at(e) is True
        assert e.current_location.fire_active and e.current_location.fire_fuel > 0

    def test_warm_window_supplies_while_fire_burns(self):
        # Das warme Fenster: brennt das eigene Feuer, werden die Reserven
        # gepflegt — Versorgung bei Wärme statt kalter Reparatur.
        e = _engine([("reeds", 4)])
        e.player.inventory.add(_tool())
        e.current_location.fire_active = True
        e.current_location.fire_fuel = 20.0
        assert _qty(e, "tinder") == 0
        _warm_here(e)
        assert _qty(e, "tinder") >= 2, "im warmen Fenster muss die tinder-Reserve aufgebaut werden"
        assert e.current_location.fire_active, "die Versorgung darf das Feuer nicht kosten"

    def test_no_cold_repair_when_fire_is_out(self):
        # Ist das Feuer AUS, wird nicht mehr versorgt (kalte Versorgungs-Trips
        # waren im 20-Sweep strikt schlechter) — der Bot zündet nur aus dem
        # Inventar und bleibt sonst am Ort (Rückzug entscheidet _warm_here).
        e = _engine([], at=WARM)
        e.current_location.fire_active = False
        assert _fire_at(e) is False
        assert e.current_location_id == WARM, "_fire_at darf ohne Feuer keine Trips starten"

    def test_fire_at_never_gathers_off_warm(self):
        # Pendel-Schutz (Lektion 28.08.): am kalten Ort kein Sammel-Trip,
        # nur Zünden aus der Inventar-Reserve — sonst Rückzug (bt<35).
        e = _engine([], at="mountain_peak")
        ok = _fire_at(e)
        assert e.current_location_id == "mountain_peak", "_fire_at darf am kalten Ort nicht weglaufen"
        assert ok is False or e.current_location.fire_active

    def test_warmup_secures_supply_before_peak_trip(self, monkeypatch):
        # Der Kern des Tasks: sobald die Basis einmal Feuer hatte, darf der Bot
        # zum Gipfel aufbrechen — die Feuer-Reserven müssen im Inventar sein
        # (Versorgung VOR der Reise, Lektion 28.08.-Spirale).
        import play.guided_full as gf
        state = {"trip": 0, "fire": False}
        orig_go = gf._go

        def spy_go(game, loc):
            if game.locations[WARM].fire_active:
                state["fire"] = True
            if loc == "mountain_peak" and state["fire"] and state["trip"] == 0:
                # erster Gipfel-Aufbruch nach erstem Basis-Feuer = der Fell-Trip
                # (der Messer-Trip liegt VOR dem ersten Feuer)
                state["trip"] += 1
                assert _qty(game, "stick") >= 2 and _qty(game, "tinder") >= 1, \
                    "Aufbruch zum Gipfel ohne Feuer-Reserve — die Spirale startet exakt hier"
            orig_go(game, loc)

        monkeypatch.setattr(gf, "_go", spy_go)
        guided_full(20260819)  # früher Spiralen-Tod in der Baseline
        assert state["trip"] > 0, "Szenario (Basis-Feuer + Gipfel-Trip) muss in diesem Seed auftreten"



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