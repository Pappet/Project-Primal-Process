"""
engine/components.py
Erweiterte Entitäten mit Thermodynamik-Attributen.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set

@dataclass
class Item:
    name: str
    base_weight: float
    tags: Dict[str, Any] = field(default_factory=dict)
    quantity: int = 1
    condition: float = 1.0 
    attributes: Dict[str, float] = field(default_factory=dict)

    @property
    def total_weight(self):
        return self.base_weight * self.quantity

    def get_attr(self, key: str, default: float = 0.0) -> float:
        return self.attributes.get(key, default)

@dataclass
class ToolBlueprint:
    id: str
    result_name: str
    slots: Dict[str, str]
    base_efficiency: float
    min_survival_req: float = 0.0

@dataclass
class Inventory:
    capacity_kg: float = 20.0
    items: List[Item] = field(default_factory=list)

    @property
    def current_weight(self) -> float:
        return sum(i.total_weight for i in self.items)

    def add(self, new_item: Item) -> bool:
        if self.current_weight + new_item.total_weight > self.capacity_kg:
            return False
        for existing in self.items:
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

    def get_total_insulation(self) -> float:
        """Summiert die Isolationswerte aller getragenen/vorhandenen Kleidung."""
        return sum(it.get_attr("insulation", 0.0) for it in self.items if "CLOTHING" in it.tags)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = Inventory()
        self.stats = {"perception": 1.0, "strength": 1.0, "survival": 1.0}
        
        # Vitalwerte
        self.max_energy = 1000.0
        self.energy = 800.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.body_temp = 37.0  # Celsius
        
        self.known_blueprints: Set[str] = set()