"""
data/blueprints.py
Baupläne für das Experimentier-System.
"""
from engine.components import ToolBlueprint

def get_all_blueprints():
    return [
        ToolBlueprint(
            id="axe",
            result_name="Axt",
            slots={"head": "HARD", "handle": "RIGID", "binding": "FIBER"},
            base_efficiency=1.0
        ),
        ToolBlueprint(
            id="knife",
            result_name="Messer",
            slots={"blade": "SHARP", "handle": "RIGID"},
            base_efficiency=0.8
        )
    ]