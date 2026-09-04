# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).
> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft (v1) | 9.500 | ±0 | niedriger | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability (v1) | 1.000 | ±0 | höher | Anteil erreichbarer Blueprints (N=50) |
| craft_variety (v2) | 5.000 | ±0 | höher | Unterschiedliche Craft-Typen (Blueprints + Prozesse) in 100 Aktionen |
| skill_spread (v1) | 0.202 | ±0 | niedriger | Überlebens-Spanne optimal vs. zufällig (fallend = gehobene Einsteiger-Decke) |
| feedback_quality (v3) | 1.000 | ±0 | höher | Anteil informativer Rückmeldungen (Label-Stimmt, inkl. NEAR_MISS) |
| content_reachable (v2) | 1.000 | ±0 | höher | Anteil sammelbarer definierter Items (inkl. Node-Ref-Prüfung) |
| session_depth (v2) (Probe bis 08.09.) | 63.000 | ±0 | höher | Aktionen bis nichts Neues passiert (ziel-bewusster naiver Bot, v2) |
| discovery_gap (v1) | 0.600 | ±0 | im Band | Abstand erreichbar vs. tatsächlich gefunden |
| forage_pressure (v2) (Probe bis 11.09.) | 0.000 | ±0 | unter Band | Anteil Sammel-Versuche, die an Erschöpfung verweigert oder deutlich gemindert werden (gefühlte Knappheit) |
| warmth_stability (v1) (Probe bis 27.08.) | 0.460 | ±0 | im Band | Anteil Kälte-Stress-Ticks, die warm überstanden werden (Feuer/Isolation) |
| recovery_stability (v1) (Probe bis 03.09.) | 0.375 | ±0 | im Band | Anteil Verletzungs-Ticks, die Behandlung + Ruhe abwenden (Verband/Umschlag) |
| gear_uptime (v1) (Probe bis 11.09.) | 0.994 | ±0 | über Band | Anteil werkzeugpflichtiger Stress-Ticks mit nutzbarem Werkzeug (>= Warnschwelle) |

## discovery_gap — Zielband

**Band: 0.2 – 0.6.** Keine Richtung (kein "höher = besser"). Unter 0.2 nimmt das Spiel den Spieler an die Hand; über 0.6 ist es faktisch unentdeckbar. `blueprint_reachability` (1.0) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (0.4) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## forage_pressure — Zielband

**Band: 0.1 – 0.5.** Keine Richtung (kein "höher = besser"). Unter 0.1 nimmt das Spiel den Spieler an die Hand; über 0.5 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## warmth_stability — Zielband

**Band: 0.4 – 0.9.** Keine Richtung (kein "höher = besser"). Unter 0.4 nimmt das Spiel den Spieler an die Hand; über 0.9 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## recovery_stability — Zielband

**Band: 0.3 – 0.7.** Keine Richtung (kein "höher = besser"). Unter 0.3 nimmt das Spiel den Spieler an die Hand; über 0.7 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## gear_uptime — Zielband

**Band: 0.7 – 0.95.** Keine Richtung (kein "höher = besser"). Unter 0.7 nimmt das Spiel den Spieler an die Hand; über 0.95 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## Details (2026-09-04)

```json
{
  "actions_to_first_craft": {
    "value": 9.5,
    "p25": 4,
    "p75": 12,
    "n_runs": 20,
    "version": 1
  },
  "blueprint_reachability": {
    "value": 1.0,
    "per_blueprint": {
      "axe": true,
      "axe_bone": true,
      "axe_stone": true,
      "knife": true,
      "knife_bone": true,
      "knife_stone": true,
      "spear": true,
      "spear_bound": true,
      "rope": true,
      "cord_spear": true
    },
    "version": 1
  },
  "craft_variety": {
    "value": 5.0,
    "p25": 4,
    "p75": 6,
    "n_runs": 20,
    "version": 2
  },
  "skill_spread": {
    "value": 0.202,
    "p25": 0.15,
    "p75": 0.226,
    "n_runs": 20,
    "version": 1
  },
  "feedback_quality": {
    "value": 1.0,
    "p25": 1.0,
    "p75": 1.0,
    "n_runs": 20,
    "version": 3
  },
  "content_reachable": {
    "value": 1.0,
    "reachable_count": 18,
    "defined_count": 18,
    "reachable": [
      "bandage",
      "berries",
      "bone",
      "clay_lump",
      "cooked_meat",
      "fire_pit",
      "flint_shard",
      "fur_cloak",
      "log_oak",
      "mushroom",
      "pebble",
      "plant_fiber",
      "poultice",
      "raw_meat",
      "reeds",
      "sharp_stone",
      "stick",
      "tinder"
    ],
    "unreachable": [],
    "dangling_refs": [],
    "version": 2
  },
  "session_depth": {
    "value": 63.0,
    "p25": 47,
    "p75": 76,
    "n_runs": 20,
    "version": 2
  },
  "discovery_gap": {
    "value": 0.6,
    "blueprint_reachability": 1.0,
    "naive_discovery_rate": 0.4,
    "naive_p25": 0.3,
    "naive_p75": 0.4,
    "band": [
      0.2,
      0.6
    ],
    "version": 1
  },
  "forage_pressure": {
    "value": 0.0,
    "p25": 0.0,
    "p75": 0.03,
    "n_runs": 20,
    "version": 2
  },
  "warmth_stability": {
    "value": 0.46,
    "p25": 0.46,
    "p75": 0.46,
    "n_runs": 20,
    "version": 1
  },
  "recovery_stability": {
    "value": 0.375,
    "p25": 0.375,
    "p75": 0.375,
    "n_runs": 20,
    "version": 1
  },
  "gear_uptime": {
    "value": 0.994,
    "p25": 0.994,
    "p75": 1.0,
    "n_runs": 20,
    "version": 1
  }
}
```
