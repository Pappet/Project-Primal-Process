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
    template_id: str = ""

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
    tool_tags: List[str] = field(default_factory=list)

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
        # survival startet bei 0.0 und wächst ausschließlich durch Discovery
        # (+0.2 je erstmals entdecktem Blueprint, +0.1 je Prozess) — das macht
        # den `min_survival_req`-Gate (SPEC-008) real: Tier-2-Blueprints sind
        # erst nach einer Mindestzahl entdeckter Tier-1-Baupläne versuchbar.
        # (Vorher 1.0 → der Gate war tot: jeder Frischling erfüllte 0.4/0.6.)
        self.stats = {"perception": 1.0, "strength": 1.0, "survival": 0.0}
        
        # Vitalwerte
        self.max_energy = 1000.0
        self.energy = 800.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.body_temp = 37.0  # Celsius
        
        self.known_blueprints: Set[str] = set()
        self.known_processes: Set[str] = set()
        # SPEC-003: Experimentiergedächtnis für Beinahe-Treffer. Blueprint-IDs,
        # für die der Spieler schon einmal eine latente ≥2/3-Teilkombination
        # gemeldet bekommen hat (NEAR_MISS). Der Hinweis feuert pro Blueprint
        # genau einmal — danach still bis zum echten Craft (keine Dauer-Belehrung).
        self.near_misses: Set[str] = set()
        # SPEC-006: Experimentiergedächtnis für gebaute Werkzeuge. Registriert
        # die tool_tag-Namen aller je gebauten Werkzeuge — der Don't-Starve-
        # Prototyper-Effekt: wer ein Werkzeug erstmals gebaut hat, bekommt genau
        # einmal den generischen Hinweis, dass es sich noch mit etwas anderem
        # verbinden lässt (kein Rezept-Leak). Pro Tag genau einmal — danach still,
        # analog der SPEC-003-Einmaligkeit.
        self.known_components: Set[str] = set()
        # SPEC-009: Persistente Verletzungen (Zustand, kein einmaliger HP-Abzug).
        # Jede Wunde trägt severity (Stärke, startet 1.0), ticks (seit Entstehung)
        # und treated (Behandlung angelegt? Verband/Umschlag). Pro-Instanz — eine
        # frische GameEngine baut ein frisches Player-Objekt, kein Cross-Session-
        # Bleed. `cut` blutet unbehandelt über Zeit; `strain` ist ein Effort-Malus.
        self.injuries: Dict[str, Dict[str, Any]] = {}