"""
engine/core.py
Zentrale Logik inklusive Wetter- und Temperatur-Simulation.
"""
import random
import itertools
from typing import List, Dict, Any
from engine.components import Player, Item, ToolBlueprint
from data.locations import get_all_locations
from data.items import create_item, TEMPLATE_DB
from data.blueprints import get_all_blueprints
from data.processes import get_all_processes

# Spielersprachliche Labels für Tags — die Brücke von internem Reason zu Text.
# Vollständig für alle im Spiel vorkommenden Tags (Konsistenz-Wächter in Tests).
TAG_LABELS = {
    "SHARP": "etwas Scharfes",
    "HARD": "etwas Hartes",
    "FLINT": "etwas aus Feuerstein",
    "BONE": "etwas aus Knochen",
    "FIBER": "etwas Faseriges",
    "RIGID": "etwas Festes",
    "STONE": "etwas Steinernes",
    "PROJECTILE": "etwas Wurfgeschossartiges",
    "EDIBLE": "etwas Essbares",
    "CHOPPING": "etwas zum Schneiden",
    "CUTTING": "etwas zum Schneiden",
    "PIERCE": "etwas zum Stechen",
    "KINDLING": "etwas zum Feuermachen",
    "SHOVEL": "etwas zum Graben",
    "DURABILITY": "etwas Haltbares",
    "WOOD": "etwas aus Holz",
    "CLAY": "etwas aus Ton",
    "CLOTHING": "Kleidung",
    "HEAT_SOURCE": "eine Wärmequelle",
}

# Wärmemanagement (SPEC-007): Kennzahlen des Location-Feuers. Balanciert das
# System "aktives Feuer aus/tragbare Isolation" — die Gegen-Schleife zur sonst
# unaufhaltsamen Unterkühlung. Detail-Balance in Peters Sinne liegt beim Dev.
FIRE_HEAT = 40.0          # Wärmebeitrag des aktiven Feuers zur Umgebungstemperatur
START_FIRE_FUEL = 24.0    # Brennstoff-Ticks beim Entzünden (≈ 4 In-Game-Stunden)
STOKE_FUEL = 8.0          # Brennstoff-Ticks, die nachgelegtes Holz/Machtsgut bringt

# Tag-Familien (SPEC-002): Eine Slot-Anforderung kann ein Familienname sein,
# der mehrere Tags subsumiert (Layer über den Einzel-Tags). Ein Item genügt der
# Familie, wenn es irgendeinen der Mitglieds-Tags trägt — so kann flint_shard
# (SHARP+HARD) oder ein harter Stab (RIGID) mehrere Rollen füllen.
TAG_FAMILIES = {
    "SHARP_OR_HARD": {"SHARP", "HARD"},
    "SHARP_OR_RIGID": {"SHARP", "RIGID"},
    "RIGID_OR_FIBER": {"RIGID", "FIBER"},
}


def _slot_satisfied(item_tags, slot_value: str) -> bool:
    """Prüft, ob die Tags eines Items einen Slot erfüllen (Familie o. Einzel-Tag).

    `item_tags` ist typischerweise ein Dict (Item.tags) oder ein Set (z.B. die
    ge-sammelte Tag-Menge in _no_match_reason). `&` zwischen set und dict wirft
    einen TypeError, daher Keywords explizit auslesen.
    """
    tags = item_tags.keys() if isinstance(item_tags, dict) else item_tags
    family = TAG_FAMILIES.get(slot_value)
    if family:
        return bool(family & set(tags))
    return slot_value in tags


def _label_for(tag: str) -> str:
    return TAG_LABELS.get(tag, f"etwas mit der Eigenschaft {tag}")


def _feedback_message(reason: str, broken_names: "List[str] | None" = None) -> str:
    """Baut eine spielersprachliche Meldung exakt aus dem Reason-Code.

    Verrät niemals mehr als der Reason hergibt — kein Rezept-Leaking. Wird der
    Code unkenntlich, gibt es eine generische (aber nicht lügende) Antwort.
    """
    if reason.startswith("MISSING_TAG:"):
        tag = reason.split(":", 1)[1]
        return f"Es fehlt dir {_label_for(tag)}."
    if reason == "TOO_FEW_ITEMS":
        return "Dafür brauchst du mindestens zwei Dinge."
    if reason == "NOT_ENOUGH_QUANTITY":
        return "Dafür brauchst du mehr von demselben Material."
    if reason == "BROKEN_ITEM":
        names = ", ".join(broken_names or [])
        return f"{names} ist zerbrochen und kann nicht verwendet werden."
    if reason == "NO_MATCH":
        return "Die Kombination ergibt nichts."
    if reason == "DEPLETED":
        return "Diese Stelle ist erschöpft. Komm später zurück."
    if reason == "FIRE_OUT":
        return "Dein Feuer erlischt."
    if reason == "NO_FIRE":
        return "Hier brennt kein Feuer."
    if reason == "MISSING_FUEL":
        return "Es fehlt dir Brennholz zum Nachlegen."
    if reason.startswith("MISSING_ENV:"):
        tag = reason.split(":", 1)[1]
        return f"Hier fehlt {_label_for(tag)} in der Umgebung."
    return "Das geht so nicht."  # UNKNOWN-Fallback — nie eine generische Leer-Meldung


class GameEngine:
    def __init__(self):
        self.player = Player("Survivor")
        self.locations = {loc.id: loc for loc in get_all_locations()}
        self.blueprints = {bp.id: bp for bp in get_all_blueprints()}
        self.processes = {p.id: p for p in get_all_processes()}
        self.current_location_id = "forest_edge"
        self.tick_counter = 36  # 6 Uhr morgens (36 Ticks), Tagesstart statt Mitternacht
        
        # Wettersystem
        self.weather_types = {
            "CLEAR": {"temp_mod": 0, "exposure_mod": 1.0},
            "RAIN": {"temp_mod": -5, "exposure_mod": 1.5},
            "STORM": {"temp_mod": -10, "exposure_mod": 2.5},
            "SNOW": {"temp_mod": -15, "exposure_mod": 2.0}
        }
        self.current_weather = "CLEAR"

    @property
    def current_location(self):
        return self.locations[self.current_location_id]

    def _update_weather(self):
        """Bestimmt alle 12 Ticks (2 Stunden) das Wetter neu."""
        if self.tick_counter % 12 == 0:
            self.current_weather = random.choice(list(self.weather_types.keys()))

    def _get_ambient_temp(self) -> float:
        """Berechnet die aktuelle Temperatur basierend auf Ort und Wetter."""
        loc = self.current_location
        weather_mod = self.weather_types[self.current_weather]["temp_mod"]
        # Simuliere Tag/Nacht-Zyklus (Nachts kälter)
        hour = (self.tick_counter % 144) / 6 # 144 Ticks = 24h
        night_mod = -10 if (hour < 6 or hour > 20) else 0
        return loc.base_temp + weather_mod + night_mod

    def _advance_time(self, ticks: int, effort_multiplier: float = 1.0):
        """Simuliert Zeit, Hunger und Thermodynamik."""
        self.tick_counter += ticks
        self._update_weather()

        # 0. Ressourcen-Regeneration (SPEC-004): Vorrat wächst über die
        # verstrichene Spielzeit, nicht über Aktionen. Dadurch regenerieren
        # sich auch andere Orte, während man unterwegs handelt — die Zeit
        # zwischen zwei Besuchen bestimmt den Füllstand.
        for loc in self.locations.values():
            for node in loc.nodes:
                node.stock = min(node.max_stock, node.stock
                                 + node.regen_per_tick * ticks)
                # Ein erschöpfter Node erholt sich erst, wenn genug Zeit
                # vergangen ist, um mindestens eine Ernte-Portion aufzufüllen.
                if node.depleted and node.stock >= node.harvest_cost:
                    node.depleted = False

        logs = []
        
        # 1. Hunger-Simulation
        drain = 5.0 * effort_multiplier * ticks
        self.player.energy = max(0, self.player.energy - drain)
        if self.player.energy <= 0:
            self.player.hp -= 2.0 * ticks
            logs.append("!!! HUNGER-SCHADEN !!!")

        # 2. Thermodynamik (SPEC-007: aktives Location-Feuer hebt die effektive
        # Umgebungstemperatur, verbraucht aber Brennstoff, der über Zeit brennt.
        # Bei Brennstoff 0 erlischt das Feuer mit einer ehrlichen Meldung — nie
        # still. Das macht Kälte abwendbar statt unvermeidbar.)
        ambient_temp = self._get_ambient_temp()
        fire_warmth = 0.0
        loc = self.current_location
        if loc.fire_active and loc.fire_fuel > 0:
            fire_warmth = FIRE_HEAT
            loc.fire_fuel = max(0.0, loc.fire_fuel - ticks)
            if loc.fire_fuel <= 0:
                loc.fire_active = False
                logs.append("!!! FIRE_OUT: " + _feedback_message("FIRE_OUT") + " !!!")
        exposure = loc.exposure * self.weather_types[self.current_weather]["exposure_mod"]
        insulation = self.player.inventory.get_total_insulation()
        effective_ambient = ambient_temp + fire_warmth

        # Delta zwischen Körper und Umwelt, abgemildert durch Isolation und Schutz
        temp_loss = (self.player.body_temp - effective_ambient) * 0.01 * exposure * (1.0 - min(0.9, insulation))
        self.player.body_temp -= (temp_loss * ticks)
        
        # Auswirkungen der Körpertemperatur
        if self.player.body_temp < 35.0:
            self.player.hp -= 1.0 * ticks
            logs.append("!!! UNTERKÜHLUNG !!!")
        elif self.player.body_temp > 40.0:
            self.player.hp -= 1.0 * ticks
            logs.append("!!! HITZSCHLAG !!!")

        return "\n".join(logs) if logs else None

    def gather(self) -> List[str]:
        logs = []
        # Sammeln ist anstrengend (Effort 2.0)
        time_msg = self._advance_time(1, effort_multiplier=2.0)
        if time_msg: logs.append(time_msg)

        for node in self.current_location.nodes:
            if self.player.stats["perception"] < node.req_perception: continue
            
            used_tool = None
            if node.req_tool_tag:
                used_tool = self.player.inventory.find_item_by_tag(node.req_tool_tag)
                if not used_tool: continue

            # Vorratsbasierter Node (SPEC-004): erschöpft → ehrliche Meldung,
            # nie stilles "nichts". Bleibt erschöpft, bis Regeneration ihn
            # über die Zeit wieder auf mindestens eine Ernte-Portion hebt.
            if node.stock <= 0 or node.depleted:
                logs.append(_feedback_message("DEPLETED"))
                continue

            # Erfolgswahrscheinlichkeit skaliert mit dem Vorratsanteil:
            # voller Vorrat = node.chance, geleerter = 0.
            eff_chance = node.chance * (node.stock / node.max_stock)
            if random.random() <= eff_chance:
                qty = random.randint(node.min_qty, node.max_qty)
                item = create_item(node.result_template_id, qty)
                if self.player.inventory.add(item):
                    logs.append(f"Gefunden: {qty}x {item.name}")
                    node.stock = max(0.0, node.stock - node.harvest_cost)
                    if node.stock < node.harvest_cost:
                        node.depleted = True
                    if used_tool:
                        wear = 0.05 / used_tool.get_attr("durability", 0.5)
                        used_tool.condition = max(0, used_tool.condition - round(wear, 2))
                        if used_tool.condition <= 0:
                            self.player.inventory.items.remove(used_tool)
                            logs.append(f"!!! {used_tool.name} zerbrochen !!!")
        return logs

    def eat(self, item_index: int) -> str:
        """Versucht ein Item aus dem Inventar zu essen."""
        items = self.player.inventory.items
        if item_index < 0 or item_index >= len(items):
            return "Ungültiges Item."
        
        item = items[item_index]
        if "EDIBLE" not in item.tags:
            return f"{item.name} ist nicht essbar!"
        
        kcal = item.tags["EDIBLE"]
        self.player.energy = min(self.player.max_energy, self.player.energy + kcal)
        
        # Wenn man isst, regeneriert man etwas HP
        self.player.hp = min(self.player.max_hp, self.player.hp + (kcal / 20))
        
        name = item.name
        if item.quantity > 1: item.quantity -= 1
        else: items.remove(item)
        
        return f"Du isst {name} und regenerierst {kcal} Energie."

    def _result(self, success, message, reason, blueprint_id=None,
                result_template_id=None):
        """Strukturiertes Ergebnis mit Reason-Code (kein Verhaltensunterschied)."""
        return {
            "success": success,
            "message": message,
            "reason": reason,                 # SUCCESS/NO_MATCH/BROKEN_ITEM/MISSING_TAG:<T>/TOO_FEW_ITEMS/UNKNOWN
            "blueprint_id": blueprint_id,
            "result_template_id": result_template_id,
        }

    def _no_match_reason(self, selected_items):
        """Bestimmt den konkretesten Reason für einen Fehlschlag.

        Wählt den Blueprint (passender Slot-Anzahl), dem der Spieler am nächsten
        ist, und nennt daraus genau ein fehlendes Merkmal. Familien-Slots werden
        auf ihren fehlenden Mitglieds-Tag aufgelöst, damit die Meldung ein
        verständliches Label trägt (nie ein leeres Null-Feedback).
        """
        available = set()
        for it in selected_items:
            available.update(it.tags)

        best = None  # (Nähe-Score, fehlender Tag fürs Label)
        for bp in self.blueprints.values():
            if len(bp.slots) != len(selected_items):
                continue
            missing = []
            for slot_value in bp.slots.values():
                required = set(TAG_FAMILIES.get(slot_value, {slot_value}))
                if not (required & available):
                    # Repräsentant fürs Label: der Ziel-Tag, der am nächsten liegt.
                    missing.append(next(iter(required)))
            if not missing:
                continue  # Volltreffer wäre schon im Haupt-Loop gefangen worden
            score = len(bp.slots) - len(missing)
            if best is None or score > best[0]:
                best = (score, missing[0])
        if best:
            return f"MISSING_TAG:{best[1]}"
        return "NO_MATCH"

    def execute_experiment(self, selected_items: List[Item]) -> Dict[str, Any]:
        # Crafting ist sehr anstrengend (Effort 3.0)
        self._advance_time(2, effort_multiplier=3.0)

        # Zerbrochene Items (condition=0) sind nicht craftbar → verständliches Feedback
        broken = [it.name for it in selected_items if it.condition <= 0]
        if broken:
            return self._result(
                False,
                _feedback_message("BROKEN_ITEM", broken),
                "BROKEN_ITEM")

        # Zu wenige Items für den kleinsten Blueprint → nicht einmal ein Versuch
        slot_counts = [len(bp.slots) for bp in self.blueprints.values()]
        min_count = min(slot_counts) if slot_counts else 0
        if len(selected_items) < min_count:
            return self._result(False, _feedback_message("TOO_FEW_ITEMS"),
                                "TOO_FEW_ITEMS")

        # Menge-Validierung (SPEC-005): Derselbe Stack kann N identische Slots
        # füllen, aber nur solange quantity >= N. Taucht ein Stack-Objekt mehrfach
        # in selected_items auf, ohne dass die Menge das deckt, würde _create_tool
        # sonst ein Item aus dem Nichts erzeugen (Fehlstart). Stattdessen: ehrliches
        # Feedback. Distinkte Stacks (zwei separate Ast-Stacks) bleiben unberührt —
        # die Zählung geht über die Objekt-Identität, nicht den Namen.
        seen = {}
        for it in selected_items:
            n = seen.get(id(it), 0) + 1
            seen[id(it)] = n
            if n > it.quantity:
                return self._result(False,
                                    _feedback_message("NOT_ENOUGH_QUANTITY"),
                                    "NOT_ENOUGH_QUANTITY")

        for bp_id, bp in self.blueprints.items():
            if len(selected_items) != len(bp.slots): continue
            if self.player.stats["survival"] < bp.min_survival_req: continue

            for p in itertools.permutations(selected_items):
                mapping = {}
                match = True
                for i, slot in enumerate(bp.slots.keys()):
                    if not _slot_satisfied(p[i].tags, bp.slots[slot]):
                        match = False; break
                    mapping[slot] = p[i]
                
                if match:
                    if bp_id not in self.player.known_blueprints:
                        self.player.known_blueprints.add(bp_id)
                        self.player.stats["survival"] += 0.2
                    return self._create_tool(bp, mapping)
        reason = self._no_match_reason(selected_items)
        return self._result(False, _feedback_message(reason), reason)

    def _create_tool(self, bp: ToolBlueprint, comp: Dict[str, Item]) -> Dict[str, Any]:
        dur_attr = min(c.get_attr("durability", 0.5) for c in comp.values())
        main = comp.get("head") or comp.get("blade") or list(comp.values())[0]
        power = main.get_attr("sharpness", 0.1) * bp.base_efficiency
        name = f"{main.name}-{bp.result_name} ({list(comp.values())[1].name})"
        new_tool = Item(name=name, base_weight=sum(c.base_weight for c in comp.values()),
                        tags={"DURABILITY": dur_attr}, attributes={"durability": dur_attr, "power": power},
                        template_id=bp.id)
        for t in bp.tool_tags:
            new_tool.tags[t] = power
        for c in comp.values():
            # Robust: verbrauche nur Stacks, die wirklich im Inventar liegen. Ein
            # Item-Objekt kann mehrfach selektiert (derselbe Stack) oder in einem
            # anderen Stack zusammengeführt worden sein — kein blindes remove(),
            # sonst ValueError. (Fix: 3-Sticks-Speer, Doppel-Selektion.)
            if c not in self.player.inventory.items:
                continue
            if c.quantity > 1:
                c.quantity -= 1
            else:
                self.player.inventory.items.remove(c)
        self.player.inventory.add(new_tool)
        return {"success": True, "message": f"Hergestellt: {name}",
                "reason": "SUCCESS", "blueprint_id": bp.id,
                "result_template_id": bp.id}

    # ------------------------------------------------------------------
    # Prozess-System — Transformationen mit Umgebungs-/Werkzeug-Kontext
    # ------------------------------------------------------------------

    def _count_template(self, template_id: str) -> int:
        """Gesamtmenge eines Items über alle Stacks (nach template_id)."""
        return sum(it.quantity for it in self.player.inventory.items
                   if it.template_id == template_id)

    def _consume_template(self, template_id: str, qty: int):
        """Entfernt qty eines Items (über mehrere Stacks, falls nötig)."""
        remaining = qty
        for it in list(self.player.inventory.items):
            if it.template_id != template_id or remaining <= 0:
                continue
            take = min(it.quantity, remaining)
            it.quantity -= take
            remaining -= take
            if it.quantity <= 0:
                self.player.inventory.items.remove(it)
        return remaining == 0

    def _item_name(self, template_id: str) -> str:
        t = TEMPLATE_DB.get(template_id)
        return t.name if t else template_id

    # ------------------------------------------------------------------
    # Wärmemanagement (SPEC-007) — Feuer entzünden, hüten, nachlegen
    # ------------------------------------------------------------------

    def _light_fire(self):
        """Setzt den Location-Feuerzustand (aktives Feuer + Brennstoff).

        Wird von execute_process("start_fire") gerufen, sobald das Feuer
        entzündet ist. Das Feuer existiert dann an der Location, nicht nur
        als Inventar-Gegenstand.
        """
        loc = self.current_location
        loc.fire_active = True
        loc.fire_fuel = START_FIRE_FUEL

    def _fire_lit(self) -> bool:
        """Ein aktives Feuer mit Brennstoff brennt an der aktuellen Location."""
        loc = self.current_location
        return bool(loc.fire_active and loc.fire_fuel > 0)

    def _env_satisfied(self, tag: str) -> bool:
        """Ob die Location ein Umgebungs-Tag erfüllt (z.B. HEAT_SOURCE)."""
        if tag == "HEAT_SOURCE":
            return self._fire_lit()
        return False

    def _find_fuel_item(self):
        """Brennstoff-Item fürs Nachlegen: Holz (WOOD) bevorzugt, sonst Zunder/
        Reisig (KINDLING) — aber nie die Feuergrube selbst."""
        for it in self.player.inventory.items:
            if "WOOD" in it.tags and it.condition > 0:
                return it
        for it in self.player.inventory.items:
            if ("KINDLING" in it.tags and it.template_id != "fire_pit"
                    and it.condition > 0):
                return it
        return None

    def stoke_fire(self) -> Dict[str, Any]:
        """Legt Brennstoff nach: erhöht fire_fuel, kostet Zeit (Long-Dark-Zyklus).

        Nur bei aktivem Feuer möglich — ohne Feuer keine Wärme, man muss Holz
        sammeln und es nachlegen, um warm zu bleiben.
        """
        loc = self.current_location
        if not loc.fire_active:
            return {"success": False, "message": _feedback_message("NO_FIRE"),
                    "reason": "NO_FIRE"}
        fuel = self._find_fuel_item()
        if fuel is None:
            return {"success": False, "message": _feedback_message("MISSING_FUEL"),
                    "reason": "MISSING_FUEL"}
        name = fuel.name
        if fuel.quantity > 1:
            fuel.quantity -= 1
        else:
            self.player.inventory.items.remove(fuel)
        loc.fire_fuel += STOKE_FUEL
        # Nachlegen ist Arbeit und vergeht Zeit — Brennstoff brennt weiter.
        time_msg = self._advance_time(1, effort_multiplier=1.0)
        msg = f"Du legst {name} nach. "
        msg += (time_msg if time_msg else "")
        return {"success": True, "message": msg.strip(), "reason": "SUCCESS"}

    def available_processes(self) -> List[str]:
        """Prozesse, deren Inputs, Werkzeug- und Umgebungs-Anforderungen erfüllt sind."""
        avail = []
        for pid, proc in self.processes.items():
            if any(self._count_template(i) < q for i, q in proc.inputs.items()):
                continue
            if any(not self.player.inventory.find_item_by_tag(t) for t in proc.tools):
                continue
            if proc.required_tag_in_env and not self._env_satisfied(proc.required_tag_in_env):
                continue
            avail.append(pid)
        return avail

    def execute_process(self, process_id: str) -> Dict[str, Any]:
        """Führt einen Prozess aus: konsumiert Inputs, nutzt Werkzeuge, erzeugt Outputs.

        Seit SPEC-007 ist `required_tag_in_env` HART: Ein Prozess, der eine
        Umgebungs-Anforderung deklariert (z.B. `cook_meat` → `HEAT_SOURCE`),
        läuft nur, wenn die aktuelle Location sie erfüllt (aktives Feuer).
        Das aktiviert das zuvor tote Feld und macht das Feuer real nötig.
        """
        proc = self.processes.get(process_id)
        if not proc:
            return {"success": False, "message": "Unbekannter Prozess.",
                    "reason": "UNKNOWN_PROCESS"}

        for item_id, qty in proc.inputs.items():
            if self._count_template(item_id) < qty:
                return {"success": False,
                        "message": f"Es fehlt dir {self._item_name(item_id)}.",
                        "reason": f"MISSING_INPUT:{item_id}"}

        for tag in proc.tools:
            if not self.player.inventory.find_item_by_tag(tag):
                return {"success": False,
                        "message": f"Es fehlt dir {_label_for(tag)} als Werkzeug.",
                        "reason": f"MISSING_TOOL:{tag}"}

        if proc.required_tag_in_env and not self._env_satisfied(proc.required_tag_in_env):
            return {"success": False,
                    "message": _feedback_message(f"MISSING_ENV:{proc.required_tag_in_env}"),
                    "reason": f"MISSING_ENV:{proc.required_tag_in_env}"}

        # SPEC-007: start_fire entzündet das Location-Feuer, BEVOR die
        # Entzündungsdauer vergeht — ein frisch gebautes Feuer wärmt schon
        # während seines Aufbaus, statt den Spieler in der Kälte warten zu lassen.
        if process_id == "start_fire":
            self._light_fire()

        # Inputs verbrauchen, dann Zeit/Energie kosten (wie Crafting anstrengend)
        for item_id, qty in proc.inputs.items():
            self._consume_template(item_id, qty)
        self._advance_time(proc.duration_ticks, effort_multiplier=2.0)

        for item_id, qty in proc.outputs.items():
            self.player.inventory.add(create_item(item_id, qty))

        if process_id not in self.player.known_processes:
            self.player.known_processes.add(process_id)
            self.player.stats["survival"] += 0.1

        return {"success": True, "message": f"Prozess ausgeführt: {proc.name}",
                "reason": "SUCCESS", "process_id": process_id}

    def travel(self, tid: str):
        if tid not in self.locations: return "Unbekannt."
        self.current_location_id = tid
        msg = self._advance_time(3, effort_multiplier=1.5)
        return f"Gereist nach {self.locations[tid].name}. " + (msg if msg else "")