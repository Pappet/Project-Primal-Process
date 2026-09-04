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

def _treat_if_injured(game):
    """SPEC-009: Verletzungen behandeln, damit der Mess-Bot nicht verblutet (sonst
    rot der Bot, wie nach SPEC-007, und untertreibt die Discovery-Decke). cut →
    Verband (plant_fiber×2) weben + anlegen; strain → Umschlag (mushroom+clay_lump).
    Verband/Paste ggf. erst besorgen; strain ist nur Effort-Malus (nicht tödlich),
    also best-effort, wenn der Ton (SHOVEL) fehlt.

    Re-Entrancy-Guard (Nachcommit 04.09.): gather_tag→_warm_here ruft diesen
    Helper erneut, solange 'cut' unbehandelt bleibt → unendlicher Zyklus
    (RecursionError, Seed 20260810). Guard nach dem bewährten
    _fire_supply_pending-Muster: der innerste Aufruf kehrt sofort heim, der
    äussere vollendet Behandlung + Nachkauf seriell."""
    if getattr(game, "_treat_pending", False):
        return
    game._treat_pending = True
    try:
        inj = game.player.injuries
        if not inj:
            return
        if "cut" in inj and not inj["cut"]["treated"]:
            if not have_qty(game, "plant_fiber", 2):
                gather_tag(game, {"FIBER"}, 8)
            if "make_bandage" in game.available_processes():
                game.execute_process("make_bandage")
            if "treat_cut" in game.available_processes():
                game.execute_process("treat_cut")
        if "strain" in inj and not inj["strain"]["treated"]:
            if not have_qty(game, "mushroom", 1):
                gather_tag(game, {"EDIBLE"}, 6)
            if "make_poultice" in game.available_processes():
                game.execute_process("make_poultice")
                # Ton ggf. nicht erreichbar → strain bleibt (nur Malus, kein Tod)
                if "treat_strain" in game.available_processes():
                    game.execute_process("treat_strain")
    finally:
        game._treat_pending = False

def _go(game, loc):
    if game.current_location_id != loc:
        game.travel(loc)

# Brennstoff-Ökonomie (PLAN-Task „Feuer-Ökonomie statt Rückzug-Trigger", 31.08.):
# Die Baseline-Tode (28.08.-Befund) sind die Versorgungsspirale am Waldrand —
# Feuer brennt während des Gipfel-Trips ab, tinder/reeds leer → start_fire
# unmöglich → bt-Kollaps. Gegenmittel: Reserven im Inventar, nachgeschoben VOR
# Reisen und vor jedem Zündversuch am warmen Ort. Am kalten Ort wird nie
# gesammelt (kein Pendel — Lektion aus den vier gescheiterten Trigger-Varianten).
FUEL_MIN_TINDER = 2
FUEL_MIN_STICKS = 2

def _ensure_fire_supply(game):
    """Feuer-Reserven im Inventar auffüllen (sticks, tinder-Kette aus reeds).

    Template-exakte Sammel-Schleifen statt gather_tag: gather_tag akzeptiert
    JEDES Inventar-Item der Tag-Familie (z. B. reeds für {"RIGID"}) und würde
    dann ohne Nachkauf zurückkehren — die Reserve bliebe leer. Best-effort:
    erschöpfte Nodes liefern nichts, der Zündversuch bleibt ehrlich (False),
    es gibt keinen Endlos-Loop."""
    if not have_qty(game, "stick", FUEL_MIN_STICKS):
        _go(game, WARM)
        for _ in range(4):
            game.gather()
            if have_qty(game, "stick", FUEL_MIN_STICKS):
                break
    if not have_qty(game, "tinder", FUEL_MIN_TINDER) and not have_qty(game, "reeds", 2):
        _go(game, "hidden_cave")                    # reeds gibt es nur in der Höhle
        for _ in range(6):
            game.gather()
            if have_qty(game, "reeds", 2):
                break
    if (not have_qty(game, "tinder", FUEL_MIN_TINDER)
            and "create_tinder" in game.available_processes()):
        game.execute_process("create_tinder")

def _fire_at(game):
    """Sichert am aktuellen Ort ein aktives Feuer (nachlegen/entzünden).
    Zündet nur aus dem Inventar — keine Sammel-Trips mehr von hier: die
    Versorgung gehört ins warme Fenster (_warm_here, siehe dort)."""
    loc = game.current_location
    if loc.fire_active:
        if loc.fire_fuel < 15:
            return game.stoke_fire().get("success", False)
        return True
    if "start_fire" in game.available_processes():
        return bool(game.execute_process("start_fire").get("success"))
    return False

def _needs_fire_supply(game):
    return (not have_qty(game, "stick", FUEL_MIN_STICKS)
            or not have_qty(game, "tinder", FUEL_MIN_TINDER))

def _worn_tool(game):
    """Das am stärksten abgenutzte getragene Schneid-/Stemm-/Stichwerkzeug —
    dieselbe Auswahl wie engine.core.execute_process('sharpen_tool')."""
    from engine.core import SHARPEN_TOOL_TAGS
    worn = None
    for it in game.player.inventory.items:
        if not (set(SHARPEN_TOOL_TAGS) & set(it.tags)): continue
        if it.condition >= 1.0: continue
        if worn is None or it.condition < worn.condition:
            worn = it
    return worn

def _sharpen_if_worthwhile(game):
    """SPEC-011-Gegenmechanik im Mess-Bot (BL 02.09): nur schärfen, wenn ein
    Werkzeug tatsächlich unter Volllast ist. available_processes() listet
    sharpen_tool schon mit flint_shard (Inputs-Check sieht keine Condition) —
    ein blinder prop-Eintrag würde NO_WORN_TOOL spinnen. Liefert True bei
    Erfolg (execute_process konsumiert den Flint nur dann)."""
    if _worn_tool(game) is None: return False
    r = game.execute_process("sharpen_tool")
    return bool(r.get("success"))

def _warm_here(game):
    """Feuer am aktuellen Arbeits-Ort unterhalten (SPEC-007: erst bei 0 erlischt es;
    SOLANGE es brennt, hebt es die eff. Temperatur um FIRE_HEAT). Ohne Feuer frisst
    die Kälte (exposure 1.0 am Gipfel) die body_temp — die Wärme-Haltung ist also
    hier der entscheidende Hebel, nicht der Rückzug."""
    _treat_if_injured(game)
    fire_ok = _fire_at(game)
    # Brennstoff-Ökonomie — warmes Fenster: Reserven pflegen, SOLANGE das eigene
    # Feuer brennt und genug fuel für die Versorgungs-Trips übrig bleibt. Nie am
    # kalten Feuer reparieren: der erste Ansatz (Versorgung, sobald Feuer aus)
    # erzeugte kalte Versorgungs-Trips (15+ ungeschützte Ticks) und war im
    # 20-Sweep strikt schlechter als die Baseline. Guard gegen Re-Entrancy.
    if (fire_ok and game.current_location_id == WARM
            and game.current_location.fire_fuel > 10
            and _needs_fire_supply(game)
            and not getattr(game, "_fire_supply_pending", False)):
        game._fire_supply_pending = True
        try:
            _ensure_fire_supply(game)
        finally:
            game._fire_supply_pending = False
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
    # Fell-Umhang: kurzer Gipfel-Ausflug nur für einen Kiesel (PROJECTILE).
    # Brennstoff-Ökonomie: Versorgung VOR der Reise sichern — die 28.08.-Spirale
    # startete genau hier (Basis-Feuer verlosch unbefestigt während des Trips).
    _ensure_fire_supply(game)
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
        prop = ["make_sharp_stone","create_tinder","start_fire","cook_meat","make_fur_cloak",
                "make_bandage","make_poultice","treat_cut","treat_strain"]
        acted=False
        for pid in prop:
            if pid in game.available_processes():
                g.shot(lambda: game.execute_process(pid)); acted=True; break
        if acted: continue
        # --- 2b. Lücken-Schritt (BL 02.09): available_processes() sieht die
        # Engine-Gates von sharpen_tool nicht (Condition des Worn-Tools) —
        # ein prop-Eintrag würde nur NO_WORN_TOOL spinnen. Stattdessen: nur
        # schärfen, wenn wirklich ein Werkzeug unter Volllast ist (Szenen-
        # Check im Helper). treat_cut/treat_strain baut _treat_if_injured
        # in _warm_here auf, sobald Verletzungen anfallen — die Szenen sind
        # dort abgedeckt, der prop-Scan verpasst sie nur, solange
        # make_bandage/make_poultice davor available bleiben.
        # (Nachcommit 04.09.: Messung via g.shot, damit eine sharpen-
        # Neuentdeckung ins Timeline-Register fällt; Gate = Worn-Tool + Flint,
        # und nur solange der Prozess unbekannt ist — sonst verbrennt der Bot
        # seinen Flint im Leerlauf. Die künstliche Szenen-Aufbau-Variante
        # (1c/1d: Gipfel-Trips + Wear-Provozieren) wurde im 20-Sweep strikt
        # schlechter (17/20 Tode vs. 12 Baseline, Exhaustion 10 vs. 19.5) und
        # nach Plan-Rückroll-Regel entfernt — ehrliches 0/20 bleibt dokumentiert
        # (tests/test_guided_full.py, xfail) = Spiel-Signal für den Direktor.)
        if ("sharpen_tool" not in game.player.known_processes
                and _worn_tool(game) is not None
                and have_qty(game, "flint_shard", 1)):
            g.shot(lambda: game.execute_process("sharpen_tool"))
            acted = True; continue
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