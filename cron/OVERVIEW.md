# Primal Process — Cron-Jobs Übersicht

> Exportiert am 2026-08-30 (Direktor-Refresh) aus `hermes cron list`

| Job | Schedule | Rolle | Nächster Run | Status |
|-----|----------|-------|--------------|--------|
| Primal Process Play | `0 9 * * 1,3,5` | Echte Runs, Scorecard, Langeweile-Stelle finden (Mo/Mi/Fr 09:00) | Mo 31.08. 09:00 | ok (28.08.) |
| Primal Process Research-Metric | `0 10 * * 2` | Schwächste Metrik → genau 1 Spec (Di 10:00) | Di 01.09. 10:00 | ok (25.08.) |
| Primal Process Research-Explore | `0 10 * * 4` | Freie Suche, Spec + Metrik-Vorschlag (Do 10:00) | Do 03.09. 10:00 | ok (27.08.) |
| Primal Process Dev | `0 14 * * 1,2,3,4,5,6` | Tasks aus PLAN.md / oberster Spec (Mo–Sa 14:00) | Mo 31.08. 14:00 | error 29.08. (Session-Abbruch nach Commit 1; SPEC-011-Landung vom Direktor nachcommittet — siehe JOURNAL 30.08.) |
| Primal Process Direktor | `0 18 * * 0` | Schreibt PLAN.md neu, darf Cron-Jobs ändern (So 18:00) | So 06.09. 18:00 | ok (23.08.) |

Einzelne Prompts: `play.md`, `research.md`, `research-explore.md`, `dev.md`, `direktor.md`.
Grenze für alle: `CONSTITUTION.md` (gültig seit 2026-08-03).
Probezeit: neue Metriken laufen 14 Tage, bevor sie Plan-Ziele werden dürfen.
