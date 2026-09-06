# Primal Process — Cron-Jobs Übersicht

> Exportiert am 2026-09-06 (Direktor-Refresh) aus `hermes cron list`

| Job | Schedule | Rolle | Nächster Run | Status |
|-----|----------|-------|--------------|--------|
| Primal Process Play | `0 9 * * 1,3,5` | Echte Runs, Scorecard, Langeweile-Stelle finden (Mo/Mi/Fr 09:00) | Mo 07.09. 09:00 | ok (04.09.) |
| Primal Process Research-Metric | `0 10 * * 2` | Schwächste Metrik → genau 1 Spec (Di 10:00) | Di 08.09. 10:00 | ok (01.09.) — 06.09.: Plan-Mode-Skill entfernt (Pläne wurden nie ausgeführt) |
| Primal Process Research-Explore | `0 10 * * 4` | Freie Suche, Spec + Metrik-Vorschlag (Do 10:00) | Do 10.09. 10:00 | ok (03.09.) — 06.09.: Plan-Mode-Skill entfernt (Pläne wurden nie ausgeführt) |
| Primal Process Dev | `0 14 * * 1,2,3,4,5,6` | Tasks aus PLAN.md / oberster Spec (Mo–Sa 14:00) | Mo 07.09. 14:00 | ok (04.09., Session-Abbruch 29.08. längst adoptiert) |
| Primal Process Direktor | `0 18 * * 0` | Schreibt PLAN.md neu, darf Cron-Jobs ändern (So 18:00) | So 13.09. 18:00 | ok (06.09.) |

Einzelne Prompts: `play.md`, `research.md`, `research-explore.md`, `dev.md`, `direktor.md`.
Grenze für alle: `CONSTITUTION.md` (gültig seit 2026-08-03).
Probezeit: neue Metriken laufen 14 Tage, bevor sie Plan-Ziele werden dürfen.
