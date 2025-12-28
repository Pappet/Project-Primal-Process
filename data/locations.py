"""
data/locations.py
Erweiterte Locations mit Temperatur-Daten.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ResourceNode:
    result_template_id: str
    min_qty: int
    max_qty: int
    chance: float
    req_perception: float = 0.0
    req_tool_tag: Optional[str] = None
    
@dataclass
class LocationDef:
    id: str
    name: str
    description: str
    base_temp: float  # Durchschnittstemperatur am Tag
    exposure: float   # 0.0 (geschützt/Höhle) bis 1.0 (offenes Feld)
    nodes: List[ResourceNode] = field(default_factory=list)

def get_all_locations() -> List[LocationDef]:
    return [
        LocationDef(
            id="forest_edge",
            name="Waldrand",
            description="Lichter Mischwald. Die Bäume bieten etwas Schutz vor Wind.",
            base_temp=15.0,
            exposure=0.5,
            nodes=[
                ResourceNode("stick", 1, 3, 0.8),
                ResourceNode("berries", 2, 5, 0.6, req_perception=2.0),
                ResourceNode("log_oak", 1, 1, 1.0, req_tool_tag="CHOPPING")
            ]
        ),
        LocationDef(
            id="mountain_peak",
            name="Gipfelkamm",
            description="Kalt, windig und absolut ungeschützt.",
            base_temp=2.0,
            exposure=1.0,
            nodes=[
                ResourceNode("flint_shard", 1, 2, 0.4, req_perception=1.5),
                ResourceNode("pebble", 2, 4, 0.8)
            ]
        ),
        LocationDef(
            id="hidden_cave",
            name="Kleine Höhle",
            description="Dunkel, aber trocken und windstill.",
            base_temp=10.0,
            exposure=0.1,
            nodes=[
                ResourceNode("clay_lump", 1, 2, 0.5, req_tool_tag="SHOVEL"),
                ResourceNode("mushroom", 1, 3, 0.7, req_perception=2.0)
            ]
        )
    ]