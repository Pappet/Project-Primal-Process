# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).
> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft (v1) | 34.500 | -27.500 ↑ besser | niedriger | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability (v1) | 0.750 | -0.250 ↓ schlechter | höher | Anteil erreichbarer Blueprints (N=50) |
| craft_variety (v1) | 3.000 | +2.000 ↑ besser | höher | Unterschiedliche Craft-Typen in 100 Aktionen |
| skill_spread (v1) | 0.216 | -0.043 ↓ schlechter | höher | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality (v2) | 1.000 | ±0 | höher | Anteil informativer Rückmeldungen (Label-Stimmt) |
| content_reachable (v1) | 1.000 | ±0 | höher | Anteil sammelbarer definierter Items |
| session_depth (v1) | 25.000 | -1.000 ↓ schlechter | höher | Aktionen bis nichts Neues passiert |
| discovery_gap (v1) | 0.375 | +0.125 | im Band | Abstand erreichbar vs. tatsächlich gefunden |
| forage_pressure (v1) (Probe bis 20.08.) | 0.707 | — (Baseline) | über Band | Anteil Sammel-Versuche an nicht-volem Node (Knappheit) |

## discovery_gap — Zielband

**Band: 0.2 – 0.6.** Keine Richtung (kein "höher = besser"). Unter 0.2 nimmt das Spiel den Spieler an die Hand; über 0.6 ist es faktisch unentdeckbar. `blueprint_reachability` (0.75) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (0.375) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## forage_pressure — Zielband

**Band: 0.1 – 0.5.** Keine Richtung (kein "höher = besser"). Unter 0.1 nimmt das Spiel den Spieler an die Hand; über 0.5 ist es faktisch unentdeckbar. `blueprint_reachability` (None) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (None) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## Details (2026-08-07)

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
    "value": 0.75,
    "per_blueprint": {
      "axe": true,
      "axe_bone": true,
      "axe_stone": true,
      "knife": true,
      "knife_bone": true,
      "knife_stone": true,
      "spear": false,
      "spear_bound": false
    },
    "version": 1
  },
  "craft_variety": {
    "value": 3.0,
    "p25": 2,
    "p75": 3,
    "n_runs": 20,
    "version": 1
  },
  "skill_spread": {
    "value": 0.216,
    "p25": 0.158,
    "p75": 0.266,
    "n_runs": 20,
    "version": 1
  },
  "feedback_quality": {
    "value": 1.0,
    "p25": 1.0,
    "p75": 1.0,
    "n_runs": 20,
    "version": 2
  },
  "content_reachable": {
    "value": 1.0,
    "reachable_count": 13,
    "defined_count": 13,
    "reachable": [
      "berries",
      "bone",
      "cooked_meat",
      "fire_pit",
      "flint_shard",
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
    "value": 0.375,
    "blueprint_reachability": 0.75,
    "naive_discovery_rate": 0.375,
    "naive_p25": 0.375,
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
  }
}
```
