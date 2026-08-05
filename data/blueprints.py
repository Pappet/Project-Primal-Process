"""
data/blueprints.py
Baupläne für das Experimentier-System — geladen aus blueprints.json.
"""
from engine.components import ToolBlueprint
from data.loader import load_blueprints


def get_all_blueprints():
    return [
        ToolBlueprint(
            id=bp.id,
            result_name=bp.result_name,
            slots=bp.slots,
            base_efficiency=bp.base_efficiency,
            min_survival_req=bp.min_survival_req,
            tool_tags=list(bp.tool_tags),
        )
        for bp in load_blueprints()
    ]