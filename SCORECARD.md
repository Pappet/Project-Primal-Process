# Project Primal Process — Scorecard

> Fitness-Signal: misst das **Spiel**, nicht die Prozesstreue. Schema v2.
> Erzeugt von `tools/scorecard.py` (deterministisch, stdlib only, Seed-Satz).
> Metriken mit `(vN)` sind versioniert; umdefinierte Metriken zeigen im Delta `— (neu definiert)`.

| Metrik | Wert | Δ Vorwoche | Richtung | Beschreibung |
|--------|------|-----------|----------|--------------|
| actions_to_first_craft (v1) | 62 | -1.000 ↑ besser | niedriger | Aktionen bis zum ersten erfolgreichen Craft (naiv) |
| blueprint_reachability (v1) | 1.000 | ±0 | höher | Anteil erreichbarer Blueprints (N=50) |
| craft_variety (v1) | 1.000 | +0.500 ↑ besser | höher | Unterschiedliche Craft-Typen in 100 Aktionen |
| skill_spread (v1) | 0.259 | -0.056 ↓ schlechter | höher | Überlebens-Spanne optimal vs. zufällig |
| feedback_quality (v2) | 1.000 | ±0 | höher | Anteil informativer Rückmeldungen (Label-Stimmt) |
| content_reachable (v1) | 1.000 | +0.333 ↑ besser | höher | Anteil sammelbarer definierter Items |
| session_depth (v1) | 26.000 | +2.000 ↑ besser | höher | Aktionen bis nichts Neues passiert |
| discovery_gap (v1) | 0.250 | -0.250 | im Band | Abstand erreichbar vs. tatsächlich gefunden |

## discovery_gap — Zielband

**Band: 0.2 – 0.6.** Keine Richtung (kein "höher = besser"). Unter 0.2 nimmt das Spiel den Spieler an die Hand; über 0.6 ist es faktisch unentdeckbar. `blueprint_reachability` (1.0) misst, was ein Orakel erreichen kann; `naive_discovery_rate` (0.75) was ein Spieler wirklich findet. Der Abstand dazwischen ist das eigentliche Spiel.


## Details (2026-08-05)

```json
{
  "actions_to_first_craft": {
    "value": 62,
    "p25": 37,
    "p75": 93,
    "n_runs": 15,
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
    "value": 1.0,
    "p25": 1,
    "p75": 2,
    "n_runs": 20,
    "version": 1
  },
  "skill_spread": {
    "value": 0.259,
    "p25": 0.213,
    "p75": 0.288,
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
    "reachable_count": 12,
    "defined_count": 12,
    "reachable": [
      "berries",
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
    "value": 26.0,
    "p25": 21,
    "p75": 33,
    "n_runs": 20,
    "version": 1
  },
  "discovery_gap": {
    "value": 0.25,
    "blueprint_reachability": 1.0,
    "naive_discovery_rate": 0.75,
    "naive_p25": 0.5,
    "naive_p75": 1.0,
    "band": [
      0.2,
      0.6
    ],
    "version": 1
  }
}
```
