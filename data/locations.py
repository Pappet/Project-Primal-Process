"""
data/locations.py
Hier wird definiert, wie die Welt aussieht. 
Locations enthalten 'ResourceNodes', keine direkten Items.
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ResourceNode:
    """Ein Vorkommen an einem Ort (z.B. ein Erzbett oder ein Hasenbau)."""
    result_template_id: str # Referenz-ID für das Item
    min_qty: int
    max_qty: int
    chance: float           # 0.0 - 1.0
    req_perception: float = 0.0
    req_tool_tag: Optional[str] = None
    
@dataclass
class LocationDef:
    """Die statische Definition eines Ortes."""
    id: str
    name: str
    description: str
    nodes: List[ResourceNode] = field(default_factory=list)

# --- DIE WELT DATEN ---

def get_all_locations() -> List[LocationDef]:
    """Factory-Funktion, die die Welt-Daten zurückgibt."""
    return [
        LocationDef(
            id="forest_edge",
            name="Waldrand",
            description="Ein lichter Mischwald. Sonnenlicht dringt durch die Baumkronen.",
            nodes=[
                # Trivial: Stöcke finden (80% Chance)
                ResourceNode("stick", 1, 3, 0.8), 
                # Trivial: Steine
                ResourceNode("pebble", 1, 2, 0.5),
                # Skill: Beeren (Braucht Wahrnehmung 2)
                ResourceNode("berries", 2, 5, 0.6, req_perception=2.0),
                # Tool: Holz hacken (Braucht Axt)
                ResourceNode("log_oak", 1, 1, 1.0, req_tool_tag="CHOPPING") 
            ]
        ),
        LocationDef(
            id="river_bank",
            name="Flussufer",
            description="Der Boden ist weich und lehmig. Das Wasser ist kalt.",
            nodes=[
                ResourceNode("clay_lump", 1, 3, 0.7, req_tool_tag="SHOVEL"),
                ResourceNode("reeds", 2, 6, 0.9) # Schilf
            ]
        )
    ]