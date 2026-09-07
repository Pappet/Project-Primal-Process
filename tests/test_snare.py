"""SPEC-012 — Faserschlinge (snare): die toten 2-Slot-Selektionsräume besetzen.

Ein 2-Slot-Blueprint {loop: FIBER, bait: EDIBLE} — Nahrung wird Baumaterial
(Don't Starve: Köder + Falle; UnReal World: Schlingenfang). Data-only: der
Test überprüft das Blueprint-Verhalten in der Engine, nicht die Engine selbst.

Akzeptanzkriterien (Work-Contract):
1. snare craftet aus (plant_fiber, berries) bei survival 0.0 und aus
   (reeds, raw_meat) — EDIBLE-Slot ist material-agnostisch.
2. Shadowing: (stick, stick) → spear; (reeds, stick) ab survival 0.4 → rope;
   snare wird nie von der Präzedenz verdrängt und verdrängt selbst nichts.
3. Jagd-Verbrauch: raw_meat-Ernte mit der Schlinge → quantity-- pro Erfolg,
   Leer-Meldung beim letzten Fang (31.08.-Munitions-Pfad), kein Stack-Wear.
"""
import pytest
from engine.core import GameEngine
from data.items import create_item


def _craft_engine(*template_ids):
    """Engine mit Templates im Inventar (für Craft-Pfade über execute_experiment
    via Inventar-Objekte). tick_counter=72: Tageszeit, kein Wetter-Roll davor."""
    engine = GameEngine()
    engine.player.inventory.items.clear()
    engine.tick_counter = 72
    for tpl in template_ids:
        engine.player.inventory.add(create_item(tpl))
    return engine


def _try(engine):
    items = list(engine.player.inventory.items)
    return engine.execute_experiment(items)


def _try_items(engine, *template_ids):
    """Experiment mit expliziter Item-Liste (getrennte Objekte) — der
    engine-true Weg für Doppelslot-Crafts wie (stick, stick) → spear,
    bei denen Inventory.add sonst zu einem Stack mergen würde."""
    items = [create_item(t) for t in template_ids]
    return engine.execute_experiment(items)


class TestSnareCraft:
    def test_crafts_at_survival_zero(self):
        """Ungated: (plant_fiber, berries) craftet die Schlinge bei survival 0.0."""
        engine = _craft_engine("plant_fiber", "berries")
        assert engine.player.stats["survival"] == 0.0
        res = _try(engine)
        assert res["success"] is True
        assert res["blueprint_id"] == "snare"

    def test_edible_slot_is_material_agnostic(self):
        """EDIBLE-Slot akzeptiert jedes Essbare: (reeds, raw_meat) craftet ebenfalls."""
        engine = _craft_engine("reeds", "raw_meat")
        res = _try(engine)
        assert res["success"] is True
        assert res["blueprint_id"] == "snare"

    def test_success_message_follows_dynamic_schema_no_leak(self):
        """Erfolgs-Meldung folgt dem dynamischen _create_tool-Namensschema —
        sie verrät nur, was der Spieler soeben selbst zusammengebracht hat."""
        engine = _craft_engine("plant_fiber", "berries")
        res = _try(engine)
        assert res["message"].startswith("Hergestellt: ")
        assert "Faserschlinge" in res["message"]
        # NEW_COMPONENT-Reveal: PROJECTILE ist neu → generischer Richtungshinweis
        assert "verbinden" in res["message"]

    def test_crafted_snare_is_projectile_tool(self):
        """Die Schlinge ist ein Werkzeug mit PROJECTILE-Tag (Jagd-Alternative)."""
        engine = _craft_engine("plant_fiber", "berries")
        _try(engine)
        projectiles = [it for it in engine.player.inventory.items
                       if "PROJECTILE" in it.tags]
        assert len(projectiles) == 1


class TestSnareShadowing:
    def test_stick_stick_still_spear(self):
        engine = GameEngine()
        res = _try_items(engine, "stick", "stick")
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"

    def test_reeds_stick_prefers_spear_not_snare(self):
        """Engine-truth: (reeds, stick) → spear (reeds trägt RIGID, spear steht
        früher im Dict) — wie VOR SPEC-012. Der Work-Contract-Text behauptete
        rope; das war falsch (rope craftet aus (plant_fiber, stick), s.u.).
        Entscheidend: snare verdrängt die Präzedenz nicht — kein EDIBLE im
        Spiel, also kann snare diesen Craft nie übernehmen."""
        engine = GameEngine()
        engine.player.stats["survival"] = 0.5
        res = _try_items(engine, "reeds", "stick")
        assert res["success"] is True
        assert res["blueprint_id"] == "spear"

    def test_plant_fiber_stick_crafts_rope_at_gate(self):
        """Der echte rope-Fall (Work-Contract: '(reeds, stick) ab survival 0.4
        → rope'): plant_fiber trägt nur FIBER, kann spear nicht besetzen →
        rope. Unverändert durch snare (stick hat kein EDIBLE)."""
        engine = GameEngine()
        engine.player.stats["survival"] = 0.5
        res = _try_items(engine, "plant_fiber", "stick")
        assert res["success"] is True
        assert res["blueprint_id"] == "rope"

    def test_berries_fiber_crafts_snare_at_any_survival(self):
        """(plant_fiber, berries) → snare bei ALLEN survival-Werten (ungated)."""
        for survival in (0.0, 0.4, 0.6, 0.9):
            engine = _craft_engine("plant_fiber", "berries")
            engine.player.stats["survival"] = survival
            res = _try(engine)
            assert res["success"] is True, f"survival={survival}"
            assert res["blueprint_id"] == "snare", f"survival={survival}"

    def test_no_edible_no_snare(self):
        """Ohne EDIBLE-Beteiligten gibt es keinen snare-Craft — Faser+Faser
        matcht ihn nicht (kein stiller Zweit-Craft hinter rope etc.)."""
        engine = _craft_engine("plant_fiber", "reeds")
        engine.player.stats["survival"] = 0.5
        res = _try(engine)
        assert res["blueprint_id"] != "snare"


class TestSnareBlueprintRegistry:
    def test_registry_has_eleven(self):
        engine = GameEngine()
        assert len(engine.blueprints) == 11
        assert "snare" in engine.blueprints

    def test_snare_is_last_entry(self):
        """Data-only-Präzedenz: snare steht am Array-Ende (nach cord_spear)."""
        engine = GameEngine()
        ids = list(engine.blueprints.keys())
        assert ids[-1] == "snare"
        assert ids[-2] == "cord_spear"

    def test_snare_fields(self):
        engine = GameEngine()
        bp = engine.blueprints["snare"]
        assert bp.result_name == "Faserschlinge"
        assert bp.slots == {"loop": "FIBER", "bait": "EDIBLE"}
        assert bp.base_efficiency == 1.0
        assert bp.min_survival_req == 0.0
        assert bp.tool_tags == ["PROJECTILE"]


class TestSnareHuntConsumption:
    """Jagd mit der Schlinge läuft über den 31.08.-Munitions-Pfad: ein Fang,
    eine Einheit — quantity-- pro Ernteerfolg, Leer-Meldung nur beim letzten
    Fang, kein Condition-Wear auf dem Stack."""

    @staticmethod
    def _deterministic_gather(monkeypatch):
        monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
        monkeypatch.setattr("engine.core.random.randint", lambda a, b: a)

    def _snare_engine(self, monkeypatch, qty=2):
        self._deterministic_gather(monkeypatch)
        engine = _craft_engine("plant_fiber", "berries")
        res = _try(engine)
        assert res["blueprint_id"] == "snare"
        engine.player.inventory.items[0].quantity = qty
        return engine

    @staticmethod
    def _snare_stack(engine):
        stacks = [it for it in engine.player.inventory.items
                  if it.template_id == "snare"]
        assert len(stacks) == 1, "Schlinge bleibt ein gemergter Stack"
        return stacks[0]

    @staticmethod
    def _meat_count(engine):
        return sum(it.quantity for it in engine.player.inventory.items
                   if it.template_id == "raw_meat")

    def test_hunt_succeeds_and_consumes_one_unit(self, monkeypatch):
        engine = self._snare_engine(monkeypatch, qty=2)
        logs = engine.gather()
        assert self._meat_count(engine) >= 1, "Jagd-Ertrag mit Schlinge"
        assert self._snare_stack(engine).quantity == 1

    def test_condition_untouched(self, monkeypatch):
        engine = self._snare_engine(monkeypatch)
        engine.gather()
        assert self._snare_stack(engine).condition == 1.0

    def test_last_snare_depletes_with_message(self, monkeypatch):
        engine = self._snare_engine(monkeypatch, qty=1)
        logs = engine.gather()
        deplete = [l for l in logs
                   if "aufgebraucht" in l and "Faserschlinge" in l]
        assert deplete, "Letzte Schlinge feuert die ehrliche Leer-Meldung"
        assert not self._snare_stacks_left(engine)

    @staticmethod
    def _snare_stacks_left(engine):
        return [it for it in engine.player.inventory.items
                if it.template_id == "snare"]

    def test_no_snare_no_hunt_yield(self, monkeypatch):
        """Ohne PROJECTILE-Item bleibt es bei der MISSING_TOOL-Meldung
        (SPEC-011-C-Pfad) — die Schlinge ergänzt, nicht ersetzt."""
        self._deterministic_gather(monkeypatch)
        engine = _craft_engine("plant_fiber", "reeds")
        logs = engine.gather()
        assert self._meat_count(engine) == 0
        assert any("Werkzeug" in l for l in logs)
