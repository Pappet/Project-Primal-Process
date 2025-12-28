"""
engine/components.py
Definiert die grundlegenden Bausteine der Simulation (Entities).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Item:
    """Repräsentiert eine konkrete Instanz eines Gegenstands."""
    name: str
    base_weight: float
    tags: Dict[str, Any] = field(default_factory=dict)
    quantity: int = 1
    
    # NEU: Material-Eigenschaften für die Berechnung
    # Beispiele: {"durability": 0.2, "sharpness": 0.8}
    attributes: Dict[str, float] = field(default_factory=dict)

    @property
    def total_weight(self):
        return self.base_weight * self.quantity

    def has_tag(self, tag_key: str) -> bool:
        return tag_key in self.tags

    def get_attr(self, key: str, default: float = 0.0) -> float:
        return self.attributes.get(key, default)


@dataclass
class Inventory:
    """Verwaltet Items und Kapazitäten."""
    capacity_kg: float = 20.0
    items: List[Item] = field(default_factory=list)

    @property
    def current_weight(self) -> float:
        return sum(i.total_weight for i in self.items)

    def add(self, new_item: Item) -> bool:
        """Fügt Item hinzu. Versucht zu stapeln (stacking) wenn möglich."""
        if self.current_weight + new_item.total_weight > self.capacity_kg:
            return False
            
        # Versuch, existierenden Stapel zu finden
        for existing in self.items:
            if existing.name == new_item.name: # Vereinfachter Check über Namen
                existing.quantity += new_item.quantity
                return True
        
        self.items.append(new_item)
        return True

    def find_item_by_tag(self, tag: str) -> Optional[Item]:
        """Hilfreich um zu prüfen: Hat der Spieler ein Werkzeug?"""
        for item in self.items:
            if tag in item.tags:
                return item
        return None
    
    def count_item(self, item_name_id: str) -> int:
        """Zählt die Gesamtmenge eines Items im Inventar."""
        return sum(item.quantity for item in self.items if item.name == item_name_id)

    def has_resources(self, requirements: Dict[str, int]) -> bool:
        """Prüft, ob alle benötigten Ressourcen in der Menge vorhanden sind."""
        for item_id, required_qty in requirements.items():
            if self.count_item(item_id) < required_qty:
                return False
        return True

    def remove_resources(self, requirements: Dict[str, int]) -> bool:
        """
        Entfernt Ressourcen. Sollte nur nach has_resources aufgerufen werden.
        """
        for item_id, required_qty in requirements.items():
            to_remove = required_qty
            # Wir gehen rückwärts durch, um Items beim Löschen nicht zu überspringen
            for i in range(len(self.items) - 1, -1, -1):
                item = self.items[i]
                if item.name == item_id:
                    if item.quantity <= to_remove:
                        to_remove -= item.quantity
                        self.items.pop(i)
                    else:
                        item.quantity -= to_remove
                        to_remove = 0
                if to_remove <= 0:
                    break
        return True

class Player:
    """Der Spieler mit Stats und Inventar."""
    def __init__(self, name: str):
        self.name = name
        self.inventory = Inventory()
        
        # Stats (0.0 bis 100.0)
        self.stats = {
            "perception": 1.0,  # Wahrnehmung
            "strength": 1.0,    # Kraft
            "survival": 1.0     # Wissen
        }
        
        # Vitalwerte
        self.energy = 1000.0
        self.hp = 100.0