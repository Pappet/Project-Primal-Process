# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).
> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft (v1) | 63 | — (Baseline) | niedriger | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability (v1) | 1.000 | — (Baseline) | höher | Anteil erreichbarer Blueprints (N=50) |
| craft_variety (v1) | 0.500 | — (Baseline) | höher | Unterschiedliche Craft-Typen in 100 Aktionen |
| skill_spread (v1) | 0.315 | — (Baseline) | höher | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality (v2) | 1.000 | — (Baseline) | höher | Anteil informativer Rückmeldungen (Label-Stimmt) |
| content_reachable (v1) | 0.667 | — (Baseline) | höher | Anteil sammelbarer definierter Items |
| session_depth (v1) | 24.000 | — (Baseline) | höher | Aktionen bis nichts Neues passiert |
| discovery_gap (v1) | 0.500 | — (Baseline) | im Band | Abstand erreichbar vs. tatsächlich gefunden |

## discovery_gap — Zielband

**Band: 0.2 – 0.6.** Keine Richtung (kein "höher = besser"). Unter 0.2 nimmt das Spiel den Spieler an die Hand; über 0.6 ist es faktisch unentdeckbar. `blueprint_reachability` (1.0) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (0.5) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## Details (2026-08-03)

```json
{
  "actions_to_first_craft": {
    "value": 63,
    "p25": 41,
    "p75": 118,
    "n_runs": 17,
    "version": 1
  },
  "blueprint_reachability": {
    "value": 1.0,
    "per_blueprint": {
      "axe": true,
      "knife": true
    },
    "version": 1
  },
  "craft_variety": {
    "value": 0.5,
    "p25": 0,
    "p75": 1,
    "n_runs": 20,
    "version": 1
  },
  "skill_spread": {
    "value": 0.315,
    "p25": 0.289,
    "p75": 0.386,
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
    ],
    "version": 1
  },
  "session_depth": {
    "value": 24.0,
    "p25": 19,
    "p75": 30,
    "n_runs": 20,
    "version": 1
  },
  "discovery_gap": {
    "value": 0.5,
    "blueprint_reachability": 1.0,
    "naive_discovery_rate": 0.5,
    "naive_p25": 0.0,
    "naive_p75": 1.0,
    "band": [
      0.2,
      0.6
    ],
    "version": 1
  }
}
```
