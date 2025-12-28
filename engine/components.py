"""
engine/components.py
Kern-Entitäten der Simulation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Item:
    """Repräsentiert eine Instanz eines Gegenstands."""
    name: str
    base_weight: float
    tags: Dict[str, Any] = field(default_factory=dict)
    quantity: int = 1
    
    # Zustand (1.0 = Neu, 0.0 = Kaputt)
    condition: float = 1.0
    
    # Material-Attribute (z.B. {"durability": 0.8, "sharpness": 0.5})
    attributes: Dict[str, float] = field(default_factory=dict)

    @property
    def total_weight(self):
        return self.base_weight * self.quantity

    def has_tag(self, tag_key: str) -> bool:
        return tag_key in self.tags

    def get_attr(self, key: str, default: float = 0.0) -> float:
        return self.attributes.get(key, default)

@dataclass
class ToolBlueprint:
    """Anforderungsprofil für ein experimentelles Werkzeug."""
    id: str
    result_name: str
    slots: Dict[str, str] # Slot-Name : Benötigter Tag
    base_efficiency: float

@dataclass
class Inventory:
    """Verwaltet Items und deren Stapelung."""
    capacity_kg: float = 20.0
    items: List[Item] = field(default_factory=list)

    @property
    def current_weight(self) -> float:
        return sum(i.total_weight for i in self.items)

    def add(self, new_item: Item) -> bool:
        if self.current_weight + new_item.total_weight > self.capacity_kg:
            return False
            
        for existing in self.items:
            # Stapeln nur, wenn Name UND Zustand gleich sind
            if existing.name == new_item.name and existing.condition == new_item.condition:
                existing.quantity += new_item.quantity
                return True
        
        self.items.append(new_item)
        return True

    def find_item_by_tag(self, tag: str) -> Optional[Item]:
        for item in self.items:
            if tag in item.tags and item.condition > 0:
                return item
        return None

    def remove_resources(self, requirements: Dict[str, int]) -> bool:
        """Entfernt Mengen von Items (für Crafting)."""
        for item_name, qty in requirements.items():
            to_remove = qty
            for i in range(len(self.items) - 1, -1, -1):
                item = self.items[i]
                if item.name == item_name:
                    if item.quantity <= to_remove:
                        to_remove -= item.quantity
                        self.items.pop(i)
                    else:
                        item.quantity -= to_remove
                        to_remove = 0
                if to_remove <= 0: break
        return True

class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = Inventory()
        self.stats = {"perception": 1.0, "strength": 1.0}
        self.energy = 1000.0
        self.hp = 100.0