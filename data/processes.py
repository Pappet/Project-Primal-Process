"""
data/processes.py
Definiert, wie Items in andere Items umgewandelt werden.
ProcessDefs werden aus processes.json geladen (keine hartkodierten Dicts).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from data.loader import load_processes


@dataclass
class ProcessDef:
    id: str
    name: str
    inputs: Dict[str, int]          # item_id : menge
    tools: List[str]                # Benötigte Tags (z.B. "CUTTING")
    outputs: Dict[str, int]         # item_id : menge
    duration_ticks: int
    required_tag_in_env: Optional[str] = None  # z.B. "HEAT_SOURCE" für Kochen


def get_all_processes() -> List[ProcessDef]:
    return [
        ProcessDef(
            id=p.id,
            name=p.name,
            inputs=p.inputs,
            tools=p.tools,
            outputs=p.outputs,
            duration_ticks=p.duration_ticks,
            required_tag_in_env=p.required_tag_in_env,
        )
        for p in load_processes()
    ]
