# Cron-Job: Primal Process Research
# Exportiert aus ~/.hermes/cron/jobs.json am 2026-08-03T15:28:44.977179+02:00

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

Du arbeitest am Project Primal Process (~/projects/primal-process/). Deine Aufgabe: Analysiere Referenzspiele und schreibe Research-Notes.

1. Lies PLAN.md und JOURNAL.md um den aktuellen Stand zu verstehen.
2. Wähle das nächste Spiel aus der geplanten Liste in PLAN.md.
3. Recherchiere dessen Mechaniken.
4. Schreibe research/<spiel-name>.md mit 5 Mechaniken + Top-3-Adaptionen.
5. Aktualisiere research/INDEX.md mit Querverweisen.
6. Aktualisiere JOURNAL.md mit Session-Eintrag.
7. Füge neue Ideen zu BACKLOG.md hinzu.

**WICHTIG — Nach allen Schreiboperationen:**
```
cd ~/projects/primal-process && git add -A && git commit -m "research: <spiel-name> analysis (cron)" && git push
```
Falls es nichts zu committen gibt (keine Änderungen), überspringe den Commit — kein Fehler.
