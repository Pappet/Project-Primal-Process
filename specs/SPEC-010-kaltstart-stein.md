# SPEC-010 — Kaltstart-Brücke: Knappbarer Startstein im Waldrand (actions_to_first_craft)

> **Modus:** Research (Metrik-Modus) · **Datum:** 2026-08-25
> **STATUS: erledigt (Dev 2026-08-26, gepaarter Batch mit NEAR_MISS-Volldeckung; actions_to_first_craft 34.5 → 9.5)**
> **Ziel-Metrik:** `actions_to_first_craft` (34.5, flach, `niedriger = besser`)
> **Grenze:** CONSTITUTION.md — keine Metrik-Redefinition, kein Rezept-Leak, kein GUI, stdlib only.

---

## Problem

`actions_to_first_craft` steht seit 08-07 **flach auf 34.5** (p25=24, p75=48, n=20) — die
komplette Mess-Historie klickt auf denselben Wert, obwohl SPEC-008 (rope/cord_spear) und
SPEC-009 (Verletzung/Heilung) seitdem landeten. Das ist die **Kaltstart-Friktion**: Ein
naiver Spieler braucht im Schnitt **34.5 Aktionen** (p75: 48!), bis sein erster Craft
gelingt — also fast die Länge der gesamten entdeckbaren Welt (`session_depth` 25). Die
Langeweile beginnt nicht erst am `session_depth`-Punkt, sondern schon vor dem ersten
Werkzeug.

**Ursache (diagnostiziert, nicht vermutet):** Der erste Craft braucht ein **Kopf-Material**
(`FLINT`/`BONE`/`STONE`), das im Start-Biome `forest_edge` **gar nicht vorkommt**.
`forest_edge` hat nur `stick` (RIGID), `plant_fiber` (FIBER), `berries`, `log_oak`
(CHOPPING-gated) und `raw_meat` (PROJECTILE-gated) — **kein einziges HARD/SHARP/STONE-
Item**. Der naive Spieler muss zum kalten `mountain_peak` (FLINT, STONE) oder zur
`hidden_cave` (BONE) *reisen*, friert dort (Exposure 1.0) ein und verbrennt Aktionen.
Probe-Instrumentierung (`_run_first_craft` über alle 20 Seeds): **Median 26.5 Aktionen,
bis das Inventar überhaupt ein komplettes 2-Slot-Blueprint-Material hält** — erst danach
ist das Craften Selektions-Lotterie. Die erste Werkzeug-Ressource sitzt schlicht nicht an
dem Ort, an dem der Spieler startet.

**Warum nicht `session_depth` / `discovery_gap`?** `discovery_gap` ist gated (REC-002,
nicht parallel verifizierbar) — laut Messregeln kein Ziel. `session_depth` ist der Nordstern
und hat bereits SPEC-006 (Werkzeug als Zutat) verplant — eine weitere Discovery-Schicht
würde in dessen Akzeptanzkriterien kollidieren. `actions_to_first_craft` ist verifizierbar,
nicht gated, nicht in Probezeit, und hat seit sechs Readings **keine** Signatur: der
**sauberste** schwächste Metrik-Fall par excellence.

---

## Mechanik (Quelle: echte Spiele)

**Kopf-Material dort, wo die Hand es findet — "primitive tool at hand".**

- **Minecraft:** Erste Axt = Holz, das man am Spawn "an der Hand" (Holzblock vor der Nase)
  bekommt — der erste Craft ist in ~2 Aktionen möglich. Das Tutorial friert nicht ein.
- **UnReal World / Vintage Story:** Knapping — ein **roher** Stein in der Umgebung ergibt
  das erste Werkzeug, **bevor** man zum harten Rohstoff wandert. Die erste Stufe nutzt ein
  Material, das der Start-Biom selbst trägt.
- **The Long Dark:** Das erste Werkzeug ist aus dem umstehenden, leicht erreichbaren
  Material der Starts immer machbar — der Lernbogen ist kurz, die Gefahr beginnt mit der
  Weite danach.

**Gemeinsam:** Nicht "mehr Content am Ende anhangen" (das bläht `content_reachable` und
verändert `craft_variety`), sondern **die erste Stufe in den Start-Biom legen** — ein
verfügbares, "an der Hand"-rohes Werkzeugmaterial, damit der erste Craft kurz und
**sicher** (kaltfrei) wird.

## Adaption (konkret für PPP)

**Eins: Knappbarer "Kiesel" in `forest_edge`.** In `data/locations.json` bekommt der
Start-Biome **einen** zusätzlichen Node:

```json
{
  "result_template_id": "pebble",
  "min_qty": 1, "max_qty": 2,
  "chance": 0.6,
  "req_perception": 0.0,
  "req_tool_tag": null,
  "max_stock": 8.0,
  "regen_per_tick": 0.04
}
```

- `pebble` trägt `STONE` (+ `PROJECTILE`, bereits in `TEMPLATE_DB`). Der naive Spieler
  startet in `forest_edge` und hat damit **sofort ein Head-Material in Reichweite** →
  `knife_stone` / `axe_stone` werden als **erster Craft** möglich, ohne den kalten
  `mountain_peak`-Aufwand.
- **Kein Endlosbrunnen:** `max_stock` klein (8.0), Regeneration langsam (0.04) — nur die
  **erste Schleife** der Kaltstart-Friktion gebrochen (SPEC-004-Muster: scarcer Rohstoff =
  kleiner Stand, damit er kein Dauer-Fountain wird).
- `content_reachable`: `pebble` + `sharp_stone` existieren bereits in `items.json` und sind
  via Prozess `make_sharp_stone` (braucht 2× pebble) sowieso erreichbar. Der neue Node
  **ändert keine Zähler**, er holt den Fund nur **an den Start**.
- **Kein Node für FLINT** — `flint_shard` (HARD+SHARP+FLINT) bleibt der rare
  `mountain_peak`-Fund. Das erhält die **Dreifaltigkeit der Heads** (STONE leicht / BONE
  mittel / FLINT mühsam) und den Discovery-Band: `knife_stone` ist eine *erste* Stufe,
  nicht das ganze Spiel.

**2. `make_sharp_stone` als unbewaffneter Früh-Prozess nutzen (Feedback-Schleife):** Der
Prozess existiert schon (inputs 2× pebble, no tools). Mit dem neuen Start-Pebble wird
`sharp_stone` früh erreichbar — direkt der 2-Slot-Craft (`STONE`+`RIGID`) und der
Knapping-Upgrade-Pfad. Beides adressiert `actions_to_first_craft`, kein Rezept-Leak.

**Firewalls:** Kein neuer Blueprint — der Blueprint-Zähler (`blueprint_reachability`) bleibt
stabil. Kein neues Item-Template (kein `TAG_LABELS`/`test_loader`-Broken). Kein
Engine-Core-Eingriff außer der Node-Liste; stdlib only.

## Akzeptanzkriterien (jede an einen verifizierbaren Effekt gebunden)

1. **Kaltstart gesenkt:** Inline-Probe (nicht `tools/scorecard.py` als `__main__` schreiben!)
   — `_run_first_craft` Median über 20 Seeds sinkt von **34.5 auf <20**. (Mit diesem Node
   gemessen: **12.5**.)
2. **Kein Mess-Bruch:** `metric_reachability` bleibt **1.0**, `metric_content_reachable`
   bleibt **1.0** (kein Zählerdenken verändert; `pebble` ist schon drin).
3. **Naive Selektion belegt:** In ≥ 8/10 Seeds ist der erste Craft ein **STONE**-Werkzeug
   (`knife_stone`/`axe_stone`/`spear` mit `pebble`) in `forest_edge` — per Play-Replay
   nachweisbar (vorher verteilt über alle 3 Biomes, Median Travel-verbrannt).
4. **Distributionsrand gezogen:** `p75` von `actions_to_first_craft` fällt unter 40 (vorher
   48) — der schlechteste Naive-Verteilungsrand wird herangeholt.
5. **Constitution:** Keine Metrik definiert/geschätzt; kein Rezept-Leak (der `pebble`-Node
   nennt keinen Craft-Befehl); kein GUI-Swap; nur data-Node. `python -m pytest` bleibt grün.

## erwartete Metrik-Wirkung

- **`actions_to_first_craft` (Hauptmetrik):** sinkt von **34.5 → ~12–15** (gemessen 12.5 im
  Inline-Probe). **niedriger = besser** → deutlicher Kaltstart-Erfolg. Grund: das erste
  Head-Material ist nicht mehr auf den kalten Peak verlegt, sondern am Start verfügbar.
- **`session_depth`:** steigt (Probe 25 → 40) — *seitige* Wirkung, weil der naive Bot mehr
  Blueprints in der frühen Phase erreicht. **Kein Konflikt mit SPEC-006:** SPEC-006 fügt
  danach eine **neue zweite Schicht** hinzu, diese Stufe hebt den **Sockel** — beide gehen
  additiv auf `session_depth`, von unten und mit der Tier-2-Seite.
- **`blueprint_reachability` / `content_reachable`:** unverändert (auf 1.0, per Inline
  nachgewiesen).
- **`craft_variety`:** nur mittelbar (die v2-Erstlesung ist 5.0; der Node fügt keine neuen
  Blueprint-/Prozess-Zähler hinzu, nur ein früheres Erreichen).
- **`discovery_gap` / Band-Metriken:** gated → explizit **nicht** Ziel; falls sie driften,
  ist der Treiber das ehrliche Kaltstart-Sockel, kein Artefakt.

## Offene Frage für Direktor/Peter

- Soll `forest_edge` nur `pebble` (STONE) oder zusätzlich einen selteneren, knappbaren
  „rohen Feuerstein"-Fund erhalten? **Empfehlung: nur `pebble`.** Ein extra FLINT-Node
  würde den `flint`-Rar-Fund entlasten und die Head-Dreifaltigkeit (STONE/BONE/FLINT) einebnen
  — die volle Resolution gehört an Dev/Direktor, nicht still in die Spekulation.
