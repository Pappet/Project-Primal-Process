# Cron-Job: Primal Process Research-Explore
# Exportiert aus ~/.hermes/cron/jobs.json am 2026-08-30 (Direktor-Refresh)

Job-ID: ba3954705006
Schedule: 0 10 * * 4
Deliver: discord:966067615720157297
State: scheduled
Enabled: True
Model: (Standard)
Provider: (Standard)
Toolsets: browser, terminal, file, search, skills, web
Skills: plan
Workdir: /home/zeroclaw/projects/primal-process
Created: 2026-08-03T20:17:27.596324+02:00
Next run: 2026-09-03T10:00:00+02:00
Last run: 2026-08-27T10:24:26.568192+02:00
Last status: ok

======================================================================
PROMPT:
======================================================================

Du bist der Research-Agent (Explorations-Modus) für Project Primal Process (~/projects/primal-process/). CONSTITUTION.md ist unantastbar. Prüfe jede Änderung dagegen.

Dein Auftrag ist freie Suche, **nicht** an eine bestehende Metrik gebunden. Die Constitution begrüßt ausdrücklich neue Mechaniken, die das Entdecken vertiefen statt abzukürzen.

**Feld (weit, nicht abschließend):**
Zeit und Jahreszeiten, Wetter, Verletzung und Heilung, Werkzeugverschleiß, Wissen und Erinnern, Terrain und Ortsbindung, Ressourcenerschöpfung, Gefahren, Handel, Basisbau, Feuer und Wärme. Nichts davon verbietet die Constitution.

**Ablauf:**
1. Lies CONSTITUTION.md, die neueste Scorecard (`scorecard/` + `SCORECARD.md`) und die Play-Reports (`play/`) für Kontext — NICHT als Metrik-Zwang, sondern als Orientierung.
2. Suche eine Mechanik, die das Spiel als **System** vertieft — auch und gerade eine, die keine der bestehenden Metriken bewegt.
3. Schreibe GENAU EINEN Spec nach `specs/SPEC-NNN-<slug>.md` mit dem Format:
   **Problem** (welche Schwäche des Systems, welcher Befund) · **Mechanik** (aus welchem Spiel, wie funktioniert sie) · **Adaption** (konkret für PPP, mit Datei-/Modulbezug) · **Akzeptanzkriterien** · **erwartete Metrik-Wirkung** (welche bestehende Metrik sich wie bewegen würde — wenn keine, explizit sagen).
4. **Jeder Spec braucht einen Metrik-Vorschlag**: welche neue Messung würde zeigen, ob die Mechanik tatsächlich wirkt. Schreibe diesen als eigene Datei `metrics/proposed/<name>.md`: Definition, was sie erfasst, Berechnungsskizze, Richtung oder Zielband, warum sie nicht trivial zu heben ist. Ohne diese Metrik ist der Spec unvollständig.
5. Ergänze den neuen Spec als offenen Task in PLAN.md (Sektion Tasks).
6. JOURNAL.md-Eintrag.

**Commit:**
```
cd ~/projects/primal-process && git add -A && git commit -m "research: explore spec <NNN> <slug> + metric-proposal (cron)" && git push
```
Falls nichts zu committen: überspringen, kein Fehler.
