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


class TestInjuredFeedbackBranch:
    """B08: gather() ruft _feedback_message("INJURED"), aber es gab keinen
    INJURED-Zweig — der Spieler las den generischen Fallback „Das geht so
    nicht." statt einer Verletzungs-Meldung."""

    def test_injured_has_own_label_no_fallback(self):
        from engine.core import _feedback_message
        msg = _feedback_message("INJURED")
        assert "verletzt" in msg.lower()
        # kein generischer Fallback
        assert msg != "Das geht so nicht."

    def test_injured_no_recipe_leak(self):
        from engine.core import _feedback_message
        low = _feedback_message("INJURED").lower()
        assert "bandage" not in low and "pflanzenfaser" not in low

    def test_gather_injury_log_uses_branch_not_fallback(self):
        e = engine_with([("plant_fiber", 2)])
        logs = e.gather()
        for line in logs:
            assert "Das geht so nicht." not in line


def _pebble_stacks(e):
    return [it for it in e.player.inventory.items if "PROJECTILE" in it.tags]


def _deterministic_gather(monkeypatch):
    """Jeder Wurf trifft, jede Menge = min. Randint-Mock, damit der
    pebble-Ground-Node (Nachschub ohne Tool-Req) nicht stört."""
    monkeypatch.setattr("engine.core.random.random", lambda: 0.0)
    monkeypatch.setattr("engine.core.random.randint", lambda a, b: a)


class TestAmmoEconomy:
    """Munitions-Ökonomie: Ein Projektil ist Consumable, kein dauerhaftes
    Werkzeug. Vorher lief die Jagd (PROJECTILE-Node) über den Werkzeug-Wear-
    Pfad (~0.25/Erfolg) — der komplette Pebble-Stack verschwand nach ~4
    Schüssen still als „zerbrochen"."""

    def test_shot_consumes_exactly_one_unit(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([("pebble", 4)])
        e.gather()  # forest_edge: 1 Schuss (-1), Ground-Node liefert +1
        assert sum(it.quantity for it in _pebble_stacks(e)) == 4

    def test_stack_not_collectively_removed(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([("pebble", 4)])
        e.gather()
        stacks = _pebble_stacks(e)
        assert stacks, "Pebble-Stack darf nach einem Schuss nicht kollektiv weg sein"
        assert len(stacks) == 1, "Munition bleibt ein gemergter Stack (keine Condition-Fragmente)"
        assert stacks[0].quantity == 4

    def test_condition_untouched_no_wear_artifacts(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([("pebble", 4)])
        for _ in range(3):
            e.gather()
        for it in _pebble_stacks(e):
            assert it.condition == it.condition  # kein NaN
            assert it.condition == 1.0  # kein Wear auf Munition

    def test_last_unit_depletes_with_message(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([("pebble", 1)])
        logs = e.gather()
        assert any("aufgebraucht" in l for l in logs), \
            "Letzte Munitionseinheit feuert ehrliche Leer-Meldung"

    def test_no_ammo_no_hunt_yield(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([])
        e.gather()
        meat = [it for it in e.player.inventory.items if it.template_id == "raw_meat"]
        assert not meat, "Ohne Munition kein Jagd-Ertrag (MISSING_TOOL-Zweig)"

    def test_no_zerbrochen_for_ammo(self, monkeypatch):
        _deterministic_gather(monkeypatch)
        e = engine_with([("pebble", 4)])
        logs = e.gather()
        assert not any("zerbrochen" in l for l in logs), \
            "Munition wird verbraucht, nicht zerbrochen"


def _craft_hint_engine(engine, template_id, qty):
    e = engine_with([(template_id, qty)])
    return e


class TestProcessPotenzialHints:
    """Ziel-2-Hebel: Besitz + Umgebung erzeugen einen einmaligen, generischen
    Hinweis pro Prozess-Klasse („hier ließe sich etwas …"), sobald die
    Prozess-Anforderungen vollständig erfüllt sind. Kein Rezept-Leak:
    Text nennt keine Items/Mengen/Prozess-IDs."""

    def test_no_hints_on_fresh_start(self):
        e = GameEngine()
        assert e.take_process_hints() == []

    def test_bandage_input_met_fires_generic_hint(self):
        e = _craft_hint_engine(None, "plant_fiber", 2)
        hints = e.take_process_hints()
        pids = [pid for pid, _ in hints]
        assert "make_bandage" in pids
        text = next(t for pid, t in hints if pid == "make_bandage")
        low = text.lower()
        assert "pflanzenfaser" not in low and "bandage" not in low and "verband" not in low

    def test_hint_is_once_per_category(self):
        e = _craft_hint_engine(None, "plant_fiber", 2)
        first = e.take_process_hints()
        assert any(pid == "make_bandage" for pid, _ in first)
        # zweiter Aufruf: Kategorie bereits gesehen → still
        assert e.take_process_hints() == []
        # nach der Ausführung: treat_cut ist eine NEUE Kategorie → feuert
        e.execute_process("make_bandage")
        second = e.take_process_hints()
        assert any(pid == "treat_cut" for pid, _ in second)

    def test_cook_meat_needs_env_and_meat(self):
        e = _craft_hint_engine(None, "raw_meat", 1)
        assert not any(pid == "cook_meat" for pid, _ in e.take_process_hints())
        e._light_fire()  # Umgebung erfüllt (HEAT_SOURCE)
        assert any(pid == "cook_meat" for pid, _ in e.take_process_hints())

    def test_tinder_needs_input_and_tool(self):
        from engine.components import Item
        e = _craft_hint_engine(None, "reeds", 2)
        assert not any(pid == "create_tinder" for pid, _ in e.take_process_hints())
        e.player.inventory.add(Item("Messer", 0.3, {"CUTTING": True}))
        assert any(pid == "create_tinder" for pid, _ in e.take_process_hints())

    def test_hint_does_not_execute_or_consume(self):
        e = _craft_hint_engine(None, "plant_fiber", 2)
        before = e._count_template("plant_fiber")
        e.take_process_hints()
        assert e._count_template("plant_fiber") == before
        assert e.tick_counter == GameEngine().tick_counter  # keine Zeit verbraucht

    def test_available_processes_unchanged_by_refactor(self):
        """Der Hint-Check darf die available_processes-Semantik nicht ändern."""
        e = _craft_hint_engine(None, "plant_fiber", 2)
        assert "make_bandage" in e.available_processes()
        e.take_process_hints()
        assert "make_bandage" in e.available_processes()
