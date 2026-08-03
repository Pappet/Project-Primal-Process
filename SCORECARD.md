# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft | 63 | — (Baseline) | niedriger = besser | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability | 1.000 | — (Baseline) | höher = besser | Anteil erreichbarer Blueprints (N=50) |
| craft_variety | 0.500 | — (Baseline) | höher = besser | Unterschiedliche Craft-Typen in 100 Aktionen |
| skill_spread | 0.315 | — (Baseline) | höher = besser | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality | 1.000 | — (Baseline) | höher = besser | Anteil informativer Rückmeldungen |
| content_reachable | 0.667 | — (Baseline) | höher = besser | Anteil sammelbarer definierter Items |
| session_depth | 24.000 | — (Baseline) | höher = besser | Aktionen bis nichts Neues passiert |

## Details (2026-08-03)

```json
{
  "actions_to_first_craft": {
    "value": 63,
    "p25": 41,
    "p75": 118,
    "n_runs": 17
  },
  "blueprint_reachability": {
    "value": 1.0,
    "per_blueprint": {
      "axe": true,
      "knife": true
    }
  },
  "craft_variety": {
    "value": 0.5,
    "p25": 0,
    "p75": 1,
    "n_runs": 20
  },
  "skill_spread": {
    "value": 0.315,
    "p25": 0.289,
    "p75": 0.386,
    "n_runs": 20
  },
  "feedback_quality": {
    "value": 1.0,
    "p25": 1.0,
    "p75": 1.0,
    "n_runs": 20
  },
  "content_reachable": {
    "value": 0.667,
    "reachable_count": 6,
    "defined_count": 9,
    "reachable": [
      "berries",
      "flint_shard",
      "mushroom",
      "pebble",
      "plant_fiber",
      "stick"
    ],
    "unreachable": [
      "cooked_meat",
      "raw_meat",
      "reeds"
    ]
  },
  "session_depth": {
    "value": 24.0,
    "p25": 19,
    "p75": 30,
    "n_runs": 20
  }
}
```
