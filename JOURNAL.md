# Project Primal Process — Journal

> Geführt von Zero. Chronologisch. Jeder Eintrag = eine Session (Research, Dev, Review).
> Format: `## YYYY-MM-DD — [Typ] Titel`

---

## 2026-07-26 — [Setup] Projektübernahme & Initialisierung

- Repo von GitHub geklont, analysiert (~400 Zeilen, 8 Items, 2 Blueprints, 3 Orte)
- Stärke: Tag-basiertes Emergent Crafting als Kernmechanik
- Schwächen: kein Save/Load, Content-arm, keine Gefahren, keine Persistenz
- Vision festgelegt: Primitive Technology Discovery Game (Steinzeit → Eisenzeit)
- 4-Phasen-Plan über ~12 Wochen erstellt
- 3 Cron-Jobs eingerichtet: Research (Di+Do), Dev (Mo+Mi+Fr), Review (So)
- Repo: ~/projects/primal-process/, Remote: Pappet/Project-Primal-Process

## 2026-07-26 — [Setup] Session-State, Tests, Doc-Struktur

**Claude-Review umgesetzt:**
1. Session-State: Dev-Prompt hat jetzt Crash-Recovery (git status, `[~]` Marker, WIP-Commits)
2. Test-Fundament: M0.2b (pytest + Smoke-Tests) vor M0.3 eingeschoben
3. Kalender: Phase 0 KW 30-33, 2 Spiele/Research-Session
4. Task-Granularität: Sub-Task-Regel im Dev-Prompt
5. Review-Guardrails: Phasen-Schutz, "Fragen an Peter"-Sektion
6. Doc-Wachstum: research/-Ordner + INDEX.md, JOURNAL-Archivierung, Triaged-Cleanup
7. Backlog-Format: Datum+Quelle+Einzeiler-Konvention

Alle 3 Cron-Jobs aktualisiert.