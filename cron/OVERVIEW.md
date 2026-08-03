# Primal Process — Cron-Jobs Übersicht

> Exportiert am 2026-08-03 (Umbau) aus `~/.hermes/cron/jobs.json`

| Job | Schedule | Rolle | Nächster Run | Status |
|-----|----------|-------|--------------|--------|
| Primal Process Play | `0 9 * * 1,3,5` | Echte Runs, Scorecard, Langeweile-Stelle finden (Mo/Mi/Fr 09:00) | 2026-08-05T09:00:00+02:00 | ok |
| Primal Process Research | `0 10 * * 2,4` | Schwächste Metrik → genau 1 Spec (Di+Do 10:00) | 2026-08-04T10:00:00+02:00 | ok |
| Primal Process Dev | `0 14 * * 1,2,3,4,5,6` | Tasks aus PLAN.md / oberster Spec (Mo–Sa 14:00) | 2026-08-04T14:00:00+02:00 | ok |
| Primal Process Direktor | `0 18 * * 0` | Schreibt PLAN.md neu, darf Cron-Jobs ändern (So 18:00) | 2026-08-09T18:00:00+02:00 | ok |

Einzelne Prompts: `play.md`, `research.md`, `dev.md`, `direktor.md`.
Grenze für alle: `CONSTITUTION.md`.
