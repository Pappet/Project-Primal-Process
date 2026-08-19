"""Exhaustiver Guided-Player: survival-sicher, voller Tech-Tree.
Misst: Aktion, bei der die LETZTE Neuheit auftritt (Erschöpfung der Entdeckung).

Seit SPEC-007 (Feuer/Wärme) überlebt ein naives Gather-Screening die Kälte nicht
mehr. Deshalb sichert dieser Runner ZUERST die Wärme-Infrastruktur am warmen
Waldrand (base_temp 15, exposure 0.5): Knochen-Messer → Zunder → Feuer. Dann
holt er kurz einen Kiesel am Gipfel (PROJECTILE), jagt rohes Fleisch und näht
den Fell-Umhang (Isolation 0.6). Danach läuft die Discovery-Suche mit aktivem
Basisfeuer + Umhang, und kalte Gather-Ausflüge kehren zum Aufwärmen an den Wald-
rand zurück. So misst `last_new` die echte Discovery-Decke statt eines Erfrier-Tods.
"""
import random, sys; sys.path.insert(0, ".")
from engine.core import GameEngine, TAG_FAMILIES
from data.items import TEMPLATE_DB
from data.blueprints import get_all_blueprints
_T = TEMPLATE_DB

WARM = "forest_edge"       # base_temp 15 — warmster erreichbarer Ort; Höhle ist kälter
def FAM(slot):
    f = TAG_FAMILIES.get(slot); return set(f) if f else {slot}

def item_with(game, tags):
    for it in game.player.inventory.items:
        if tags & set(it.tags) and it.condition > 0:
            return it
    return None

def have_qty(game, tid, q):
    return sum(it.quantity for it in game.player.inventory.items if it.template_id==tid) >= q

def eat(game):
    # Gegen Kälte-Energieverlust und HP-Blut: essen, wenn Energie ODER HP sinken.
    # Rohes Fleisch ist Zutat (cook_meat 1×, make_fur_cloak 1×) — nicht anrühren,
    # solange gekochtes Fleisch / Beeren / Pilze verfügbar sind. Nur als letzte
    # Notration essen (sonst frisst sich der Bot seinen eigenen Fortschritt weg).
    if game.player.energy < 260 or game.player.hp < 40:
        best = None
        for i, it in enumerate(game.player.inventory.items):
            if "EDIBLE" not in it.tags or it.template_id == "raw_meat":
                continue
            if best is None or it.tags["EDIBLE"] > best[1]:
                best = (i, it.tags["EDIBLE"])
        if best:
            game.eat(best[0]); return
        # Notration: nur noch rohes Fleisch übrig
        for i, it in enumerate(game.player.inventory.items):
            if it.template_id == "raw_meat" and "EDIBLE" in it.tags:
                game.eat(i); return

def _go(game, loc):
    if game.current_location_id != loc:
        game.travel(loc)

def _fire_at(game):
    """Sichert am aktuellen Ort ein aktives Feuer (nachlegen/entzünden)."""
    loc = game.current_location
    if loc.fire_active:
        if loc.fire_fuel < 15:
            return game.stoke_fire().get("success", False)
        return True
    if "start_fire" in game.available_processes():
        return bool(game.execute_process("start_fire").get("success"))
    return False

def _warm_here(game):
    """Feuer am aktuellen Arbeits-Ort unterhalten (SPEC-007: erst bei 0 erlischt es;
    SOLANGE es brennt, hebt es die eff. Temperatur um FIRE_HEAT). Ohne Feuer frisst
    die Kälte (exposure 1.0 am Gipfel) die body_temp — die Wärme-Haltung ist also
    hier der entscheidende Hebel, nicht der Rückzug."""
    _fire_at(game)
    # Kein Feuer möglich → kurzer Rückzug an den warmen Waldrand (base 15)
    loc = game.current_location
    if not (loc.fire_active and loc.fire_fuel > 0) and game.player.body_temp < 35.0:
        _go(game, WARM)
        _fire_at(game)
        for _ in range(6):
            if game.player.body_temp >= 35.5: break
            game._advance_time(1, effort_multiplier=1.0)

def gather_tag(game, tags, n=25, min_mode=True):
    """Sammelt kältesicher: Kurz-Burst, bei Kälte kurzer Rückzug an den Waldrand."""
    for loc in game.locations.values():
        for node in loc.nodes:
            t = _T.get(node.result_template_id)
            if not t: continue
            if not (tags & set(getattr(t,"tags",{}))): continue
            if node.req_tool_tag and not item_with(game, {node.req_tool_tag}): continue
            _go(game, loc.id)
            for _ in range(n):
                _warm_here(game)
                game.gather()
                got = item_with(game, tags)
                if got and got not in game.player.inventory.items:
                    return got
                got = item_with(game, tags)
                if got and have_qty(game, got.template_id, 2):
                    return got
    return item_with(game, tags)

def gather_at(game, loc, n):
    _go(game, loc)
    for _ in range(n):
        _warm_here(game)
        game.gather()

def _warmup(game):
    """Wärme-Infrastruktur sicherstellen: Messer → Zunder → Feuer → Fell-Umhang."""
    gather_at(game, "forest_edge", 8)     # stick, fiber, berries
    gather_at(game, "hidden_cave", 6)     # bone, reeds, mushroom
    # Knochen-Messer (CUTTING)
    if not game.player.inventory.find_item_by_tag("CUTTING"):
        for bp in get_all_blueprints():
            if not (bp.tool_tags and "CUTTING" in bp.tool_tags): continue
            if "BONE" not in bp.slots.values(): continue
            sel = []
            for slot_name, v in bp.slots.items():
                fam = FAM(v)
                it = item_with(game, fam)
                if it is None:
                    it = gather_tag(game, fam, 6)
                if it is None: break
                sel.append(it)
            if len(sel) == len(bp.slots):
                game.execute_experiment(sel)
            break
    # Zunder + Feuer am Waldrand
    game.execute_process("create_tinder")
    _go(game, WARM)
    _fire_at(game)
    # Fell-Umhang: kurzer Gipfel-Ausflug nur für einen Kiesel (PROJECTILE)
    if not game.player.inventory.get_total_insulation():
        pb = item_with(game, {"PROJECTILE"})
        if pb is None:
            _go(game, "mountain_peak")
            for _ in range(6):
                game.gather()
                pb = item_with(game, {"PROJECTILE"})
                if pb: break
            _go(game, WARM)
        if pb is not None:
            # rohes Fleisch jagen (PROJECTILE am Waldrand)
            _go(game, WARM)
            for _ in range(8):
                game.gather()
                if have_qty(game, "raw_meat", 1): break
            # Fell-Umhang zuerst (braucht 1 rohes Fleisch)
            game.execute_process("make_fur_cloak")
    # Kochen: 1. rohes Fleisch frisst das Fell-Rezept. Jage ein zweites und
    # brate es, solange Feuer + Energie noch frisch sind (BL 17.08: sonst isst
    # der Bot sein Fleisch oder stirbt, bevor cook_meat je Inputs hat).
    if "cook_meat" not in game.player.known_processes:
        _go(game, WARM)
        _fire_at(game)
        for _ in range(8):
            game.gather()
            if have_qty(game, "raw_meat", 1):
                game.execute_process("cook_meat")
                break
        _go(game, WARM)

class G:
    def __init__(s, seed):
        random.seed(seed); s.rng = random.Random(seed)
        s.game = GameEngine(); s.game._rng = s.rng
        s.known = set(); s.timeline = []; s.actions = 0; s.last_new = 0
    def nov(s):
        g = s.game
        tpl = {it.template_id or it.name for it in g.player.inventory.items}
        return tpl | set(g.player.known_blueprints) | set(g.player.known_processes)
    def shot(s, fn):
        s.actions += 1
        before = s.nov()
        eat(s.game)
        fn()
        after = s.nov()
        if after != before:
            s.last_new = s.actions
            s.timeline.append((s.actions, sorted(after-before)))

def guided_full(seed, max_actions=400):
    g = G(seed); game = g.game
    _warmup(game)
    _fire_at(game)
    for _ in range(max_actions):
        if game.player.hp <= 0: break
        _warm_here(game)
        # --- 1. try undiscovered blueprints ---
        acted = False
        for bp in get_all_blueprints():
            if bp.id in game.player.known_blueprints: continue
            sel = []
            for slot_name, v in bp.slots.items():
                fam = FAM(v)
                it = next((x for x in game.player.inventory.items
                           if fam & set(x.tags) and x.condition>0 and x not in sel), None)
                if it is None:
                    got = gather_tag(game, fam)
                    if got is None or got in sel:
                        got = None
                    if got is None: break
                    sel.append(got)
                else:
                    sel.append(it)
            if len(sel) == len(bp.slots):
                g.shot(lambda: game.execute_experiment(sel))
                acted = True; break
        if acted: continue
        # --- 1b. Kochen vorbereiten: rohes Fleisch jagen + Feuer halten ---
        # cook_meat braucht 1 raw_meat + aktives Feuer am Ort. Nach dem Fell-Umhang
        # (Warmup) ist das rohe Fleisch verbraucht; sonst jagt der Bot nie gezielt
        # ein zweites und kocht nie (BL 17.08). Also: Feuer am Waldrand, dort jagen.
        if "cook_meat" not in game.player.known_processes and not have_qty(game, "raw_meat", 1):
            _go(game, WARM)
            _fire_at(game)
            hunted = False
            for _ in range(8):
                _warm_here(game)
                game.gather()
                if have_qty(game, "raw_meat", 1):
                    hunted = True; break
            if hunted:
                g.shot(lambda: game.execute_process("cook_meat"))
                acted = True; continue
            else:
                acted = True; continue  # Jagd-Fehlschlag zählt als Aktion, kein Spin
        if acted: continue
        # --- 2. processes in order ---
        prop = ["make_sharp_stone","create_tinder","start_fire","cook_meat","make_fur_cloak"]
        acted=False
        for pid in prop:
            if pid in game.available_processes():
                g.shot(lambda: game.execute_process(pid)); acted=True; break
        if acted: continue
        # --- 3. gather supplies / edibles / hunt ---
        g.shot(lambda: gather_at(game, list(game.locations.keys())[g.rng.randrange(len(game.locations))], 3))
    return g

if __name__ == "__main__":
    for s in [20260803, 20260810, 20260815]:
        g = guided_full(s)
        print(f"\nseed {s}: Aktionen={g.actions}, LETZTE Neuheit @{g.last_new} (Grind danach={g.actions-g.last_new})")
        print("   bps:", sorted(g.game.player.known_blueprints))
        print("   procs:", sorted(g.game.player.known_processes))
        print("   timeline letzte 5:", g.timeline[-5:])