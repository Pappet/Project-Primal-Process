import itertools
from typing import List, Dict, Optional
from engine.components import Item

class Blueprint:
    def __init__(self, id_name, result_name, slots: Dict[str, str]):
        self.id = id_name
        self.result_name = result_name
        self.slots = slots # z.B. {"head": "HARD", "handle": "RIGID", "binding": "FIBER"}

def try_combine(items: List[Item], blueprints: List[Blueprint]) -> Optional[Item]:
    """Prüft, ob eine Liste von Items auf einen Bauplan passt."""
    for bp in blueprints:
        if len(items) != len(bp.slots):
            continue
        
        # Wir prüfen alle Permutationen, falls ein Item mehrere Tags hat
        for p in itertools.permutations(items):
            match = True
            slot_mapping = {}
            
            for i, slot_name in enumerate(bp.slots.keys()):
                required_tag = bp.slots[slot_name]
                if required_tag not in p[i].tags:
                    match = False
                    break
                slot_mapping[slot_name] = p[i]
            
            if match:
                return create_dynamic_item(bp, slot_mapping)
    return None

def create_dynamic_item(bp: Blueprint, components: Dict[str, Item]) -> Item:
    # 1. Haltbarkeit berechnen (Das schwächste Glied bestimmt den Wert)
    durability = min(c.get_attr("durability", 0.5) for c in components.values())

    # 2. Effizienz: erster Slot mit sharpness oder Fallback
    comp_list = list(components.values())
    primary = comp_list[0] if comp_list else Item("Empty", 0)
    power = 0.1
    for c in comp_list:
        if c.get_attr("sharpness", 0.0) > 0:
            power = c.get_attr("sharpness", 0.1)
            break

    # 3. Dynamischer Name aus den Komponenten
    name_parts = [c.name for c in comp_list]
    if len(name_parts) >= 2:
        name = f"{name_parts[0]}-{bp.result_name} ({name_parts[1]})"
    else:
        name = f"{name_parts[0]}-{bp.result_name}" if name_parts else bp.result_name

    return Item(
        name=name,
        base_weight=sum(c.base_weight for c in comp_list),
        tags={"CHOPPING": power, "DURABILITY": durability},
        attributes={"durability": durability, "power": power}
    )