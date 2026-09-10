# SPEC-015 — Rast: Zeit als investierbare Ressource (der Nacht-Bogen bekommt ein Verb)

> **STATUS: erledigt (Dev 10.09.) — `rest()`-Verb in engine/core.py
> (`_advance_time(REST_TICKS=4, effort 0.4)`), Menü `[r]asten`; compute_all 12×
> byte-identisch gegen 2026-09-09 (Tages-Probe, Go); 342 Tests grün (+22
> test_rest.py); Delta-Tabelle JOURNAL 10.09.; Play-Gegenprobe (rest_adoption,
> explorativ) → Play-Job.**

STATUS: offen (Research-Exploration, 2026-09-10) · Probe-Verifiziert (read-only /tmp, Repo unberührt)

## Problem

**System-Schwäche: Die Welt tickt — aber der Spieler kann die Ticken nicht gewähren.**
Es existiert kein Verb, das Zeit verstreichen lässt, ohne Arbeit zu leisten. Die CLI kennt
gather/experiment/process/feed/knowledge/inventory/travel/wärmen (`main.py:26`) — jede
dieser Aktionen kostet vollen Effort und zieht RNG-Draws; "einfach eine Weile da sitzen"
ist nicht ausdrückbar. Zeit ist aber die zentrale Ressource des Spiels: Alles, was
regeneriert oder vergeht, hängt an `_advance_time` — Node-Vorräte (SPEC-004), Feuer-
Brennstoff (SPEC-007), Körpertemperatur, Wunden (SPEC-009), Wetter-Lose, Tag/Nacht.

Probe-Verifizierte Befunde (read-only, `/tmp`, Standard-Seeds, Repo unberührt):

1. **Die Heil-Kette (SPEC-009) endet für echte Spieler im Nichts.** Heilung braucht
   `treated + _resting_warm()` (`engine/core.py:804-811`) — aber es gibt kein Verb
   "rasten". Ein naiver Bot über 500 Ticks (10 Seeds): **0/10 behandelt jemals**, also
   heilt nie. Ein guided-artiger Bot heilt "nebenbei" (severity 1.0 → verheilt nach
   **19 gathers am Feuer**) — die Ruhe-Bedingung wird als Zufalls-Nebeneffekt des
   Weitersammelns erfüllt, nie als Entscheidung. `recovery_stability` (0.375, p25=p75
   flach) liest genau diese deterministische Nebenbei-Policy, kein Spielerwissen.
2. **Der Nacht-Bogen ist unbeantwortbar.** ~41% aller Ticks sind Nacht (413/1008,
   bt-Mod −10°C). Ein Tag Sammeln am Waldrand (84 Ticks, CLEAR) wirft den Körper von
   37.0 auf **19.99°C** (UNTERKÜHLUNG-Drain). Die dokumentierte Ausweg-Klasse
   "Shelter suchen" (BACKLOG 13.08.) existiert — aber "am Feuer bis zum Morgen
   ausharren" kann niemand, weil es das Verb dafür nicht gibt. Kälte bleibt damit der
   "Wartungsloop ohne Entdeckungsziel" (Play 14.08.) — man kann sie nicht *überstehen*,
   nur *durcharbeiten*.
3. **Die Energie-Decke kappt jedes Langspiel.** Optimal-Spiel stirbt bei ~240 Ticks an
   Ökonomie (BACKLOG 10.08.: "Energie-Balance (passive/Schlaf-Regen) wäre hier Hebel").
   Heute muss der Spieler für JEDE verstrichene Zeiteinheit 10 Energie (gather-Effort
   2.0) plus Werkzeug-Verschleiß plus Verletzungsrisiko (Schnitt/Zerrung pro
   Erfolgs-Tick) bezahlen — auch wenn er sie nur *verbringen* will.
4. **Stream-Anatomie bestätigt die Lücke:** 60 gathers ziehen 60 Draw-Cycles (Node-
   chance-Würfe), 60× `_advance_time(4)` ziehen nur die ~20 %-12-Wetter-Crossings. Es
   gibt im Verb-Inventar keine Möglichkeit, Zeit zu konsumieren, ohne zugleich
   Ressourcen-Sequenzen zu verschieben — Rast als Verb ist der einzige saubere
   Zeit-Kauf.

**Warum das das System vertieft (Constitution-Feld "Zeit und Jahreszeiten"):** Zeit wird
von einer Nebenwirkung jeder Aktion zu einer *investierbaren* Ressource mit eigenem
Preis (Hunger-Ticks, Feuer-Brennstoff, Wetter-Gefahr während der Rast). Daraus wachsen
echte Entscheidungen: ausharren vs. weiterarbeiten, die Heil-Kette als bewusster
Spielerpfad, Nacht als überstehbares Ereignis statt unaufhaltsamer Kältetod, Node-Regen
als Planungsobjekt. Kein Content-Ballon: kein Item, kein Blueprint, kein Prozess —
Rast verdrahtet bestehende Systeme (Feuer, Heilung, Regen, Nacht) mit einem Verb.

## Mechanik

Aus **Don't Starve** (Sleep/Ruhe als Zeitsprung: der Spieler zahlt Hunger und
Verwundbarkeit für verstrichene Zeit — man "kauft" den Morgen) und **The Long Dark**
(Rest als Risiko-Waage: Schlaf regeneriert, aber das Feuer brennt ab und der Sturm
kümmert sich nicht darum). **Project Zomboid** liefert die zweite Achse: Heilung ist an
Zeit gebunden, die man bewusst opfern muss (" Ruhe ≠ Stillstand"). Gemeinsamer Kern:
**Zeit ist eine Ressource, die man investieren oder verlieren kann — aber nie gratis
bekommt.**

Adaptierte Kernidee: Ein `rest`-Verb (CLI: `[r]asten`) lässt 4 Ticks verstreichen mit
*reduziertem* Effort (0.4 statt gather-2.0): Hunger-Ticks laufen weiter (konstante
Basis), Feuer-Brennstoff verbrennt weiter, Wetter würfelt weiter — aber die Tätigkeit
selbst kostet kaum Kraft, keine Draws, kein Werkzeug-Verschleiß, kein Verletzungsrisiko.
Rast ist nur bei "gastlicher Umgebung" sinnvoll (Feuer oder geschützter Ort) — das ist
genau die bestehende `_resting_warm()`-Bedingung, die bislang nur für die Heilung
existiert und nun zum Spiel-Verb aufgewertet wird.

## Adaption (konkret für PPP)

Dateien: `engine/core.py` (Verb + Konstanten), `main.py` (Menü-Zeile [r]), `tests/test_engine.py`.
**Kein Data-Touch** (kein items/blueprints/processes/locations — die Wächter
`blueprint_reachability`/`content_reachable` sind strukturell unberührt), **kein
Metrik-Core-Touch** (`scorecard.py` unangetastet).

1. **Konstanten (`engine/core.py`, Konstantenblock nach STOKE_FUEL):**
   ```python
   # SPEC-015: Rast — Zeit als investierbare Ressource. Detail-Balance beim Dev.
   REST_TICKS = 4            # ein Rast-Zyklus (≈ 40 In-Game-Minuten)
   REST_EFFORT = 0.4         # reduzierter Hunger-Drain (vs. gather 2.0)
   REST_HEAL_BONUS = 1.0     # Reserve: Rast am Feuer könnte Heilrate über INJ_HEAL_RATE heben
   ```
   `REST_HEAL_BONUS` ist bewusst Reserve (Dev-Balance), nicht Kern — der Kern ist der
   Zeitsprung mit reduziertem Effort; die Heilung funktioniert HEUTE über
   `_resting_warm()` + ticks und braucht keinen Bonus, nur die *Möglichkeit*, Zeit
   zu verbringen.

2. **Verb (`engine/core.py`):**
   ```python
   def rest(self) -> Dict[str, Any]:
       """Verbringt REST_TICKS Ticks mit reduziertem Effort — Zeit kaufen
       (Heilung abwarten, Nacht überstehen, Node-Regen geben). Kostet
       Hunger-Ticks, Feuer-Brennstoff und Wetter-Gefahr wie jede Zeit."""
       msg = self._advance_time(REST_TICKS, effort_multiplier=REST_EFFORT)
       return {"success": True, "message": "Du rastest eine Weile."
               + (f" {msg}" if msg else ""), "reason": "SUCCESS"}
   ```
   Das ist der gesamte Mechanik-Kern: Rast ruft `_advance_time` mit niedrigem Effort.
   Alle Systeme laufen *durch* den bestehenden Tick-Pfad — Ressourcen-Regen, Feuer-
   Brennstoff, Thermodynamik, SPEC-014-Warnungen (Kälte/Feuer-schwach feuern auch
   während der Rast, ehrlich), Verletzungs-Heilung, Wetter. Kein paralleler
   Simulation-Pfad, keine Sonderlogik, keine neuen RNG-Würfe.

3. **UI (`main.py`):** Menü-Zeile um `[r]asten` ergänzen, Handler ruft `game.rest()`
   und druckt die Message (musterkonform zu `[w]ärmen`).

4. **Bewusst NICHT (Design-Abgrenzung):**
   - **Kein Sleep-Skip bis Morgen** (Don't-Starve-Zeitsprung über 8h): würde den
     Nacht-Bogen als Frage auslöschen statt als Entscheidung — Rast ist ein
     *kurzer* Zeitsprung, den man wiederholen muss; jede Wiederholung kostet
     Brennstoff und Hunger. Die Nacht bleibt ein Ereignis, das man *arbeitet*.
   - **Kein Energie-Regen** (BACKLOG 10.08.-Idee "Schlaf-Regeneration"): ein
     zweiter Ressourcen-Kreislauf ist ein eigenes Spec-Thema; hier kauft man nur
     *Zeit* zum bestehenden Preis, nur ohne Arbeits-Zusatzkosten. Energie bleibt
     eine Einbahn (drain) — das ehrliche Lesen der Energie-Decke bleibt bestehen.
   - **Keine Heilung als Rast-Effekt künstlich verdrahten:** Heilung läuft über
     die existierende Bedingung (`treated + _resting_warm()`), Rast macht sie nur
     *anwendbar*. Der Spieler muss trotzdem behandeln können (treat_cut/
     treat_strain entdecken) — Rast ist der letzte fehlende Baustein, kein Auto-Heal.
   - **Kein Beruf "Wachen":** die Gefahr während der Rast ist die bestehende
     (Wetter, Kälte, Brennstoff-Limit) — keine neuen Feinde, kein Kampf (Nicht-Ziel).

## Akzeptanzkriterien

1. **Rast existiert als Verb:** `[r]asten` in `main.py`, `game.rest()` in der Engine;
   ein Rast-Zyklus verstreicht REST_TICKS mit REST_EFFORT — verifizierbar über
   Energie-Delta (80 Ticks Rast = 160 Drain statt gather-800) und Tick-Zähler.
2. **Alle Systeme laufen durch den Tick-Pfad:** während der Rast verbrennt Feuer-
   Brennstoff (FIRE_OUT möglich, ehrliche Meldung), würfelt Wetter (%12-Crossings),
   feuern SPEC-014-Warnungen (Kälte/Feuer-schwach — Rast-Zeit ist ehrliche Zeit,
   keine Hint-freie Blase), heilen behandelte Wunden bei `_resting_warm()`.
   Kontroll-Test: behandelte 1.0-Schnittwunde am Feuer heilt über Rast-Zyklen
   (Probe: 19-20 Ticks bis verheilt), ohne Feuer nie.
3. **Rast ist kein Gratis-Schlaf:** über Nacht-Rast ohne Brennstoff-Nachlegen friert
   der Spieler (bt fällt, UNTERKÜHLUNG-Drain) — Rast verschiebt das Kälte-Problem
   nicht, es macht es planbar (Feuer vor der Nacht sichern = Entscheidung).
4. **Stream-Disziplin:** Rast führt KEINE neuen RNG-Würfe ein (nur die bestehenden
   %-12-Wetter-Crossings von `_advance_time`). Go/No-Go-Probe auf Tages-HEAD:
   `compute_all()` **byte-identisch** gegen `scorecard/2026-09-09.json` (alle 12
   Werte) — Scorecard-Bots rufen `rest()` nie (kein Policy-Touch), die Wettkreis-
   Sequenzen verschieben sich nicht. Delta-Tabelle trotzdem Pflicht im JOURNAL.
   Falls die Tages-Probe wider Erwarten abweicht: Tages-Probe gilt, kein Spec-Ship
   in dieser Form (SPEC-013-Präzedenz) — Negativ-Protokoll im JOURNAL.
5. **Wächter unberührt (strukturell, trotzdem gemessen):** `blueprint_reachability`
   1.0 (11/11), `content_reachable` 1.0 (18/18), `feedback_quality` 1.0 — kein
   Data-Touch, `rest` ist kein Experiment-Pfad, `EMITTABLE_REASONS` unangetastet.
6. **pytest grün** inkl. neuer Tests: rest-Ticks/Effort, Heil-Kette über Rast
   (am Feuer ja, ohne Feuer nein), FIRE_OUT während Rast, Nacht-Rast-Kälte-Kontrolle,
   keine-Draws-Assertion (random.getstate() vor/nach rest() unverändert außer
   %-12-Crossings), Menü-Regression ([r] erscheint, Parser bricht nicht).
7. **CLI bleibt Textinterface, kein Rezept-Leak:** Rast nennt keine Items, Prozesse
   oder Rezepte; die Meldung ist generisch ("Du rastest eine Weile."), Weltzustands-
   Meldungen (UNTERKÜHLUNG/FIRE_OUT) bleiben die bestehenden.

## Erwartete Metrik-Wirkung

**Primär: keine Bewegung in den bestehenden 12 Metriken — bewusst.** Das ist die
ehrliche Behauptung (Kriterium 4, byte-identisch): Scorecard-Bots rufen `rest()` nie,
keine Policy liest das neue Verb. Das Spielgefühl-Argument (Heil-Kette anwendbar,
Nacht überstehbar, Zeit investierbar) liegt vollständig außerhalb der Bot-Welt —
deshalb existiert das Metrik-Proposal `rest_adoption` (`metrics/proposed/rest_adoption.md`).

Sekundär-Kandidaten (beobachtend, keine Versprechen):
- `recovery_stability` (0.375, p25=p75 flach): die Metrik liest die deterministische
  Nebenbei-Policy. Wenn Dev später einen Rast-bewussten Runner baut (nur nach Probe-
  zeit/Freigabe), wäre Streuung über Seeds plausibel — im Messfenster bleibt sie
  byte-identisch.
- `session_depth` (52.5): unberührt — Rast erzeugt keine Neuheiten, der Stall-Punkt
  der Bots verschiebt sich nicht. Für echte Spieler verlängert Rast die Überlebens-
  spanne (der eigentliche Zweck), ohne die Discovery-Leere zu füllen — auch das ist
  ehrlich als Nicht-Ziel notiert: Rast ist kein Content, der Erschöpfung verschiebt.

## Constitution-Check

- Tag-basiertes Crafting unangetastet — Rast ist ein Zeit-Verb, kein Crafting-Pfad.
- Kein Rezept, kein Leak: die Meldung ist generisch, `rest` nennt nichts Kombinatorisches.
- CLI bleibt; Spiel startet in unter einer Sekunde (kein neuer Lade-Pfad); stdlib only.
- Keine Metrik entfernt, umdefiniert oder abgeschwächt; `scorecard.py`/`METRICS` unangetastet.
- Nicht-Ziele respektiert: kein Content-Ballon (0 Items, 0 Blueprints, 0 Prozesse),
  kein GUI-Ersatz, kein Kampf.
- Entdecken vertieft statt abgekürzt: Rast macht bestehende, bislang zufällige
  Systeme (Heil-Bedingung, Node-Regen, Nacht) zu planbaren Entscheidungsräumen —
  der Spieler muss immer noch entdecken, *dass* und *wann* Rast hilft.

## Probe-Log (dieser Lauf, read-only)

| Probe | Ergebnis |
|---|---|
| Naiver Bot 500 Ticks, 10 Seeds | 0/10 behandelt jemals → 0/10 Heilung (Kette endet im Nichts) |
| Behandelte Wunde am Feuer, "Nebenbei-Heilung" | verheilt nach 19 gathers (Zufalls-Nebeneffekt, kein Plan) |
| Ohne Feuer, 600 gathers | severity bleibt 1.0, hp −1527 (Bedingung nie erfüllt) |
| Nacht-Anteil | 413/1008 Ticks ≈ 41%, bt 37.0 → 19.99 nach einem Tag (84 Ticks) Waldrand |
| 80 Ticks "Rast" am Feuer (Probe via `_advance_time(80, 0.4)`) | 0.6-Wunde verheilt, Drain 160 statt 800 |
| Draws: 60× gather | 60 Draw-Cycles (chance-Würfe) |
| Draws: 60× `_advance_time(4)` | 20 (nur %-12-Wetter-Crossings) — Rast-Pfad ist draw-arm |
| 100× gather vs 99× gather + 1 Block(5) | draw-Cycles 100 vs 99, Crossings identisch — Block-Verben ändern Crossing-Anzahl nicht, wenn Batching an derselben Phase hängt (Rust-Batching ist Dev-Detailsache, im Spec nicht festgenagelt) |

## Hinweis an Direktor/Dev

Die Mechanik ist absichtlich klein — ein Verb, das `_advance_time` mit niedrigem
Effort ruft. Die Wucht steckt nicht im Code, sondern darin, was dadurch *anwendbar*
wird: SPEC-009s Heil-Kette (die heute nur als Zufalls-Nebeneffekt funktioniert),
die Nacht (die heute unaufhaltsam arbeitet statt überstehbar), SPEC-004s Node-Regen
(die heute als passives Warten nebenbei passiert). Balance-Freiheitsgrade (REST_TICKS,
REST_EFFORT, ggf. REST_HEAL_BONUS) liegen beim Dev, wie in SPEC-007/013-Präzedenz.
Der Spec ist kein Gap-/Band-Hebel und beansprucht keinen: sein Beweis läuft über
`rest_adoption` (Proposal), nicht über Bewegung bestehender Metriken.
