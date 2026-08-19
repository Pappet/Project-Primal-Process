# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).
> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft (v1) | 34.500 | ±0 | niedriger | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability (v1) | 1.000 | ±0 | höher | Anteil erreichbarer Blueprints (N=50) |
| craft_variety (v1) | 3.500 | +0.500 ↑ besser | höher | Unterschiedliche Craft-Typen in 100 Aktionen |
| skill_spread (v1) | 0.216 | ±0 | höher | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality (v2) | 0.916 | -0.084 ↓ schlechter | höher | Anteil informativer Rückmeldungen (Label-Stimmt) |
| content_reachable (v1) | 1.000 | ±0 | höher | Anteil sammelbarer definierter Items |
| session_depth (v1) | 25.000 | ±0 | höher | Aktionen bis nichts Neues passiert |
| discovery_gap (v1) | 0.600 | -0.025 | im Band | Abstand erreichbar vs. tatsächlich gefunden |
| forage_pressure (v1) (Probe bis 20.08.) | 0.707 | ±0 | über Band | Anteil Sammel-Versuche an nicht-volem Node (Knappheit) |
| warmth_stability (v1) (Probe bis 27.08.) | 0.460 | ±0 | im Band | Anteil Kälte-Stress-Ticks, die warm überstanden werden (Feuer/Isolation) |

## discovery_gap — Zielband

**Band: 0.2 – 0.6.** Keine Richtung (kein "höher = besser"). Unter 0.2 nimmt das Spiel den Spieler an die Hand; über 0.6 ist es faktisch unentdeckbar. `blueprint_reachability` (1.0) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (0.4) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## forage_pressure — Zielband

**Band: 0.1 – 0.5.** Keine Richtung (kein "höher = besser"). Unter 0.1 nimmt das Spiel den Spieler an die Hand; über 0.5 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## warmth_stability — Zielband

**Band: 0.4 – 0.9.** Keine Richtung (kein "höher = besser"). Unter 0.4 nimmt das Spiel den Spieler an die Hand; über 0.9 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## Details (2026-08-19)

```json
{
  "actions_to_first_craft": {
    "value": 34.5,
    "p25": 24,
    "p75": 48,
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
    "value": 3.5,
    "p25": 3,
    "p75": 5,
    "n_runs": 20,
    "version": 1
  },
  "skill_spread": {
    "value": 0.216,
    "p25": 0.158,
    "p75": 0.258,
    "n_runs": 20,
    "version": 1
  },
  "feedback_quality": {
    "value": 0.916,
    "p25": 0.911,
    "p75": 0.925,
    "n_runs": 20,
    "version": 2
  },
  "content_reachable": {
    "value": 1.0,
    "reachable_count": 16,
    "defined_count": 16,
    "reachable": [
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
      "raw_meat",
      "reeds",
      "sharp_stone",
      "stick",
      "tinder"
    ],
    "unreachable": [],
    "version": 1
  },
  "session_depth": {
    "value": 25.0,
    "p25": 21,
    "p75": 43,
    "n_runs": 20,
    "version": 1
  },
  "discovery_gap": {
    "value": 0.6,
    "blueprint_reachability": 1.0,
    "naive_discovery_rate": 0.4,
    "naive_p25": 0.3,
    "naive_p75": 0.5,
    "band": [
      0.2,
      0.6
    ],
    "version": 1
  },
  "forage_pressure": {
    "value": 0.707,
    "p25": 0.612,
    "p75": 0.862,
    "n_runs": 20,
    "version": 1
  },
  "warmth_stability": {
    "value": 0.46,
    "p25": 0.46,
    "p75": 0.46,
    "n_runs": 20,
    "version": 1
  }
}
```
