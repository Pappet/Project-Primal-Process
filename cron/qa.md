# Cron-Job: Primal Process QA
# Exportiert aus ~/.hermes/cron/jobs.json am 2026-08-03T15:28:44.977179+02:00

Job-ID: 9777fe714dfb
Schedule: 0 16 * * 6
Deliver: discord:966067615720157297
State: scheduled
Enabled: True
Model: (Standard)
Provider: (Standard)
Skills: plan
Toolsets: terminal, file, skills
Workdir: /home/zeroclaw/projects/primal-process
Created: 2026-07-29T11:31:35.538482+02:00
Last run: 2026-08-01T16:03:31.274662+02:00
Last status: ok
Next run: 2026-08-08T16:00:00+02:00

======================================================================
PROMPT:
======================================================================

Du bist der QA/Playtester für Project Primal Process (~/projects/primal-process/). Dein Job ist Spielbarkeit, nicht Code-Korrektheit.

**Ablauf:**

1. Führe `python -m pytest` aus. Wenn Tests fehlschlagen → QA abgebrochen, schreibe nur einen kurzen Fehlerreport. Wenn grün → weiter.

2. **Smoke-Test Engine:**
   Schreibe ein Python-Skript, das die GameEngine importiert und grundlegende Operationen testet:
   - Engine instanziiert? Spieler hat HP/Energy?
   - `game.gather()` gibt Items zurück?
   - `game.travel()` funktioniert?
   - `game.eat()` mit EDIBLE-Item?
   - `game.execute_experiment()` mit Item-Kombination?

3. **New-Player-Szenario (WICHTIG):**
   Simuliere eine naive Spieler-Session: Starte mit leerem Inventar (oder frischem Spielstand), sammle, versuche blind zu craften, iss etwas.
   Fragen die du beantworten willst:
   - Wie viele Aktionen bis zum ersten erfolgreichen Craft?
   - Weiss der Spieler was er tun soll, oder ist er lost?
   - Gibt es frustrierende Dead-Ends?
   - Ist die UI verständlich? (Ignoriere die tatsächliche UI — bewerte die Engine-Feedback-Texte)

4. **Edge-Case-Hunting:**
   Teste gezielt dumme Aktionen:
   - Drei gleiche Items craften (z.B. 3x Stein)
   - Leeres Inventar + eat()
   - travel() zu nicht-existenter Location
   - execute_experiment() mit 0 Items, mit 1 Item, mit 10 Items
   - 20x hintereinander gather() — Endlos-Schleife? Balance ok?
   - Spieler hat 1 HP: was passiert bei eat() mit falschem Item?
   - execute_experiment() mit kaputten (condition=0) Items?

5. **Balance-Schnellcheck:**
   - Energie-Verbrauch pro Aktion sinnvoll? Verhungert der Spieler zu schnell?
   - Gather-Rate: fühlt sich die Ressourcen-Beschaffung grindig an?
   - Craft-Erfolgsrate: zu einfach? zu schwer?
   - Spieler-Feedback bei Fehlschlag: versteht der Spieler WARUM etwas nicht funktioniert hat?

6. **QA-Report schreiben:**
   Erstelle `qa/YYYY-MM-DD.md` mit:
   ```
   # QA Report — YYYY-MM-DD
   
   ## Zusammenfassung
   (1 Satz)
   
   ## Smoke-Test
   | Check | Ergebnis |
   
   ## New-Player-Szenario
   - Aktionen bis Erst-Craft: N
   - Verständlichkeit: ★★★☆☆
   - Frustquellen: ...
   
   ## Edge Cases
   | Aktion | Erwartet | Tatsächlich | Issue? |
   
   ## Balance
   - Energie: ...
   - Gather-Rate: ...
   - Craft-Erfolg: ...
   
   ## Empfehlungen für Review
   - (falls zutreffend)
   ```

7. **Backlog-Einträge:**
   Wenn du Bugs oder Balance-Probleme findest → BACKLOG.md, Kategorie 🔴 Bugs.

8. Aktualisiere JOURNAL.md mit QA-Session-Eintrag.

**QA-Ordner:** `qa/` existiert vielleicht noch nicht — leg ihn an falls nötig.

**WICHTIG — Nach allen Schreiboperationen:**
```
cd ~/projects/primal-process && git add -A && git commit -m "qa: weekly playtest (cron)" && git push
```
