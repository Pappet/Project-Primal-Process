"""
engine/core.py
Haupt-Logik inklusive Abnutzung von Werkzeugen.
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
        self.blueprints = get_all_blueprints()
        self.current_location_id = "forest_edge"
        self.tick_counter = 0

    @property
    def current_location(self):
        return self.locations[self.current_location_id]

    def gather(self) -> List[str]:
        """Sammeln mit Werkzeug-Abnutzung."""
        loc = self.current_location
        logs = []
        self._advance_time(1)

        for node in loc.nodes:
            if self.player.stats["perception"] < node.req_perception:
                continue
            
            used_tool = None
            if node.req_tool_tag:
                used_tool = self.player.inventory.find_item_by_tag(node.req_tool_tag)
                if not used_tool: continue

            if random.random() <= node.chance:
                qty = random.randint(node.min_qty, node.max_qty)
                item = create_item(node.result_template_id, qty)
                
                if self.player.inventory.add(item):
                    logs.append(f"Gefunden: {qty}x {item.name}")
                    # Werkzeug-Abnutzung berechnen
                    if used_tool:
                        # Abnutzung basiert auf der Durability des Werkzeug-Materials
                        wear = 0.05 / used_tool.get_attr("durability", 0.5)
                        used_tool.condition -= round(wear, 2)
                        if used_tool.condition <= 0:
                            self.player.inventory.items.remove(used_tool)
                            logs.append(f"!!! DEIN WERKZEUG ({used_tool.name}) IST ZERBROCHEN !!!")
                else:
                    logs.append(f"Inventar voll für {item.name}.")
        
        return logs if logs else ["Nichts gefunden."]

    def execute_experiment(self, selected_items: List[Item]) -> Dict[str, Any]:
        """Systemic Crafting Check."""
        for bp in self.blueprints:
            if len(selected_items) != len(bp.slots): continue

            for p in itertools.permutations(selected_items):
                mapping = {}
                match = True
                slot_keys = list(bp.slots.keys())
                for i, slot in enumerate(slot_keys):
                    if bp.slots[slot] not in p[i].tags:
                        match = False; break
                    mapping[slot] = p[i]
                
                if match: return self._create_tool(bp, mapping)
        return {"success": False, "message": "Keine Kombination möglich."}

    def _create_tool(self, bp: ToolBlueprint, comp: Dict[str, Item]) -> Dict[str, Any]:
        # Haltbarkeit = Schwächstes Glied
        durability_attr = min(c.get_attr("durability", 0.5) for c in comp.values())
        # Power = Kopf-Schärfe
        main = comp.get("head") or comp.get("blade")
        power = main.get_attr("sharpness", 0.1) * bp.base_efficiency
        
        name = f"{main.name}-{bp.result_name} ({comp.get('handle').name})"
        new_tool = Item(
            name=name, base_weight=sum(c.base_weight for c in comp.values()),
            tags={"DURABILITY": durability_attr},
            attributes={"durability": durability_attr, "power": power},
            condition=1.0
        )
        if bp.id == "axe": new_tool.tags["CHOPPING"] = power
        if bp.id == "knife": new_tool.tags["CUTTING"] = power

        for c in comp.values(): self.player.inventory.items.remove(c)
        self.player.inventory.add(new_tool)
        return {"success": True, "message": f"Erschaffen: {name} (Qualität: {durability_attr})"}

    def _advance_time(self, ticks: int):
        self.tick_counter += ticks
        self.player.energy -= (2.0 * ticks)

    def travel(self, tid: str):
        if tid not in self.locations: return "Ziel unbekannt."
        self.current_location_id = tid
        self._advance_time(3)
        return f"Gereist nach {self.locations[tid].name}."