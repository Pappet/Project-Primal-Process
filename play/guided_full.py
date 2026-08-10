"""Exhaustiver Guided-Player: survival-sicher, voller Tech-Tree.
Misst: Aktion, bei der die LETZTE Neuheit auftritt (Erschöpfung der Entdeckung).
"""
import random, sys; sys.path.insert(0, ".")
from engine.core import GameEngine, TAG_FAMILIES
from data.items import TEMPLATE_DB
from data.blueprints import get_all_blueprints
_T = TEMPLATE_DB

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
    if game.player.energy < 250:
        best = None
        for i, it in enumerate(game.player.inventory.items):
            if "EDIBLE" in it.tags and (best is None or it.tags["EDIBLE"] > best[1]):
                best = (i, it.tags["EDIBLE"])
        # don't eat the only raw_meat we need for cooking unless desperate
        if best:
            eat_idx = best[0]
            it = game.player.inventory.items[eat_idx]
            if it.template_id == "raw_meat" and have_qty(game, "raw_meat", 2) is False and game.player.energy > 100:
                pass
            else:
                game.eat(eat_idx)

def gather_tag(game, tags, n=25, min_mode=True):
    """Sammelt an allen Orten, bis ein Item mit einem der tags im Inventar (min_mode)
    oder n Versuche gemacht (nicht-min)."""
    for loc in game.locations.values():
        for node in loc.nodes:
            t = _T.get(node.result_template_id)
            if not t: continue
            if not (tags & set(getattr(t,"tags",{}))): continue
            if node.req_tool_tag and not item_with(game, {node.req_tool_tag}): continue
            game.travel(loc.id)
            for _ in range(n):
                game.gather()
                got = item_with(game, tags)
                if got and got not in game.player.inventory.items:  # fresh
                    return got
                got = item_with(game, tags)
                if got and have_qty(game, got.template_id, 2):
                    return got
    return item_with(game, tags)

def gather_at(game, loc, n):
    if game.current_location_id != loc: game.travel(loc)
    for _ in range(n): game.gather()

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
    for _ in range(max_actions):
        if game.player.hp <= 0: break
        # --- 1. try undiscovered blueprints ---
        acted = False
        for bp in get_all_blueprints():
            if bp.id in game.player.known_blueprints: continue
            sel = []
            for slot_name, v in bp.slots.items():
                fam = FAM(v)
                # choose distinct stacks
                it = next((x for x in game.player.inventory.items
                           if fam & set(x.tags) and x.condition>0 and x not in sel), None)
                if it is None:
                    got = gather_tag(game, fam)
                    if got is None or got in sel:
                        # force distinct: gather more
                        got = None
                    if got is None: break
                    sel.append(got)
                else:
                    sel.append(it)
            if len(sel) == len(bp.slots):
                g.shot(lambda: game.execute_experiment(sel))
                acted = True; break
        if acted: continue
        # --- 2. processes in order ---
        prop = ["make_sharp_stone","create_tinder","start_fire","cook_meat"]
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
