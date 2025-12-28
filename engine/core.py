"""
engine/core.py
Zentrale Logik inklusive Wetter- und Temperatur-Simulation.
"""
import random
import itertools
from typing import List, Dict, Any
from engine.components import Player, Item, ToolBlueprint
from data.locations import get_all_locations
from data.items import create_item
from data.blueprints import get_all_blueprints

class GameEngine:
    def __init__(self):
        self.player = Player("Survivor")
        self.locations = {loc.id: loc for loc in get_all_locations()}
        self.blueprints = {bp.id: bp for bp in get_all_blueprints()}
        self.current_location_id = "forest_edge"
        self.tick_counter = 0
        
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
        
        logs = []
        
        # 1. Hunger-Simulation
        drain = 5.0 * effort_multiplier * ticks
        self.player.energy = max(0, self.player.energy - drain)
        if self.player.energy <= 0:
            self.player.hp -= 2.0 * ticks
            logs.append("!!! HUNGER-SCHADEN !!!")

        # 2. Thermodynamik
        ambient_temp = self._get_ambient_temp()
        exposure = self.current_location.exposure * self.weather_types[self.current_weather]["exposure_mod"]
        insulation = self.player.inventory.get_total_insulation()
        
        # Delta zwischen Körper und Umwelt, abgemildert durch Isolation und Schutz
        temp_loss = (self.player.body_temp - ambient_temp) * 0.01 * exposure * (1.0 - min(0.9, insulation))
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

            if random.random() <= node.chance:
                qty = random.randint(node.min_qty, node.max_qty)
                item = create_item(node.result_template_id, qty)
                if self.player.inventory.add(item):
                    logs.append(f"Gefunden: {qty}x {item.name}")
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

    def execute_experiment(self, selected_items: List[Item]) -> Dict[str, Any]:
        # Crafting ist sehr anstrengend (Effort 3.0)
        self._advance_time(2, effort_multiplier=3.0)
        
        for bp_id, bp in self.blueprints.items():
            if len(selected_items) != len(bp.slots): continue
            if self.player.stats["survival"] < bp.min_survival_req: continue

            for p in itertools.permutations(selected_items):
                mapping = {}
                match = True
                for i, slot in enumerate(bp.slots.keys()):
                    if bp.slots[slot] not in p[i].tags:
                        match = False; break
                    mapping[slot] = p[i]
                
                if match:
                    if bp_id not in self.player.known_blueprints:
                        self.player.known_blueprints.add(bp_id)
                        self.player.stats["survival"] += 0.2
                    return self._create_tool(bp, mapping)
        return {"success": False, "message": "Nichts passiert."}

    def _create_tool(self, bp: ToolBlueprint, comp: Dict[str, Item]) -> Dict[str, Any]:
        dur_attr = min(c.get_attr("durability", 0.5) for c in comp.values())
        main = comp.get("head") or comp.get("blade") or list(comp.values())[0]
        power = main.get_attr("sharpness", 0.1) * bp.base_efficiency
        name = f"{main.name}-{bp.result_name} ({list(comp.values())[1].name})"
        new_tool = Item(name=name, base_weight=sum(c.base_weight for c in comp.values()),
                        tags={"DURABILITY": dur_attr}, attributes={"durability": dur_attr, "power": power})
        if bp.id == "axe": new_tool.tags["CHOPPING"] = power
        for c in comp.values():
            if c.quantity > 1: c.quantity -= 1
            else: self.player.inventory.items.remove(c)
        self.player.inventory.add(new_tool)
        return {"success": True, "message": f"Hergestellt: {name}"}

    def travel(self, tid: str):
        if tid not in self.locations: return "Unbekannt."
        self.current_location_id = tid
        msg = self._advance_time(3, effort_multiplier=1.5)
        return f"Gereist nach {self.locations[tid].name}. " + (msg if msg else "")