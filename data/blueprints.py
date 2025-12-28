"""
data/blueprints.py
Definiert 'Baupläne', die Anforderungen an Tags stellen, statt an feste Items.
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ToolBlueprint:
    id: str
    name: str
    # Welche 'Slots' hat das Werkzeug und welche Tags müssen die Items darin haben?
    slots: Dict[str, str]  # Slot-Name : Benötigter Tag
    base_efficiency: float

# Beispiel für eine Axt
AXE_BLUEPRINT = ToolBlueprint(
    id="primitive_axe",
    name="Axt",
    slots={
        "head": "HARD",      # Braucht etwas Hartes (Stein, Metall)
        "handle": "RIGID",   # Braucht einen Griff (Holz, Knochen, Schilf)
        "binding": "FIBER"   # Braucht eine Schnur (Darm, Bast, Schilf)
    },
    base_efficiency=1.0
)