"""
engine/core.py
Zentrale Logik inklusive Wetter- und Temperatur-Simulation.
"""
import random
import itertools
from typing import List, Dict, Any
from engine.components import Player, Item, ToolBlueprint
from data.locations import get_all_locations
from data.items import create_item, TEMPLATE_DB
from data.blueprints import get_all_blueprints
from data.processes import get_all_processes

# Spielersprachliche Labels für Tags — die Brücke von internem Reason zu Text.
# Vollständig für alle im Spiel vorkommenden Tags (Konsistenz-Wächter in Tests).
TAG_LABELS = {
    "SHARP": "etwas Scharfes",
    "HARD": "etwas Hartes",
    "FLINT": "etwas aus Feuerstein",
    "BONE": "etwas aus Knochen",
    "FIBER": "etwas Faseriges",
    "RIGID": "etwas Festes",
    "STONE": "etwas Steinernes",
    "PROJECTILE": "etwas Wurfgeschossartiges",
    "EDIBLE": "etwas Essbares",
    "CHOPPING": "etwas zum Schneiden",
    "CUTTING": "etwas zum Schneiden",
    "PIERCE": "etwas zum Stechen",
    "CORD": "etwas zum Binden",
    "KINDLING": "etwas zum Feuermachen",
    "SHOVEL": "etwas zum Graben",
    "DURABILITY": "etwas Haltbares",
    "WOOD": "etwas aus Holz",
    "CLAY": "etwas aus Ton",
    "CLOTHING": "Kleidung",
    "HEAT_SOURCE": "eine Wärmequelle",
}

# Wärmemanagement (SPEC-007): Kennzahlen des Location-Feuers. Balanciert das
# System "aktives Feuer aus/tragbare Isolation" — die Gegen-Schleife zur sonst
# unaufhaltsamen Unterkühlung. Detail-Balance in Peters Sinne liegt beim Dev.
FIRE_HEAT = 40.0          # Wärmebeitrag des aktiven Feuers zur Umgebungstemperatur
START_FIRE_FUEL = 24.0    # Brennstoff-Ticks beim Entzünden (≈ 4 In-Game-Stunden)

# SPEC-011: Werkzeugverschleiß als lesbarer Zustand (Druck ohne Wahrnehmung).
# Threshold: darunter gilt ein Werkzeug als stark abgenutzt (einmalige Warnung
# pro fallendem Durchgang). Min-Factor: stumpfe Werkzeuge ernten gedämpft
# weiter (min Faktor), statt bis zum Bruch volle Chance zu liefern.
WEAR_WARN_THRESHOLD = 0.25
WEAR_MIN_FACTOR = 0.25

# Ziel-2-Hebel: Prozess-Potenzial-Hinweise. Besitz + Umgebung erzeugen ein
# einmaliges, generisches Richtungssignal pro Prozess-Klasse — das analoge
# Signal zum NEW_COMPONENT-Reveal (SPEC-006), das Werkzeug-Potenzial meldet.
# Kein Rezept-Leak: der Text nennt weder Item, Menge, Prozess-ID noch
# fehlende Tags — nur die Zweck-Kategorie. Kein neuer Reason-Code: der
# Hinweis ist eine Zusatz-Meldung im Logstream, `EMITTABLE_REASONS` und der
# feedback_quality-Kern bleiben unangetastet.
PROCESS_HINT_CATEGORY = {
    "make_sharp_stone": "bearbeiten",
    "create_tinder": "verarbeiten",
    "start_fire": "entzünden",
    "cook_meat": "zubereiten",
    "make_fur_cloak": "anfertigen",
    "make_bandage": "verbinden",
    "make_poultice": "wundbehandeln",
    "treat_cut": "wundbehandeln",
    "treat_strain": "wundbehandeln",
    "sharpen_tool": "instandhalten",
}
PROCESS_HINT_TEXT = {
    "bearbeiten": "Einiges davon ließe sich wohl weiter bearbeiten.",
    "verarbeiten": "Einiges davon ließe sich weiter verarbeiten — mit dem richtigen Werkzeug.",
    "entzünden": "Damit ließe sich hier etwas entzünden.",
    "zubereiten": "Hier ließe sich etwas zubereiten.",
    "anfertigen": "Damit ließe sich etwas anfertigen.",
    "verbinden": "Einiges davon ließe sich verbinden.",
    "wundbehandeln": "Damit ließe sich eine Wunde behandeln.",
    "instandhalten": "Damit ließe sich ein Werkzeug instand halten.",
}
SHARPEN_RESTORE = 0.5     # condition-Zugewinn durch sharpen_tool (cap 1.0)
SHARPEN_TOOL_TAGS = ("CUTTING", "CHOPPING", "PIERCE")
STOKE_FUEL = 8.0          # Brennstoff-Ticks, die nachgelegtes Holz/Machtsgut bringt

# Verletzung & Heilung (SPEC-009): pro-Instanz Wund-Zustand (Player.injuries)
# + handlungsgebundene Risikoquelle (Sammeln) + Behandlungs-/Ruhe-Gegenmechanik.
# Frequenz bewusst niedrig: über die KURZE Mess-Fenster der Discovery-Bots
# (~150 Aktionen) sollen die meisten Seeds unbeschadet bleiben (sonst fällt
# `discovery_gap` über Band), während ein lang spielender, unvorbereiteter
# Spieler Verletzungen schon spürt und die Behandlung lernen muss.
INJURE_CUT_CHANCE = 0.015   # pro Fund scharfen Materials (SHARP-Node) → Schnittwunde
INJURE_STRAIN_CHANCE = 0.02 # pro Sammeln am exponierten Ort (exposure ≥ 0.8) → Zerrung
CUT_BLEED_PER_TICK = 0.2    # unbehandelte Schnittwunde: HP-Verlust pro Tick
STRAIN_EFFORT_MALUS = 1.0   # unbehandelte Zerrung: Extra-Effort beim Sammeln
INJ_HEAL_RATE = 0.05        # Behandlung + Ruhe: severity-Regeneration pro Tick
INJ_HEAL_THRESHOLD = 0.05   # darunter gilt die Wunde als verheilt (entfernt)
REST_EXPOSURE = 0.15        # Ort gilt als "ruhig/sheltered", wenn exposure darunter

# Tag-Familien (SPEC-002): Eine Slot-Anforderung kann ein Familienname sein,
# der mehrere Tags subsumiert (Layer über den Einzel-Tags). Ein Item genügt der
# Familie, wenn es irgendeinen der Mitglieds-Tags trägt — so kann flint_shard
# (SHARP+HARD) oder ein harter Stab (RIGID) mehrere Rollen füllen.
TAG_FAMILIES = {
    "SHARP_OR_HARD": {"SHARP", "HARD"},
    "SHARP_OR_RIGID": {"SHARP", "RIGID"},
    "RIGID_OR_FIBER": {"RIGID", "FIBER"},
}


def _slot_satisfied(item_tags, slot_value: str) -> bool:
    """Prüft, ob die Tags eines Items einen Slot erfüllen (Familie o. Einzel-Tag).

    `item_tags` ist typischerweise ein Dict (Item.tags) oder ein Set (z.B. die
    ge-sammelte Tag-Menge in _no_match_reason). `&` zwischen set und dict wirft
    einen TypeError, daher Keywords explizit auslesen.
    """
    tags = item_tags.keys() if isinstance(item_tags, dict) else item_tags
    family = TAG_FAMILIES.get(slot_value)
    if family:
        return bool(family & set(tags))
    return slot_value in tags


def _label_for(tag: str) -> str:
    return TAG_LABELS.get(tag, f"etwas mit der Eigenschaft {tag}")


# Spielersprachliche Namen für Verletzungen (SPEC-009) — fürs Heil-Feedback.
INJURY_LABELS = {"cut": "Schnittwunde", "strain": "Zerrung"}


def _injury_label(kind: str) -> str:
    return INJURY_LABELS.get(kind, kind)


def _missing_tags(bp, available) -> list:
    """Repräsentierte fehlende Single-Tags eines Blueprints bzgl. der
    verfügbaren Tag-Menge. Familien-Slots werden auf ihren Ziel-Tag aufgelöst.
    Gibt die *fehlenden* Member zurück (leer → Voll-Treffer)."""
    missing = []
    for slot_value in bp.slots.values():
        required = set(TAG_FAMILIES.get(slot_value, {slot_value}))
        if not (required & available):
            missing.append(next(iter(required)))
    return missing


def _feedback_message(reason: str, broken_names: "List[str] | None" = None) -> str:
    """Baut eine spielersprachliche Meldung exakt aus dem Reason-Code.

    Verrät niemals mehr als der Reason hergibt — kein Rezept-Leaking. Wird der
    Code unkenntlich, gibt es eine generische (aber nicht lügende) Antwort.
    """
    if reason.startswith("MISSING_TAG:"):
        tag = reason.split(":", 1)[1]
        return f"Es fehlt dir {_label_for(tag)}."
    if reason == "TOO_FEW_ITEMS":
        return "Dafür brauchst du mindestens zwei Dinge."
    if reason == "NOT_ENOUGH_QUANTITY":
        return "Dafür brauchst du mehr von demselben Material."
    if reason == "BROKEN_ITEM":
        names = ", ".join(broken_names or [])
        return f"{names} ist zerbrochen und kann nicht verwendet werden."
    if reason == "NO_MATCH":
        return "Die Kombination ergibt nichts."
    if reason.startswith("NEAR_MISS:"):
        # SPEC-003: reines Ja/nein auf die gehaltene Teilmenge — bestätigt den
        # Weg, verrät weder das fehlende Item noch den Tag (kein Rezept-Leak).
        return "Einige dieser Dinge scheinen zusammenzugehören, aber es fehlt noch etwas."
    if reason == "DEPLETED":
        return "Diese Stelle ist erschöpft. Komm später zurück."
    if reason == "FIRE_OUT":
        return "Dein Feuer erlischt."
    if reason == "NO_FIRE":
        return "Hier brennt kein Feuer."
    if reason == "MISSING_FUEL":
        return "Es fehlt dir Brennholz zum Nachlegen."
    if reason == "MISSING_TOOL":
        return "Du brauchst ein Werkzeug dafür."
    if reason.startswith("MISSING_ENV:"):
        tag = reason.split(":", 1)[1]
        return f"Hier fehlt {_label_for(tag)} in der Umgebung."
    if reason == "NO_INJURY":
        return "Du bist nicht verletzt."
    if reason == "INJURED":
        # B08: gather()-Verletzung hat bisher den generischen Fallback gelesen.
        # Eigene Meldung, generisch (kein Rezept-/Mechanik-Leak).
        return "Du verletzt dich bei der Arbeit."
    if reason == "BLEEDING":
        # Generisch, kein Rezept-Leak: sagt nur, dass eine Behandlung fehlt,
        # nicht welche Kombination sie herstellt.
        return "Du blutest — die Wunde muss behandelt und du musst rasten."
    if reason == "TREATED":
        return "Die Wunde ist behandelt."
    if reason == "HEALED":
        return "Deine Wunde heilt."
    return "Das geht so nicht."  # UNKNOWN-Fallback — nie eine generische Leer-Meldung


class GameEngine:
    def __init__(self):
        self.player = Player("Survivor")
        self.locations = {loc.id: loc for loc in get_all_locations()}
        self.blueprints = {bp.id: bp for bp in get_all_blueprints()}
        self.processes = {p.id: p for p in get_all_processes()}
        self.current_location_id = "forest_edge"
        self.tick_counter = 36  # 6 Uhr morgens (36 Ticks), Tagesstart statt Mitternacht
        
        # Wettersystem
        self.weather_types = {
            "CLEAR": {"temp_mod": 0, "exposure_mod": 1.0},
            "RAIN": {"temp_mod": -5, "exposure_mod": 1.5},
            "STORM": {"temp_mod": -10, "exposure_mod": 2.5},
            "SNOW": {"temp_mod": -15, "exposure_mod": 2.0}
        }
        self.current_weather = "CLEAR"

        # Verletzungs-RNG (SPEC-009): EIGENER Strom, damit die Verletzungswürfe
        # die Ressourcen-RNG-Sequenz (Fund-Items/Erschöpfung) NICHT verschieben.
        # Würde gather() dafür das gemeinsame `random` benutzen, änderten sich
        # für alle bestehenden Mess-Bots (Reachability, Session-Depth, guided)
        # deterministisch die Ausbeuten — der Verletzungs-Wurf gehört nicht auf
        # denselben Kanal. Aus dem aktuellen (deterministisch geseedeten) Zustand
        # kopiert → pro Lauf reproduzierbar, aber unabhängig vom Hauptstrom.
        self.injuries_rng = random.Random()
        self.injuries_rng.setstate(random.getstate())

    @property
    def current_location(self):
        return self.locations[self.current_location_id]

    def _update_weather(self):
        """Bestimmt alle 12 Ticks (2 Stunden) das Wetter neu."""
        if self.tick_counter % 12 == 0:
            self.current_weather = random.choice(list(self.weather_types.keys()))

    def _get_ambient_temp(self) -> float:
        """Berechnet die aktuelle Temperatur basierend auf Ort und Wetter."""
        loc = self.current_location
        weather_mod = self.weather_types[self.current_weather]["temp_mod"]
        # Simuliere Tag/Nacht-Zyklus (Nachts kälter)
        hour = (self.tick_counter % 144) / 6 # 144 Ticks = 24h
        night_mod = -10 if (hour < 6 or hour > 20) else 0
        return loc.base_temp + weather_mod + night_mod

    def _advance_time(self, ticks: int, effort_multiplier: float = 1.0):
        """Simuliert Zeit, Hunger und Thermodynamik."""
        self.tick_counter += ticks
        self._update_weather()

        # 0. Ressourcen-Regeneration (SPEC-004): Vorrat wächst über die
        # verstrichene Spielzeit, nicht über Aktionen. Dadurch regenerieren
        # sich auch andere Orte, während man unterwegs handelt — die Zeit
        # zwischen zwei Besuchen bestimmt den Füllstand.
        for loc in self.locations.values():
            for node in loc.nodes:
                node.stock = min(node.max_stock, node.stock
                                 + node.regen_per_tick * ticks)
                # Ein erschöpfter Node erholt sich erst, wenn genug Zeit
                # vergangen ist, um mindestens eine Ernte-Portion aufzufüllen.
                if node.depleted and node.stock >= node.harvest_cost:
                    node.depleted = False

        logs = []
        
        # 1. Hunger-Simulation
        drain = 5.0 * effort_multiplier * ticks
        self.player.energy = max(0, self.player.energy - drain)
        if self.player.energy <= 0:
            self.player.hp -= 2.0 * ticks
            logs.append("!!! HUNGER-SCHADEN !!!")

        # 2. Thermodynamik (SPEC-007: aktives Location-Feuer hebt die effektive
        # Umgebungstemperatur, verbraucht aber Brennstoff, der über Zeit brennt.
        # Bei Brennstoff 0 erlischt das Feuer mit einer ehrlichen Meldung — nie
        # still. Das macht Kälte abwendbar statt unvermeidbar.)
        ambient_temp = self._get_ambient_temp()
        fire_warmth = 0.0
        loc = self.current_location
        if loc.fire_active and loc.fire_fuel > 0:
            fire_warmth = FIRE_HEAT
            loc.fire_fuel = max(0.0, loc.fire_fuel - ticks)
            if loc.fire_fuel <= 0:
                loc.fire_active = False
                logs.append("!!! FIRE_OUT: " + _feedback_message("FIRE_OUT") + " !!!")
        exposure = loc.exposure * self.weather_types[self.current_weather]["exposure_mod"]
        insulation = self.player.inventory.get_total_insulation()
        effective_ambient = ambient_temp + fire_warmth

        # Delta zwischen Körper und Umwelt, abgemildert durch Isolation und Schutz
        temp_loss = (self.player.body_temp - effective_ambient) * 0.01 * exposure * (1.0 - min(0.9, insulation))
        self.player.body_temp -= (temp_loss * ticks)
        
        # Auswirkungen der Körpertemperatur
        if self.player.body_temp < 35.0:
            self.player.hp -= 1.0 * ticks
            logs.append("!!! UNTERKÜHLUNG !!!")
        elif self.player.body_temp > 40.0:
            self.player.hp -= 1.0 * ticks
            logs.append("!!! HITZSCHLAG !!!")

        # 3. Verletzung & Heilung (SPEC-009): Bluten + Behandlung+Ruhe-Heilung.
        # Eine unbehandelte Schnittwunde zieht über Zeit (HP-Drain), bis sie
        # verbunden wird. Eine behandelte Wunde heilt NUR, solange der Spieler
        # an einem warmen/ruhigen Ort rastet (Feuer oder geschützter Ort).
        cut = self.player.injuries.get("cut")
        if cut:
            cut["ticks"] += ticks
            if not cut["treated"]:
                self.player.hp -= CUT_BLEED_PER_TICK * ticks
                logs.append("!!! " + _feedback_message("BLEEDING") + " !!!")

        healed = []
        for kind in list(self.player.injuries.keys()):
            inj = self.player.injuries[kind]
            inj["ticks"] += ticks
            if inj["treated"] and self._resting_warm():
                inj["severity"] -= INJ_HEAL_RATE * ticks
                if inj["severity"] <= INJ_HEAL_THRESHOLD:
                    del self.player.injuries[kind]
                    healed.append(kind)
        if healed:
            logs.append("!!! " + _feedback_message("HEALED")
                        + f" ({', '.join(map(_injury_label, healed))}) !!!")

        return "\n".join(logs) if logs else None

    def gather(self) -> List[str]:
        logs = []
        # Sammeln ist anstrengend (Effort 2.0), plus Malus durch eine
        # unbehandelte Zerrung (SPEC-009) — sie senkt die Leistungsfähigkeit.
        effort = 2.0 + self._injury_effort_malus()
        time_msg = self._advance_time(1, effort_multiplier=effort)
        if time_msg: logs.append(time_msg)

        for node in self.current_location.nodes:
            if self.player.stats["perception"] < node.req_perception: continue
            
            used_tool = None
            if node.req_tool_tag:
                used_tool = self.player.inventory.find_item_by_tag(node.req_tool_tag)
                if not used_tool:
                    # SPEC-011 (C): die Stillstell-Falle schließen — ohne Werkzeug
                    # schweigte der gather komplett. Node-gebundene ehrliche
                    # Meldung: nur wenn der Node sonst erntbar wäre (perception
                    # ist oben geprüft, Vorrat hier). Nur Logstream, KEIN neuer
                    # Experiment-Reason (EMITTABLE_REASONS unangetastet).
                    if node.stock > 0 and not node.depleted:
                        logs.append(_feedback_message("MISSING_TOOL"))
                    continue

            # Vorratsbasierter Node (SPEC-004): erschöpft → ehrliche Meldung,
            # nie stilles "nichts". Bleibt erschöpft, bis Regeneration ihn
            # über die Zeit wieder auf mindestens eine Ernte-Portion hebt.
            if node.stock <= 0 or node.depleted:
                logs.append(_feedback_message("DEPLETED"))
                continue

            # Erfolgswahrscheinlichkeit skaliert mit dem Vorratsanteil:
            # voller Vorrat = node.chance, geleerter = 0.
            eff_chance = node.chance * (node.stock / node.max_stock)
            # SPEC-011 (A): Attrition wirkt graduell — ein stumpfes Werkzeug
            # erntet schlechter, lange bevor es bricht (cliff → kurve).
            # Gleiche Form wie der Vorratsfaktor (SPEC-004), zweite Achse.
            if used_tool is not None:
                eff_chance *= max(WEAR_MIN_FACTOR, used_tool.condition)
            if random.random() <= eff_chance:
                qty = random.randint(node.min_qty, node.max_qty)
                item = create_item(node.result_template_id, qty)
                if self.player.inventory.add(item):
                    logs.append(f"Gefunden: {qty}x {item.name}")
                    node.stock = max(0.0, node.stock - node.harvest_cost)
                    if node.stock < node.harvest_cost:
                        node.depleted = True
                    # Verletzungsrisiko (SPEC-009) — aus eigenem Handeln, nicht
                    # globalem Timer: scharfe Funde → Schnitt; exponierter Ort →
                    # Zerrung. Frequenz niedrig (abwendbar), nicht vermeidbar.
                    # Eigener RNG-Strom (injuries_rng), damit diese Würfe die
                    # Ressourcen-Sequenz der Mess-Bots nicht verschieben.
                    if "SHARP" in item.tags and self.injuries_rng.random() < INJURE_CUT_CHANCE:
                        if self._inflict("cut"):
                            logs.append("!!! " + _feedback_message("INJURED") + " !!!")
                    if (self.current_location.exposure >= 0.8
                            and self.injuries_rng.random() < INJURE_STRAIN_CHANCE):
                        if self._inflict("strain"):
                            logs.append("!!! " + _feedback_message("INJURED") + " !!!")
                    if used_tool:
                        if "PROJECTILE" in used_tool.tags:
                            # Munitions-Ökonomie: Ein Projektil ist Consumable,
                            # kein dauerhaftes Werkzeug. Pro Ernteerfolg (ein
                            # Wurf) genau eine Einheit weg — NICHT Condition-
                            # Wear auf den gemergten Stack (vorher verschwand
                            # der komplette Munitionsbestand nach ~4 Schüssen
                            # still als „zerbrochen", inkl. Condition-Fragmente
                            # im Inventar). Die Leer-Meldung ist ehrlich und
                            # feuert nur beim letzten Schuss.
                            used_tool.quantity -= 1
                            if used_tool.quantity <= 0:
                                self.player.inventory.items.remove(used_tool)
                                logs.append(f"!!! {used_tool.name} aufgebraucht !!!")
                        else:
                            # SPEC-011 (B): Verschleiß wird lesbar — die Warnung
                            # feuert einmalig an dem gather-Tick, der die Schwelle
                            # unterschreitet (vorher >=, danach <), kein Spam.
                            prev_cond = used_tool.condition
                            wear = 0.05 / used_tool.get_attr("durability", 0.5)
                            used_tool.condition = max(0, used_tool.condition - round(wear, 2))
                            if used_tool.condition <= 0:
                                self.player.inventory.items.remove(used_tool)
                                logs.append(f"!!! {used_tool.name} zerbrochen !!!")
                            elif (prev_cond >= WEAR_WARN_THRESHOLD
                                  and used_tool.condition < WEAR_WARN_THRESHOLD):
                                logs.append(f"!!! {used_tool.name} ist stark abgenutzt !!!")
        return logs

    def eat(self, item_index: int) -> str:
        """Versucht ein Item aus dem Inventar zu essen."""
        items = self.player.inventory.items
        if item_index < 0 or item_index >= len(items):
            return "Ungültiges Item."
        
        item = items[item_index]
        if "EDIBLE" not in item.tags:
            return f"{item.name} ist nicht essbar!"
        
        kcal = item.tags["EDIBLE"]
        self.player.energy = min(self.player.max_energy, self.player.energy + kcal)
        
        # Wenn man isst, regeneriert man etwas HP
        self.player.hp = min(self.player.max_hp, self.player.hp + (kcal / 20))
        
        name = item.name
        if item.quantity > 1: item.quantity -= 1
        else: items.remove(item)
        
        return f"Du isst {name} und regenerierst {kcal} Energie."

    def _result(self, success, message, reason, blueprint_id=None,
                result_template_id=None):
        """Strukturiertes Ergebnis mit Reason-Code (kein Verhaltensunterschied)."""
        return {
            "success": success,
            "message": message,
            "reason": reason,                 # SUCCESS/NO_MATCH/BROKEN_ITEM/MISSING_TAG:<T>/TOO_FEW_ITEMS/UNKNOWN
            "blueprint_id": blueprint_id,
            "result_template_id": result_template_id,
        }

    def _feasible_mapping(self, selected_items, bp):
        """True, wenn sich selected_items wie execute_experiment real auf
        bp.slots zuweisen lassen — Permutation + _slot_satisfied, nur ohne
        Survival-Gate. Filtert Tag-Schatten heraus, bei denen die
        Vereinigungs-Tag-Sicht (_overlap) 'voll' suggeriert, aber niemals eine
        reale Zuordnung existiert (z.B. stick+plant_fiber gegen spear: der
        RIGID-Bedarf beider Slots ist physikalisch nicht deckbar)."""
        if len(selected_items) != len(bp.slots):
            return False
        for p in itertools.permutations(selected_items):
            ok = True
            for i, slot in enumerate(bp.slots.keys()):
                if not _slot_satisfied(p[i].tags, bp.slots[slot]):
                    ok = False
                    break
            if ok:
                return True
        return False

    def _no_match_reason(self, selected_items):
        """Bestimmt den konkretesten Reason für einen Fehlschlag.

        Priorität (SPEC-003 / SPEC-002):
        1. Bekannter Blueprint (SPEC-002): Wer das Ziel bereits entdeckt hat,
           bekommt das fehlende Merkmal genannt — die bestehende Hilfe, die
           Vorwissen belohnt.
        2. Unbekannter Blueprint mit ≥2/3 Treffern (SPEC-003): reines
           Ja/nein-Signal (NEAR_MISS) auf die gehaltene Teilmenge, einmalig pro
           Blueprint, ohne Rezept-/Tag-Leak. Konvergiert naive Spieler, ohne
           ihnen etwas zu schenken.
        3. Generischer Fallback: konkretes Merkmal eines unbekannten Blueprints
           nur, solange noch gar kein Beinahe-Treffer gelaufen ist — danach
           bleibt es still statt jeden Richtungsversuch erneut zu befeuern.
        """
        available = set()
        for it in selected_items:
            available.update(it.tags)

        def _overlap(bp) -> int:
            n = 0
            for slot_value in bp.slots.values():
                required = set(TAG_FAMILIES.get(slot_value, {slot_value}))
                if required & available:
                    n += 1
            return n

        # 1. Bekannte Blueprints → konkretes Merkmal (SPEC-002). Vorrang, weil
        #    entdecktes Wissen beim Wieder-Herstellen mehr wert ist als ein
        #    neuer Entdeckungs-Hinweis auf ein anderes Ziel.
        best_score, best_tag = -1, None
        for bp in self.blueprints.values():
            if bp.id not in self.player.known_blueprints:
                continue
            if len(bp.slots) != len(selected_items):
                continue
            missing = _missing_tags(bp, available)
            if not missing:
                continue
            score = len(bp.slots) - len(missing)
            if score > best_score:
                best_score, best_tag = score, missing[0]
        if best_tag:
            return f"MISSING_TAG:{best_tag}"

        # 2. Unbekannte Blueprints → Beinahe-Treffer (SPEC-003). Einmalig: der
        #    Blueprint wandert in near_misses und feuert nicht erneut.
        near, near_overlap = None, 1  # muss ≥2 sein
        for bp in self.blueprints.values():
            if bp.id in self.player.known_blueprints:
                continue
            if bp.id in self.player.near_misses:
                continue
            # Gate-blockierte Tier-2-Blueprints sprechen ausschließlich über
            # Block 2b (echte Volldeckung). Ohne diese Linie schiebt sich ein
            # reiner Tag-Vereinigungs-Schatten vor (z.B. stick+plant_fiber auf
            # cord_spear: EIN Ast deckt tip+shaft nur virtuell, die Physik
            # kann es nie) und frisst den One-Shot des Hinweises, bevor der
            # echte Volldeckungs-Signal (rope) je drankommt.
            if bp.min_survival_req > self.player.stats["survival"]:
                continue
            o = _overlap(bp)
            if 2 <= o < len(bp.slots) and o > near_overlap:
                near_overlap, near = o, bp
        if near is not None:
            self.player.near_misses.add(near.id)
            return f"NEAR_MISS:{near.id}"

        # 2b. Gate-blockierte Tier-2-Volldeckung (Peter-Hebel, PLAN-Ziel 3):
        #     Die gehaltenen Dinge füllen ALLE Slots wirklich (reale
        #     Permutations-Zuordnung unten, nicht bloß die Tag-Vereinigung aus
        #     _overlap) — der Bau scheitert allein am Survival-Gate
        #     (min_survival_req von rope/cord_spear). Ohne diesen Weg erhalten
        #     Spieler nie eine Richtungssignal auf die zweite Entdeckungs-
        #     schicht: ein voll abgedeckter Blueprint ist heute stumm, weil der
        #     alte Bereich `o < len(slots)` ihn ausschloss. Genau einmal pro
        #     Blueprint wie jeder Near-Miss; der Text bleibt generisch, kein
        #     Gate-/Rezept-/Tag-Leak. Nicht-voll-abgedeckte Kandidaten (z.B.
        #     spear mit einer Sichel an RIGID-Tags) bleiben stumm — der alte
        #     Zustand bleibt in seiner Priorität unangetastet.
        full_bp, full_req = None, -1.0
        for bp in self.blueprints.values():
            if bp.id in self.player.known_blueprints:
                continue
            if bp.id in self.player.near_misses:
                continue
            if self.player.stats["survival"] >= bp.min_survival_req:
                continue                      # Gate offen → Hauptloop hätte gebaut
            if _overlap(bp) != len(bp.slots):
                continue                      # nur echte Volldeckung zählt
            if not self._feasible_mapping(selected_items, bp):
                continue                      # Tag-Schatten ohne reale Zuordnung
            if bp.min_survival_req > full_req:
                full_req, full_bp = bp.min_survival_req, bp
        if full_bp is not None:
            self.player.near_misses.add(full_bp.id)
            return f"NEAR_MISS:{full_bp.id}"

        # 3. Generisch — konkretes Merkmal nur, solange kein Beinahe-Treffer
        #    lief (danach genügt der eine Hinweis; kein Dauer-Leak derselben
        #    Materialrichtung).
        if not self.player.near_misses:
            best_score, best_tag = -1, None
            for bp in self.blueprints.values():
                if bp.id in self.player.known_blueprints:
                    continue
                if len(bp.slots) != len(selected_items):
                    continue
                missing = _missing_tags(bp, available)
                if not missing:
                    continue
                score = len(bp.slots) - len(missing)
                if score > best_score:
                    best_score, best_tag = score, missing[0]
            if best_tag:
                return f"MISSING_TAG:{best_tag}"
        return "NO_MATCH"

    def execute_experiment(self, selected_items: List[Item]) -> Dict[str, Any]:
        # Crafting ist sehr anstrengend (Effort 3.0)
        self._advance_time(2, effort_multiplier=3.0)

        # Zerbrochene Items (condition=0) sind nicht craftbar → verständliches Feedback
        broken = [it.name for it in selected_items if it.condition <= 0]
        if broken:
            return self._result(
                False,
                _feedback_message("BROKEN_ITEM", broken),
                "BROKEN_ITEM")

        # Zu wenige Items für den kleinsten Blueprint → nicht einmal ein Versuch
        slot_counts = [len(bp.slots) for bp in self.blueprints.values()]
        min_count = min(slot_counts) if slot_counts else 0
        if len(selected_items) < min_count:
            return self._result(False, _feedback_message("TOO_FEW_ITEMS"),
                                "TOO_FEW_ITEMS")

        # Menge-Validierung (SPEC-005): Derselbe Stack kann N identische Slots
        # füllen, aber nur solange quantity >= N. Taucht ein Stack-Objekt mehrfach
        # in selected_items auf, ohne dass die Menge das deckt, würde _create_tool
        # sonst ein Item aus dem Nichts erzeugen (Fehlstart). Stattdessen: ehrliches
        # Feedback. Distinkte Stacks (zwei separate Ast-Stacks) bleiben unberührt —
        # die Zählung geht über die Objekt-Identität, nicht den Namen.
        seen = {}
        for it in selected_items:
            n = seen.get(id(it), 0) + 1
            seen[id(it)] = n
            if n > it.quantity:
                return self._result(False,
                                    _feedback_message("NOT_ENOUGH_QUANTITY"),
                                    "NOT_ENOUGH_QUANTITY")

        for bp_id, bp in self.blueprints.items():
            if len(selected_items) != len(bp.slots): continue
            if self.player.stats["survival"] < bp.min_survival_req: continue

            for p in itertools.permutations(selected_items):
                mapping = {}
                match = True
                for i, slot in enumerate(bp.slots.keys()):
                    if not _slot_satisfied(p[i].tags, bp.slots[slot]):
                        match = False; break
                    mapping[slot] = p[i]
                
                if match:
                    if bp_id not in self.player.known_blueprints:
                        self.player.known_blueprints.add(bp_id)
                        self.player.stats["survival"] += 0.2
                    return self._create_tool(bp, mapping)
        reason = self._no_match_reason(selected_items)
        return self._result(False, _feedback_message(reason), reason)

    def _create_tool(self, bp: ToolBlueprint, comp: Dict[str, Item]) -> Dict[str, Any]:
        dur_attr = min(c.get_attr("durability", 0.5) for c in comp.values())
        # TASK-R02: Dynamische Slot-Erkennung statt hartkodierter "head"/"blade"-
        # Fallbacks. Der Träger der Werkzeug-Effizienz ist der erste Bauteil mit
        # Schärfe (sharpness > 0), unabhängig davon, wie der Slot heißt ("tip",
        # "blade", "head", …). Konsistent mit crafting.py::create_dynamic_item.
        # Fällt kein Bauteil mit Schärfe aus, zählt der erste als Hauptteil mit
        # dem sharpness-Fallback 0.1 (Verhalten unverändert für alle aktuellen
        # Blueprints). Dadurch bricht kein Blueprint: Der Speer (Slots "tip"/"shaft"),
        # der zuvor über die generische Value-Fallback-Liste den spitzen Stein als
        # Hauptteil nahm, wird jetzt über die Schärfe-Scan: identisch ermittelt.
        comp_list = list(comp.values())
        main = comp_list[0] if comp_list else Item("Empty", 0)
        for c in comp_list:
            if c.get_attr("sharpness", 0.0) > 0:
                main = c
                break
        power = main.get_attr("sharpness", 0.1) * bp.base_efficiency
        if len(comp_list) >= 2:
            name = f"{main.name}-{bp.result_name} ({comp_list[1].name})"
        else:
            name = f"{main.name}-{bp.result_name}"
        new_tool = Item(name=name, base_weight=sum(c.base_weight for c in comp.values()),
                        tags={"DURABILITY": dur_attr}, attributes={"durability": dur_attr, "power": power},
                        template_id=bp.id)
        for t in bp.tool_tags:
            new_tool.tags[t] = power
        for c in comp.values():
            # Robust: verbrauche nur Stacks, die wirklich im Inventar liegen. Ein
            # Item-Objekt kann mehrfach selektiert (derselbe Stack) oder in einem
            # anderen Stack zusammengeführt worden sein — kein blindes remove(),
            # sonst ValueError. (Fix: 3-Sticks-Speer, Doppel-Selektion.)
            if c not in self.player.inventory.items:
                continue
            if c.quantity > 1:
                c.quantity -= 1
            else:
                self.player.inventory.items.remove(c)
        self.player.inventory.add(new_tool)
        # SPEC-006: Wird ein Werkzeug-Tag ERSTMALS gebaut, registriert das
        # Experimentiergedächtnis ihn als bekannte Komponente und setzt den
        # Einmal-Reveal (Don't-Starve-Prototyper): "Besitz gibt Richtung". Der
        # Hinweis ist bewusst generisch — nennt weder Item noch Ziel-Blueprint
        # noch fehlenden Tag (kein Rezept-Leak). Die `reason` bleibt SUCCESS: das
        # Werkzeug IST erfolgreich gebaut; der Reveal ist eine Zusatz-Meldung,
        # kein separater Fehlschlag-Reason (kein Eingriff in feedback_quality /
        # die Reason-Vollständigkeit). Pro Tag genau einmal, dann still.
        reveal = []
        for t in bp.tool_tags:
            if t not in self.player.known_components:
                self.player.known_components.add(t)
                reveal.append(t)
        msg = f"Hergestellt: {name}"
        if reveal:
            msg += " Das könnte sich noch mit etwas anderem verbinden lassen."
        return {"success": True, "message": msg,
                "reason": "SUCCESS", "blueprint_id": bp.id,
                "result_template_id": bp.id}

    # ------------------------------------------------------------------
    # Prozess-System — Transformationen mit Umgebungs-/Werkzeug-Kontext
    # ------------------------------------------------------------------

    def _count_template(self, template_id: str) -> int:
        """Gesamtmenge eines Items über alle Stacks (nach template_id)."""
        return sum(it.quantity for it in self.player.inventory.items
                   if it.template_id == template_id)

    def _consume_template(self, template_id: str, qty: int):
        """Entfernt qty eines Items (über mehrere Stacks, falls nötig)."""
        remaining = qty
        for it in list(self.player.inventory.items):
            if it.template_id != template_id or remaining <= 0:
                continue
            take = min(it.quantity, remaining)
            it.quantity -= take
            remaining -= take
            if it.quantity <= 0:
                self.player.inventory.items.remove(it)
        return remaining == 0

    def _item_name(self, template_id: str) -> str:
        t = TEMPLATE_DB.get(template_id)
        return t.name if t else template_id

    # ------------------------------------------------------------------
    # Wärmemanagement (SPEC-007) — Feuer entzünden, hüten, nachlegen
    # ------------------------------------------------------------------

    def _light_fire(self):
        """Setzt den Location-Feuerzustand (aktives Feuer + Brennstoff).

        Wird von execute_process("start_fire") gerufen, sobald das Feuer
        entzündet ist. Das Feuer existiert dann an der Location, nicht nur
        als Inventar-Gegenstand.
        """
        loc = self.current_location
        loc.fire_active = True
        loc.fire_fuel = START_FIRE_FUEL

    def _fire_lit(self) -> bool:
        """Ein aktives Feuer mit Brennstoff brennt an der aktuellen Location."""
        loc = self.current_location
        return bool(loc.fire_active and loc.fire_fuel > 0)

    def _env_satisfied(self, tag: str) -> bool:
        """Ob die Location ein Umgebungs-Tag erfüllt (z.B. HEAT_SOURCE)."""
        if tag == "HEAT_SOURCE":
            return self._fire_lit()
        return False

    # ------------------------------------------------------------------
    # Verletzung & Heilung (SPEC-009) — Zustand, Ruhe-Bedingung, Effort
    # ------------------------------------------------------------------

    def _resting_warm(self) -> bool:
        """Ob der Spieler an einem warmen/ruhigen Ort rastet (Heil-Bedingung).

        Rast = aktives Feuer an der Location ODER windgeschützter Ort mit
        geringer Exposition (z.B. die Höhle). Nur HIER heilt eine behandelte
        Wunde über Zeit — behandelt aber unterwegs heilt nicht (SPEC-009).
        """
        return self._fire_lit() or self.current_location.exposure <= REST_EXPOSURE

    def _inflict(self, kind: str) -> bool:
        """Setzt eine Verletzung, falls nicht schon aktiv. True, wenn neu.

        `cut` verursacht Bluten; `strain` ist ein Effort-Malus. Wiederverletzen
        einer aktiven Wunde stapelt nicht (Severity bleibt 1.0).
        """
        if kind in self.player.injuries:
            return False
        self.player.injuries[kind] = {"severity": 1.0, "ticks": 0, "treated": False}
        return True

    def _injury_effort_malus(self) -> float:
        """Extra-Effort durch eine unbehandelte Zerrung beim Sammeln."""
        inj = self.player.injuries.get("strain")
        if inj and not inj["treated"]:
            return STRAIN_EFFORT_MALUS
        return 0.0

    def _find_fuel_item(self):
        """Brennstoff-Item fürs Nachlegen: Holz (WOOD) bevorzugt, sonst Zunder/
        Reisig (KINDLING) — aber nie die Feuergrube selbst."""
        for it in self.player.inventory.items:
            if "WOOD" in it.tags and it.condition > 0:
                return it
        for it in self.player.inventory.items:
            if ("KINDLING" in it.tags and it.template_id != "fire_pit"
                    and it.condition > 0):
                return it
        return None

    def stoke_fire(self) -> Dict[str, Any]:
        """Legt Brennstoff nach: erhöht fire_fuel, kostet Zeit (Long-Dark-Zyklus).

        Nur bei aktivem Feuer möglich — ohne Feuer keine Wärme, man muss Holz
        sammeln und es nachlegen, um warm zu bleiben.
        """
        loc = self.current_location
        if not loc.fire_active:
            return {"success": False, "message": _feedback_message("NO_FIRE"),
                    "reason": "NO_FIRE"}
        fuel = self._find_fuel_item()
        if fuel is None:
            return {"success": False, "message": _feedback_message("MISSING_FUEL"),
                    "reason": "MISSING_FUEL"}
        name = fuel.name
        if fuel.quantity > 1:
            fuel.quantity -= 1
        else:
            self.player.inventory.items.remove(fuel)
        loc.fire_fuel += STOKE_FUEL
        # Nachlegen ist Arbeit und vergeht Zeit — Brennstoff brennt weiter.
        time_msg = self._advance_time(1, effort_multiplier=1.0)
        msg = f"Du legst {name} nach. "
        msg += (time_msg if time_msg else "")
        return {"success": True, "message": msg.strip(), "reason": "SUCCESS"}

    def _process_requirements_met(self, proc) -> bool:
        """Alle Input-/Werkzeug-/Umgebungs-Anforderungen eines Prozesses erfüllt?"""
        if any(self._count_template(i) < q for i, q in proc.inputs.items()):
            return False
        if any(not self.player.inventory.find_item_by_tag(t) for t in proc.tools):
            return False
        if proc.required_tag_in_env and not self._env_satisfied(proc.required_tag_in_env):
            return False
        return True

    def available_processes(self) -> List[str]:
        """Prozesse, deren Inputs, Werkzeug- und Umgebungs-Anforderungen erfüllt sind."""
        return [pid for pid, proc in self.processes.items()
                if self._process_requirements_met(proc)]

    def take_process_hints(self) -> List[tuple]:
        """Einmalige, generische Potenzial-Hinweise pro Prozess-Klasse (Ziel-2-Hebel).

        Feuert für Prozesse, deren Besitz- und Umgebungs-Anforderungen JETZT
        vollständig erfüllt sind und deren Kategorie noch nie gemeldet wurde —
        derselbe Trigger-Moment, in dem `available_processes` sie listen würde,
        aber als aktives Richtungssignal statt passiver Liste. Liefert
        (process_id, text)-Paare und markiert die Kategorie als gesehen.
        Konsumiert nichts, kostet keine Zeit, würfelt nicht.
        """
        hints = []
        for pid, proc in self.processes.items():
            cat = PROCESS_HINT_CATEGORY.get(pid)
            if cat is None or cat in self.player.process_hints_seen:
                continue
            if self._process_requirements_met(proc):
                self.player.process_hints_seen.add(cat)
                hints.append((pid, PROCESS_HINT_TEXT[cat]))
        return hints

    def execute_process(self, process_id: str) -> Dict[str, Any]:
        """Führt einen Prozess aus: konsumiert Inputs, nutzt Werkzeuge, erzeugt Outputs.

        Seit SPEC-007 ist `required_tag_in_env` HART: Ein Prozess, der eine
        Umgebungs-Anforderung deklariert (z.B. `cook_meat` → `HEAT_SOURCE`),
        läuft nur, wenn die aktuelle Location sie erfüllt (aktives Feuer).
        Das aktiviert das zuvor tote Feld und macht das Feuer real nötig.
        """
        proc = self.processes.get(process_id)
        if not proc:
            return {"success": False, "message": "Unbekannter Prozess.",
                    "reason": "UNKNOWN_PROCESS"}

        for item_id, qty in proc.inputs.items():
            if self._count_template(item_id) < qty:
                return {"success": False,
                        "message": f"Es fehlt dir {self._item_name(item_id)}.",
                        "reason": f"MISSING_INPUT:{item_id}"}

        for tag in proc.tools:
            if not self.player.inventory.find_item_by_tag(tag):
                return {"success": False,
                        "message": f"Es fehlt dir {_label_for(tag)} als Werkzeug.",
                        "reason": f"MISSING_TOOL:{tag}"}

        if proc.required_tag_in_env and not self._env_satisfied(proc.required_tag_in_env):
            return {"success": False,
                    "message": _feedback_message(f"MISSING_ENV:{proc.required_tag_in_env}"),
                    "reason": f"MISSING_ENV:{proc.required_tag_in_env}"}

        # SPEC-007: start_fire entzündet das Location-Feuer, BEVOR die
        # Entzündungsdauer vergeht — ein frisch gebautes Feuer wärmt schon
        # während seines Aufbaus, statt den Spieler in der Kälte warten zu lassen.
        if process_id == "start_fire":
            self._light_fire()

        # SPEC-009: Behandlung anlegen (Verband stoppt das Bluten, Umschlag
        # lindert die Zerrung). Ohne aktive Wunde wird das Verbandsmaterial
        # NICHT verbraucht — ehrliches Feedback statt verschwendetem Item.
        # Die eigentliche Heilung braucht danach zusätzlich Ruhe am warmen Ort.
        if process_id == "treat_cut":
            if "cut" not in self.player.injuries:
                return {"success": False, "message": _feedback_message("NO_INJURY"),
                        "reason": "NO_INJURY"}
            self.player.injuries["cut"]["treated"] = True
        if process_id == "treat_strain":
            if "strain" not in self.player.injuries:
                return {"success": False, "message": _feedback_message("NO_INJURY"),
                        "reason": "NO_INJURY"}
            self.player.injuries["strain"]["treated"] = True

        # SPEC-011: Schärfen als Instandhaltungshebel (apply-only, Behandlungs-
        # Muster). Das am meisten abgenutzte getragene Schneid-/Stemm-/Stich-
        # werkzeug unter Volllast wird geschärft. Scheitert es (kein
        # verschlissenes Werkzeug da), wird der Flint-Splitter NICHT verbraucht
        # — ehrliches Feedback statt verschwendetem Material.
        sharpened_name = None
        if process_id == "sharpen_tool":
            worn = None
            for it in self.player.inventory.items:
                if not (set(SHARPEN_TOOL_TAGS) & set(it.tags)):
                    continue
                if it.condition >= 1.0:
                    continue
                if worn is None or it.condition < worn.condition:
                    worn = it
            if worn is None:
                return {"success": False,
                        "message": "Nichts hier, das zu schärfen wäre.",
                        "reason": "NO_WORN_TOOL"}
            worn.condition = min(1.0, worn.condition + SHARPEN_RESTORE)
            sharpened_name = worn.name

        # Inputs verbrauchen, dann Zeit/Energie kosten (wie Crafting anstrengend)
        for item_id, qty in proc.inputs.items():
            self._consume_template(item_id, qty)
        self._advance_time(proc.duration_ticks, effort_multiplier=2.0)

        for item_id, qty in proc.outputs.items():
            self.player.inventory.add(create_item(item_id, qty))

        if process_id not in self.player.known_processes:
            self.player.known_processes.add(process_id)
            self.player.stats["survival"] += 0.1

        msg = f"Prozess ausgeführt: {proc.name}"
        if sharpened_name:
            msg = f"{sharpened_name} geschärft."
        return {"success": True, "message": msg,
                "reason": "SUCCESS", "process_id": process_id}

    def travel(self, tid: str):
        if tid not in self.locations: return "Unbekannt."
        self.current_location_id = tid
        msg = self._advance_time(3, effort_multiplier=1.5)
        return f"Gereist nach {self.locations[tid].name}. " + (msg if msg else "")