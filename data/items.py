"""
data/items.py
Template-Datenbank — geladen aus items.json.
"""
from engine.components import Item
from data.loader import load_items

TEMPLATE_DB = load_items()


def create_item(template_id: str, quantity: int = 1) -> Item:
    data = TEMPLATE_DB.get(template_id)
    if not data:
        return Item("Unbekannt", 0.1)
    return Item(
        name=data.name,
        base_weight=data.weight,
        tags=data.tags.copy(),
        attributes=data.attributes.copy(),
        quantity=quantity
    )