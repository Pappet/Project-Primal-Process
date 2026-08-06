"""
data/locations.py
Erweiterte Locations mit Temperatur-Daten — geladen aus locations.json.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from data.loader import load_locations, ResourceNodeData


@dataclass
class ResourceNode:
    result_template_id: str
    min_qty: int
    max_qty: int
    chance: float
    req_perception: float = 0.0
    req_tool_tag: Optional[str] = None
    # Vorratsbasierte Nodes (SPEC-004): Ernte reduziert den Vorrat, Regeneration
    # über verstrichene Spielzeit. `stock` ist veränderlicher Zustand und wird
    # pro Instanz frisch auf max_stock initialisiert (kein Cross-Session-Bleed).
    max_stock: float = 10.0
    regen_per_tick: float = 0.05
    harvest_cost: float = 1.0
    stock: float = 0.0
    # `depleted` ist ein ehrlicher Zustand für den Spieler: einmal bis unter
    # eine Ernte-Portion geleert, bleibt der Node erschöpft und meldet das,
    # bis verstrichene Zeit (Regeneration) mindestens eine Portion wieder
    # aufgefüllt hat. So übersteht er nicht still, nur weil ein einzelner
    # Gather-Tick eine homöopathische Menge nachschiebt.
    depleted: bool = False

    def __post_init__(self):
        self.stock = self.max_stock
        self.depleted = False


@dataclass
class LocationDef:
    id: str
    name: str
    description: str
    base_temp: float
    exposure: float
    nodes: List[ResourceNode] = field(default_factory=list)


def _node_from_data(n: ResourceNodeData) -> ResourceNode:
    return ResourceNode(
        result_template_id=n.result_template_id,
        min_qty=n.min_qty,
        max_qty=n.max_qty,
        chance=n.chance,
        req_perception=n.req_perception,
        req_tool_tag=n.req_tool_tag,
        max_stock=n.max_stock,
        regen_per_tick=n.regen_per_tick,
        harvest_cost=n.harvest_cost,
    )


def get_all_locations() -> List[LocationDef]:
    return [
        LocationDef(
            id=loc.id,
            name=loc.name,
            description=loc.description,
            base_temp=loc.base_temp,
            exposure=loc.exposure,
            nodes=[_node_from_data(n) for n in loc.nodes],
        )
        for loc in load_locations()
    ]