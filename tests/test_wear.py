"""Tests für SPEC-011 — Werkzeugverschleiß sichtbar machen.

Verdrahtet den bestehenden (stummen) Wear-Pfad: Warnzeile beim Schwellen-
durchgang, MISSING_TOOL-Zeile im gather-Log (node-gebunden), graduelle
Wirkung auf die Erntechance, sharpen_tool als apply-only Instandhaltung.
Kein neuer Experiment-Reason — alle Meldungen leben im gather-Logstream.
"""
import random

import pytest

from engine.core import GameEngine, WEAR_MIN_FACTOR, WEAR_WARN_THRESHOLD
from data.items import create_item


def _engine_with_axe(condition=1.0):
    """Engine am Waldrand mit frisch gecrafteter Flint-Axt (CHOPPING+SHOVEL)."""
    g = GameEngine()
    g.travel("forest_edge")
    inv = g.player.inventory
    for tpl, qty in [("flint_shard", 1), ("stick", 1), ("plant_fiber", 1)]:
        inv.add(create_item(tpl, qty))
    mats = [i for i in inv.items
            if i.template_id in ("flint_shard", "stick", "plant_fiber")]
    res = g.execute_experiment(mats)
    axe = inv.find_item_by_tag("CHOPPING")
    assert axe is not None, "Test-Setup: Flint-Axt sollte craftbar sein"
    axe.condition = condition
    return g


def _chopping_node(game):
    for node in game.current_location.nodes:
        if node.req_tool_tag:
            return node
    return None


class TestWearWarningOnce:
    def test_warning_fires_exactly_once_per_falling_pass(self):
        """Axt synthetisch knapp über der Schwelle: exakt EINE `abgenutzt`-Zeile
        an dem gather-Tick, der die Schwelle kreuzt; danach nie wieder."""
        g = _engine_with_axe(condition=WEAR_WARN_THRESHOLD + 0.05)
        axe = g.player.inventory.find_item_by_tag("CHOPPING")
        warns = 0
        for _ in range(30):
            if g.player.inventory.find_item_by_tag("CHOPPING") is None:
                break  # Werkzeug zerbrochen (eigene Zeile, keine Warnung)
            for line in g.gather():
                if "abgenutzt" in line:
                    warns += 1
        assert warns == 1, (
            f"Warnung soll genau 1x pro fallendem Durchgang feuern, war {warns}x"
        )

    def test_warning_not_fired_when_condition_already_below(self):
        """Bereits unter Schwelle: keine Nach-Warnung (kein Dauerspam)."""
        g = _engine_with_axe(condition=0.10)
        warns = 0
        for _ in range(10):
            if g.player.inventory.find_item_by_tag("CHOPPING") is None:
                break
            for line in g.gather():
                if "abgenutzt" in line:
                    warns += 1
        assert warns == 0


class TestMissingToolFeedback:
    def test_post_break_yields_missing_tool_line_at_harvestable_node(self):
        """Werkzeug entfernt, oak-Node voll (chance 1.0 via stock=max):
        gather() muss die Werkzeug-Meldung tragen statt still zu sein."""
        g = _engine_with_axe()
        g.player.inventory.items.remove(
            g.player.inventory.find_item_by_tag("CHOPPING"))
        node = _chopping_node(g)
        node.stock = node.max_stock  # erntbar (perception-Check läuft in gather)
        lines = []
        for _ in range(4):
            lines.extend(g.gather())
        assert any("Werkzeug" in l for l in lines), \
            "Nach Werkzeugverlust muss der gather eine Werkzeug-Meldung tragen"

    def test_no_missing_tool_line_when_nodes_not_harvestable(self):
        """Node-gebunden: nicht erntbare Tool-Nodes (depleted) erzeugen die
        Meldung nicht — sie gehört nur zum echten Wartungsfall."""
        g = _engine_with_axe()
        g.player.inventory.items.remove(
            g.player.inventory.find_item_by_tag("CHOPPING"))
        for n in g.current_location.nodes:
            if n.req_tool_tag:
                n.depleted = True
                n.stock = 0.0
        lines = []
        for _ in range(4):
            lines.extend(g.gather())
        assert not any("Werkzeug" in l for l in lines), \
            "Nicht erntbare Tool-Nodes dürfen die Meldung nicht erzeugen"


class TestGradualEffect:
    def test_worn_tool_harvests_less_than_fresh(self):
        """Deterministisch: 50 wood-gathers mit cond 1.0 vs 0.25 — die gedämpfte
        Axt erntet signifikant weniger (Faktor ~WEAR_MIN_FACTOR)."""
        def successes(condition):
            g = _engine_with_axe(condition=condition)
            node = _chopping_node(g)
            node.chance = 1.0            # deterministisches Max-Fenster
            node.stock = node.max_stock  # voller Vorrat (SPEC-004-Faktor = 1)
            node.depleted = False
            node.stock = float(node.max_stock) + 50  # 50 Erfolge ohne Erschöpfung
            hits = 0
            for _ in range(50):
                logs = g.gather()
                if any("Gefunden" in l and "Eichenstamm" in l for l in logs):
                    hits += 1
                # Traglast leeren, damit nur die Chance zählt (Gewicht cap sonst)
                for it in [i for i in g.player.inventory.items
                           if i.template_id == "log_oak"]:
                    g.player.inventory.items.remove(it)
                if g.player.inventory.find_item_by_tag("CHOPPING") is None:
                    break  # zerbrochen — zählt als 0 weiterer Erfolge
            return hits

        random.seed(424242)
        fresh = successes(1.0)
        random.seed(424242)
        worn = successes(WEAR_WARN_THRESHOLD)
        assert worn < fresh, (
            f"gedämpft ({worn}) muss unter frisch ({fresh}) liegen"
        )
        assert worn <= fresh * 0.7, (
            f"Faktor-Grenze verletzt: fresh={fresh}, worn={worn} "
            f"(erwartet ≲ {fresh * 0.7})"
        )


class TestSharpenTool:
    def test_success_consumes_flint_and_restores_condition(self):
        g = _engine_with_axe(condition=0.30)
        inv = g.player.inventory
        inv.add(create_item("flint_shard", 1))
        axe = inv.find_item_by_tag("CHOPPING")
        r = g.execute_process("sharpen_tool")
        assert r["success"] is True
        assert axe.condition == pytest.approx(0.80)  # +0.5, cap 1.0
        assert sum(i.quantity for i in inv.items
                   if i.template_id == "flint_shard") == 0

    def test_restore_caps_at_one(self):
        g = _engine_with_axe(condition=0.80)
        inv = g.player.inventory
        inv.add(create_item("flint_shard", 1))
        axe = inv.find_item_by_tag("CHOPPING")
        assert g.execute_process("sharpen_tool")["success"] is True
        assert axe.condition == 1.0  # cap

    def test_no_worn_tool_consumes_nothing(self):
        """Zweiter Aufruf ohne verschlissenes Werkzeug: kein Verbrauch."""
        g = _engine_with_axe(condition=1.0)  # nur volles Werkzeug
        inv = g.player.inventory
        inv.add(create_item("flint_shard", 1))
        r = g.execute_process("sharpen_tool")
        assert r["success"] is False
        assert r["reason"] == "NO_WORN_TOOL"
        assert sum(i.quantity for i in inv.items
                   if i.template_id == "flint_shard") == 1

    def test_without_flint_nothing_happens(self):
        g = _engine_with_axe(condition=0.30)
        r = g.execute_process("sharpen_tool")
        assert r["success"] is False
        assert g.player.inventory.find_item_by_tag("CHOPPING").condition == 0.30

    def test_sharpens_most_worn_matching_tool(self):
        """Zwei Werkzeuge: das am meisten abgenutzte passende wird geschärft."""
        g = _engine_with_axe(condition=0.60)
        inv = g.player.inventory
        # zweites Werkzeug (Messer, CUTTING) — noch abgenutzter
        inv.add(create_item("flint_shard", 1))
        inv.add(create_item("stick", 1))
        mats = [i for i in inv.items if i.template_id in ("flint_shard", "stick")]
        res = g.execute_experiment(mats)
        knife = inv.find_item_by_tag("CUTTING")
        assert knife is not None, "Setup: Messer craftbar"
        knife.condition = 0.20
        inv.add(create_item("flint_shard", 1))
        assert g.execute_process("sharpen_tool")["success"] is True
        assert knife.condition == pytest.approx(0.70)   # 0.20 + 0.5
        axe = inv.find_item_by_tag("CHOPPING")
        assert axe.condition == pytest.approx(0.60)     # unangetastet
