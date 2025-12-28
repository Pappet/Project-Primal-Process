"""
data/items.py
Template-Datenbank für alle Rohstoffe und Basis-Items.
"""
from engine.components import Item

TEMPLATE_DB = {
    "stick": {
        "name": "Eichenast", "weight": 0.5, 
        "tags": {"RIGID": True, "BURNABLE": 50}, 
        "attributes": {"durability": 0.8}
    },
    "reeds": {
        "name": "Schilfrohr", "weight": 0.1, 
        "tags": {"RIGID": True, "FIBER": True}, 
        "attributes": {"durability": 0.1}
    },
    "flint_shard": {
        "name": "Feuersteinsplitter", "weight": 0.4, 
        "tags": {"HARD": True, "SHARP": True}, 
        "attributes": {"sharpness": 0.9, "durability": 0.4}
    },
    "plant_fiber": {
        "name": "Pflanzenfaser", "weight": 0.05, 
        "tags": {"FIBER": True}, 
        "attributes": {"durability": 0.5}
    },
    "pebble": {
        "name": "Kieselstein", "weight": 0.1, 
        "tags": {"HARD": True, "THROWABLE": True},
        "attributes": {"durability": 1.0}
    },
    "log_oak": {
        "name": "Eichenstamm", "weight": 5.0, 
        "tags": {"WOOD": True, "BURNABLE": 500},
        "attributes": {"durability": 1.0}
    }
}

def create_item(template_id: str, quantity: int = 1) -> Item:
    data = TEMPLATE_DB.get(template_id)
    if not data: return Item("Unbekanntes Objekt", 0.1)
    
    return Item(
        name=data["name"],
        base_weight=data["weight"],
        tags=data["tags"].copy(),
        attributes=data.get("attributes", {}).copy(),
        quantity=quantity
    )