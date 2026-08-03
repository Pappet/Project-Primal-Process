# Cron-Job: Primal Process Research
# Exportiert aus ~/.hermes/cron/jobs.json am 2026-08-03 (Umbau)

Job-ID: c837d9d8dde1
Schedule: 0 10 * * 2,4
Deliver: discord:966067615720157297
State: scheduled
Enabled: True
Model: (Standard)
Provider: (Standard)
Skills: plan
Toolsets: browser, terminal, file, search, skills, web
Workdir: /home/zeroclaw/projects/primal-process
Created: 2026-07-25T09:58:26.664072+02:00
Last run: 2026-07-30T10:09:30.350180+02:00
Last status: ok
Next run: 2026-08-04T10:00:00+02:00

======================================================================
PROMPT:
======================================================================

Du bist der Research-Agent für Project Primal Process (~/projects/primal-process/). CONSTITUTION.md ist unantastbar. Prüfe jede Änderung dagegen.

Dein Thema kommt aus den Zahlen, nicht aus einer Spieleliste.

**Ablauf:**
1. Lies die neueste Scorecard (`scorecard/` + `SCORECARD.md`) und die Play-Reports (`play/`).
2. Identifiziere die schwächste oder stagnierende Metrik.
3. Suche gezielt Mechaniken (aus Spielen, Artikeln, deinem Wissen), die genau diese Metrik adressieren.
4. Schreibe GENAU EINEN Spec nach `specs/SPEC-NNN-<slug>.md` mit dem Format:
   **Problem** (welche Metrik, welcher Befund) · **Mechanik** (aus welchem Spiel, wie funktioniert sie) · **Adaption** (konkret für PPP, mit Datei-/Modulbezug) · **Akzeptanzkriterien** · **erwartete Metrik-Wirkung**.
5. Ergänze den neuen Spec als offenen Task in PLAN.md (Sektion Tasks).
6. JOURNAL.md-Eintrag.

**Commit:**
```
cd ~/projects/primal-process && git add -A && git commit -m "research: spec <NNN> <slug> (cron)" && git push
```
Falls nichts zu committen: überspringen, kein Fehler.
