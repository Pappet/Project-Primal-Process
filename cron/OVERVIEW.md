# Primal Process — Cron-Jobs Übersicht

> Exportiert am 2026-08-03T15:28:07.761281 aus `~/.hermes/cron/jobs.json`

| Job | Schedule | Beschreibung | Nächster Run | Status |
|-----|----------|--------------|--------------|--------|
| Primal Process Dev | `0 14 * * 1,2,3,4,5,6` | Implementierung der Sprint-Tasks (Mo-Sa 14:00); summoned Review wenn Sprint leer | 2026-08-04T14:00:00+02:00 | ok |
| Primal Process QA | `0 16 * * 6` | Playtest & Balance aus User-Sicht (Sa 16:00) | 2026-08-08T16:00:00+02:00 | ok |
| Primal Process Research | `0 10 * * 2,4` | Referenzspiel-Analyse (Di+Do 10:00) | 2026-08-04T10:00:00+02:00 | ok |
| Primal Process Review | `0 18 * * 0` | Weekly Triage + Sprint-Planung, kann mid-week gesummondt werden (So 18:00) | 2026-08-09T18:00:00+02:00 | ok |

Einzelne Prompts: `research.md`, `dev.md`, `review.md`, `qa.md`
