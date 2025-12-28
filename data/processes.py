"""
data/processes.py
Definiert, wie Items in andere Items umgewandelt werden.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ProcessDef:
    id: str
    name: str
    inputs: Dict[str, int]          # item_id : menge
    tools: List[str]                # Benötigte Tags (z.B. "CUTTING")
    outputs: Dict[str, int]         # item_id : menge
    duration_ticks: int
    required_tag_in_env: Optional[str] = None # z.B. "HEAT_SOURCE" für Kochen

def get_all_processes() -> List[ProcessDef]:
    return [
        ProcessDef(
            id="make_sharp_stone",
            name="Stein schlagen (Knapping)",
            inputs={"pebble": 2},
            tools=[], # Man schlägt Steine gegeneinander
            outputs={"sharp_stone": 1},
            duration_ticks = 2
        ),
        ProcessDef(
            id="create_tinder",
            name="Zunder vorbereiten",
            inputs={"reeds": 2},
            tools=["CUTTING"],
            outputs={"tinder": 3},
            duration_ticks = 1
        ),
        ProcessDef(
            id="start_fire",
            name="Feuer bohren",
            inputs={"tinder": 1, "stick": 2},
            tools=["KINDLING"],
            outputs={"fire_pit": 1},
            duration_ticks = 5
        )
    ]