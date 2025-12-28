from engine.components import Item

TEMPLATE_DB = {
    # --- ROHSTOFFE ---
    "stick": {
        "name": "Eichenast", "weight": 0.5, 
        "tags": {"RIGID": True}, 
        "attributes": {"durability": 0.8} # Stabil
    },
    "reeds": {
        "name": "Schilfrohr", "weight": 0.1, 
        "tags": {"RIGID": True, "FIBER": True}, 
        "attributes": {"durability": 0.1} # Bricht sofort
    },
    "flint_shard": {
        "name": "Feuersteinsplitter", "weight": 0.4, 
        "tags": {"HARD": True, "SHARP": True}, 
        "attributes": {"sharpness": 0.9, "durability": 0.4}
    },
    "bone_fragment": {
        "name": "Knochensplitter", "weight": 0.3, 
        "tags": {"HARD": True, "RIGID": True}, 
        "attributes": {"sharpness": 0.4, "durability": 0.6}
    },
    "plant_fiber": {
        "name": "Pflanzenfaser", "weight": 0.05, 
        "tags": {"FIBER": True}, 
        "attributes": {"durability": 0.5}
    },
    "pebble": {
        "name": "Kieselstein", 
        "weight": 0.1, 
        "tags": {"THROWABLE": True}
    },
    "berries": {
        "name": "Waldbeeren", 
        "weight": 0.05, 
        "tags": {"EDIBLE": 20}
    },
    "log_oak": {
        "name": "Eichenstamm", 
        "weight": 5.0, 
        "tags": {"BURNABLE": 500, 
                 "WOOD": True}
    },
    "clay_lump": {
        "name": "Lehmklumpen", 
        "weight": 1.0, 
        "tags": {"MOLDABLE": True}
    },
    
    # Tools (zum Testen geben wir dem Spieler gleich eins)
    "stone_axe": {"name": "Primitive Axt", "weight": 1.5, "tags": {"CHOPPING": 1.0}},
    "sharp_stone": {"name": "Scharfer Stein", "weight": 0.3, "tags": {"CUTTING": 0.5}},
    "hand_drill": {"name": "Handbohrer (Holz)", "weight": 0.2, "tags": {"KINDLING": 1.0}},
    "tinder": {"name": "Zunder", "weight": 0.01, "tags": {"FUEL": 1, "IGNITABLE": True}},
    "fire_pit": {"name": "Lagerfeuer", "weight": 0.0, "tags": {"HEAT_SOURCE": 400}}, # Ein stationäres Item
}

def create_item(template_id: str, quantity: int = 1) -> Item:
    """Factory Pattern: Erstellt ein echtes Item aus der Template-ID."""
    data = TEMPLATE_DB.get(template_id)
    if not data:
        return Item("ERROR_ITEM", 0.0)
    
    return Item(
        name=data["name"],
        base_weight=data["weight"],
        tags=data["tags"].copy(), # Copy ist wichtig, damit wir Tags modifizieren können ohne das Template zu ändern!
        quantity=quantity
    )