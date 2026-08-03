# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only).

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft | 43 | — (Baseline) | niedriger = besser | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability | 1.000 | — (Baseline) | höher = besser | Anteil erreichbarer Blueprints (N=50) |
| craft_variety | 1 | — (Baseline) | höher = besser | Unterschiedliche Crafts in 100 Aktionen |
| skill_spread | 0.298 | — (Baseline) | höher = besser | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality | 0.600 | — (Baseline) | höher = besser | Anteil informativer Rückmeldungen |
| content_reachable | 0.667 | — (Baseline) | höher = besser | Anteil sammelbarer definierter Items |
| session_depth | 16 | — (Baseline) | höher = besser | Aktionen bis nichts Neues passiert |

## Baseline-Details (2026-08-03)

```json
{
  "actions_to_first_craft": 43,
  "blueprint_reachability": {
    "value": 1.0,
    "per_blueprint": {
      "axe": true,
      "knife": true
    }
  },
  "craft_variety": {
    "distinct_results": 1,
    "value": 1
  },
  "skill_spread": {
    "optimal_ticks": 258,
    "random_ticks": 181,
    "value": 0.298
  },
  "feedback_quality": {
    "value": 0.6,
    "informative": 27,
    "total": 45
  },
  "content_reachable": {
    "value": 0.667,
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
    "value": 16,
    "stall_limit": 15
  }
}
```
