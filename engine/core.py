"""
engine/core.py
Das Herzstück der Simulation. Verwaltet den Game-Loop, 
die Welt-Interaktionen und das systemische Experimentier-System.
"""

import random
import itertools
from typing import List, Dict, Any, Optional

# Importe aus unseren anderen Modulen
from engine.components import Player, Item
from data.locations import get_all_locations
from data.items import create_item, TEMPLATE_DB

@dataclass
class Blueprint:
    """Definiert eine funktionale Anforderung für ein Werkzeug."""
    id: str
    result_name: str
    # Slots definieren: "Welcher Tag wird für diesen Teil benötigt?"
    # Beispiel: {"head": "HARD", "handle": "RIGID", "binding": "FIBER"}
    slots: Dict[str, str]
    base_efficiency: float

class GameEngine:
    def __init__(self):
        self.player = Player("Survivor")
        self.locations = {loc.id: loc for loc in get_all_locations()}
        
        # Statische Daten laden
        self.blueprints = self._initialize_blueprints()
        
        # Start-Zustand
        self.current_location_id = "forest_edge"
        self.tick_counter = 0
        
        # Start-Ausrüstung für Tests (kann später entfernt werden)
        # self.player.inventory.add(create_item("stone_axe"))

    def _initialize_blueprints(self) -> List[Blueprint]:
        """Definiert die 'physikalischen Baupläne' der Welt."""
        return [
            Blueprint(
                id="axe",
                result_name="Axt",
                slots={"head": "HARD", "handle": "RIGID", "binding": "FIBER"},
                base_efficiency=1.0
            ),
            Blueprint(
                id="knife",
                result_name="Messer",
                slots={"blade": "SHARP", "handle": "RIGID"},
                base_efficiency=0.8
            )
        ]

    @property
    def current_location(self):
        return self.locations[self.current_location_id]

    # --- WELT INTERAKTIONEN ---

    def travel(self, target_id: str) -> str:
        """Wechselt den Ort und berechnet den Zeitverbrauch."""
        if target_id not in self.locations:
            return f"Ort '{target_id}' existiert nicht."
        
        self.current_location_id = target_id
        self._advance_time(ticks=3) # Reisen dauert 30 Minuten
        return f"Du bist nun am Ort: {self.locations[target_id].name}."

    def gather(self) -> List[str]:
        """Sammelt Ressourcen basierend auf Wahrscheinlichkeiten und Tools."""
        loc = self.current_location
        logs = []
        self._advance_time(ticks=1)

        for node in loc.nodes:
            # Check: Wahrnehmung
            if self.player.stats["perception"] < node.req_perception:
                continue
            
            # Check: Werkzeug (Sucht im Inventar nach dem benötigten Tag)
            if node.req_tool_tag:
                if not self.player.inventory.find_item_by_tag(node.req_tool_tag):
                    continue

            # Check: Würfelwurf
            if random.random() <= node.chance:
                qty = random.randint(node.min_qty, node.max_qty)
                new_item = create_item(node.result_template_id, quantity=qty)
                
                if self.player.inventory.add(new_item):
                    logs.append(f"Gefunden: {qty}x {new_item.name}")
                else:
                    logs.append(f"Inventar voll! Konnte {new_item.name} nicht tragen.")
        
        return logs if logs else ["Nichts Nützliches gefunden."]

    # --- DAS SYSTEMISCHE EXPERIMENTIER-SYSTEM ---

    def execute_experiment(self, selected_items: List[Item]) -> Dict[str, Any]:
        """
        Prüft, ob eine Kombination von Items ein neues Werkzeug ergibt.
        Nutzt Permutationen, um Items den Slots zuzuordnen.
        """
        if not selected_items:
            return {"success": False, "message": "Keine Items ausgewählt."}

        # Wir prüfen jeden Bauplan
        for bp in self.blueprints:
            # Anzahl der Items muss exakt mit Slot-Anzahl übereinstimmen
            if len(selected_items) != len(bp.slots):
                continue

            # Wir testen alle Kombinationen (Permutationen) der Items gegen die Slots
            slot_keys = list(bp.slots.keys())
            for permutation in itertools.permutations(selected_items):
                match = True
                mapping = {}
                
                for idx, slot_key in enumerate(slot_keys):
                    required_tag = bp.slots[slot_key]
                    if required_tag not in permutation[idx].tags:
                        match = False
                        break
                    mapping[slot_key] = permutation[idx]

                if match:
                    # Erfolg! Wir haben eine gültige Kombination gefunden
                    return self._create_dynamic_tool(bp, mapping)

        return {"success": False, "message": "Diese Kombination ergibt keinen Sinn."}

    def _create_dynamic_tool(self, bp: Blueprint, components: Dict[str, Item]) -> Dict[str, Any]:
        """Berechnet die Attribute des neuen Items aus seinen Komponenten."""
        
        # 1. Haltbarkeit (Schwächstes Glied bestimmt das Ergebnis)
        # Wir greifen auf die 'durability' in den Attributen zu
        durability = min(c.attributes.get("durability", 0.5) for c in components.values())
        
        # 2. Effizienz (Der Kopf/Klinge bestimmt die Stärke)
        # Wir nehmen an, der Slot 'head' oder 'blade' ist primär
        main_part = components.get("head") or components.get("blade")
        power = main_part.attributes.get("sharpness", 0.1) * bp.base_efficiency

        # 3. Das neue Item Objekt bauen
        # Name dynamisch generieren
        new_name = f"{main_part.name}-{bp.result_name} ({components.get('handle').name})"
        
        new_tool = Item(
            name=new_name,
            base_weight=sum(c.base_weight for c in components.values()),
            tags={"DURABILITY": durability},
            attributes={"durability": durability, "power": power}
        )
        
        # Den spezifischen Tool-Tag hinzufügen (z.B. CHOPPING für Äxte)
        if bp.id == "axe": new_tool.tags["CHOPPING"] = power
        if bp.id == "knife": new_tool.tags["CUTTING"] = power

        # 4. Ressourcen verbrauchen und Zeit voranschreiten
        # TODO: Inventar-Methode schreiben, die selektierte Instanzen löscht
        for comp in components.values():
            self.player.inventory.items.remove(comp)

        self.player.inventory.add(new_tool)
        self._advance_time(ticks=5) # Crafting dauert 50 Min

        return {
            "success": True, 
            "message": f"Du hast ein neues Werkzeug erschaffen: {new_name}!"
        }

    def _advance_time(self, ticks: int):
        """Berechnet den Einfluss der Zeit auf den biologischen Spieler."""
        self.tick_counter += ticks
        # Einfacher Energieverbrauch pro Tick
        self.player.energy -= (2.0 * ticks)
        # TODO: Hier Thermodynamik aus player.py integrieren