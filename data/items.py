"""
data/items.py
Template-Datenbank.
"""
from engine.components import Item

TEMPLATE_DB = {
    # --- ROHSTOFFE ---
    "stick": {"name": "Eichenast", "weight": 0.5, "tags": {"RIGID": True}, "attributes": {"durability": 0.8}},
    "flint_shard": {"name": "Feuersteinsplitter", "weight": 0.4, "tags": {"HARD": True, "SHARP": True}, "attributes": {"sharpness": 0.9, "durability": 0.4}},
    "plant_fiber": {"name": "Pflanzenfaser", "weight": 0.05, "tags": {"FIBER": True}, "attributes": {"durability": 0.5}},
    "reeds": {"name": "Schilfrohr", "weight": 0.1, "tags": {"RIGID": True, "FIBER": True}, "attributes": {"durability": 0.1}},
    
    # --- NAHRUNG ---
    "berries": {"name": "Waldbeeren", "weight": 0.1, "tags": {"EDIBLE": 50}},
    "mushroom": {"name": "Wildpilz", "weight": 0.1, "tags": {"EDIBLE": 30}},
    "raw_meat": {"name": "Rohes Fleisch", "weight": 0.5, "tags": {"EDIBLE": 150}}, # Risiko von Parasiten (später)
    "cooked_meat": {"name": "Gebratenes Fleisch", "weight": 0.4, "tags": {"EDIBLE": 400}}
}

def create_item(template_id: str, quantity: int = 1) -> Item:
    data = TEMPLATE_DB.get(template_id)
    if not data: return Item("Unbekannt", 0.1)
    return Item(
        name=data["name"],
        base_weight=data["weight"],
        tags=data["tags"].copy(),
        attributes=data.get("attributes", {}).copy(),
        quantity=quantity
    )