# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand

Die Messbasis ist gesund (`blueprint_reachability` 1.0, `content_reachable` 1.0, `feedback_quality` 1.0,
`actions_to_first_craft` 9.5 nach SPEC-010), aber der `discovery_gap` klettert drittlesung in Folge über
Band — 0.6 → 0.65 → **0.70** — weil jedes neue Druck-System (Kälte, Verletzung, jetzt Verschleiß) die
naive Discovery-Rate (0.4 → 0.35 → 0.3) erodiert. SPEC-011 (Werkzeugverschleiß sichtbar, inkl.
`sharpen_tool`) ist gelandet (Nachcommit 30.08. nach Session-Abbruch); die neue `gear_uptime`-Erstlesung
0.994 über Band dokumentiert ehrlich, dass Attrition für den naiven Bot trotz Verdrahtung fast unsichtbar
bleibt (Probe bis 11.09.). Der echte Boredom-Punkt ist unverändert klein (~15–19 gezielte Aktionen);
`session_depth` 54.5 ist v2-Re-Baseline (Probe bis 08.09.), kein Wachstum.

## Was als nächstes besser werden muss

1. **Naive Spieler behalten den Anschluss — discovery_gap zurück ins Band.**
   Metrik: `discovery_gap` (0.70 → zurück ≤ 0.6; Band 0.2–0.6 bleibt, keine Abschwächung).
   Drei Lesungen über Band sind ein Spiel-Signal, kein Zufall: die Druck-Systeme (Kälte SPEC-007,
   Verletzung SPEC-009, Verschleiß SPEC-011) stapeln sich, aber ihre **Beantwortbarkeit** ist für
   Naive unsichtbar — der v2-Hint-Layer hilft nur Akteuren, die Hints verfolgen. Antwort strikt
   spiel-seitig: Constitution erlaubt Entdeckungsjournal, Hinweise, Experimentiergedächtnis —
   Überlebens-Lektionen müssen als Entdeckung erlebbar werden (z. B. Kälte/Hunger/Verletzung
   mit einer richtungsgebenden, generischen Meldung beantworten statt nur zu strafen).
   Kein Tuning an den Metriken, keine Band-Schrauben.

2. **Prozesse als zweite Entdeckungsebene öffnen.**
   Metrik: `craft_variety` (4.5, wieder ≥ 5 und darüber). Naive Spieler führen **null** Prozesse aus
   (Play-Probe 26.08.: 0 Prozesse in Blind-Runs) — die 10 Prozesse sind für Zufalls-Entdeckung
   faktisch unsichtbar, obwohl sie halb der Content-Tiefe sind. Antwort spiel-seitig, Muster
   NEW_COMPONENT-Reveal (SPEC-006) auf Prozesse übertragen: Besitz/Umgebung gibt einen
   einmaligen, generischen Hinweis („hier ließe sich etwas zubereiten/entzünden") — kein Rezept-Leak,
   kein Reason-Code-Eingriff.

3. **Die Wächter halten, während neuer Content kommt.**
   Metriken: `blueprint_reachability` = 1.0, `content_reachable` = 1.0, `feedback_quality` = 1.0.
   Zwei Tasks unten (Munitions-Ökonomie, Prozess-Hints) fassen die Engine an — kein neuer
   dangling Node, kein unreachable Blueprint, kein uninformative Reason. Bei jedem Engine-Eingriff:
   RNG-Strom-Klasse beachten (eigener Strom für neue Würfe), Delta-Tabelle im JOURNAL ist Pflicht.

## Tasks

> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.

- [x] **SPEC-011 — Werkzeugverschleiß sichtbar machen** — **umgesetzt 29.08.**, vom Direktor
      nachcommittet 30.08. (Dev-Lauf crashte vor JOURNAL/Commit; Verifikation + Pflicht-Delta-Tabelle
      im JOURNAL 30.08.). Erstlesung `gear_uptime` 0.994 über Band = dokumentierte Unsichtbarkeit,
      Probe bis 11.09. — beobachtend, kein Tuning.

- [ ] **B08 — INJURED-Feedback-Zweig** (keine Freigabe nötig, kleiner Fix). `core.gather()` ruft
      `_feedback_message("INJURED")`, aber `_feedback_message` hat keinen INJURED-Zweig → Spieler
      liest den Fallback „Das geht so nicht." statt einer Verletzungs-Meldung.
      Akzeptanz: eigener `INJURED`-Zweig (z. B. „Du verletzt dich."), kein generischer Fallback mehr;
      Verletzungswahrscheinlichkeit unangetastet; `feedback_quality` unverändert 1.0 (Experiment-only);
      pytest grün; Delta-Tabelle compute_all() vor/nach im JOURNAL (alle Werte müssen identisch bleiben).

- [ ] **Munitions-Ökonomie: Pebble = Consumable** (BACKLOG 27.08., Research-Befund, promotet).
      Die Jagd wäscht den ganzen Pebble-Stack über den Werkzeug-Wear-Pfad (~0.25/Erfolg,
      durability 0.2) — der komplette Munitionsbestand verschwindet nach ~4 Schüssen still und
      ohne Vorwarnung. Ein Projektil ist Consumable, kein dauerhaftes Werkzeug.
      Fix-Richtung: PROJECTILE-Nutzung verbraucht `quantity--` pro Schuss statt Condition-Wear auf
      den gemergten Stack (oder eigenes Ammo-Tagging — Dev entscheidet, beides ist constitution-konform).
      Akzeptanz: Pebble-Stack verschwindet nicht kollektiv still; pro Schuss genau ein Projektil
      weg; keine stillen NaN/Condition-Artefakte auf Stacks; pytest grün; vollständige
      compute_all()-Delta-Tabelle vor/nach im JOURNAL (RNG-Strom-Klasse!) — verschiebt eine
      Metrik: Lesung dokumentieren, nicht kompensieren; discovery_gap > 0.70 → Direktor-Flag im
      selben Commit. Kein Rezept-Leak.

- [ ] **Ziel-2-Hebel: Prozesse für naive Spieler sichtbar machen** (keine Freigabe nötig, aber
      Mechanik-Design sauber halten). Der NEW_COMPONENT-Reveal (SPEC-006) zeigt Werkzeug-Potenzial
      einmalig beim ersten Werkzeugbau — das analoge Signal für Prozesse fehlt: Besitz + Umgebung
      (z. B. rohes Fleisch + aktives Feuer, Reeds + CUTTING-Werkzeug) erzeugen null Richtungssignal.
      Antwortsspielraum (Dev/Research): ein generischer, einmaliger Umgebungshinweis pro Prozess-Klasse
      (kein Rezept-Leak, kein neuer Reason-Code, `feedback_quality`-Kern unangetastet). Erst Design
      kurz skizzieren (1 Absatz im JOURNAL), dann TDD.
      Akzeptanz: naive Bots führen in Mess-Läufen Prozesse aus, ohne dass Rezepte geleakt werden;
      craft_variety bewegt sich (Ziel: ≥ 5) ohne dass blueprint_reachability/content_reachable sinken;
      keine neue Metrik nötig.

- [ ] **Gap-Wächter zurücksetzen, sobald Ziel 1 liest** (Auflage aus den gelockten Tests ≤ 0.70).
      Nachdem eine spiel-seitige Antwort (B08 + Prozess-Hinweise + ggf. Überlebens-Hinweise) eine
      Play-Scorecard gezeigt hat: die beiden Gap-Wächter-Tests (TestRec001/TestRec002) von ≤ 0.70
      auf die dann aktuelle ehrliche Marke zurücksetzen bzw. verschärfen — keine stille
      Abwärtsanpassung, Auflage-Kommentar in `tests/test_scorecard.py` ablösen.

- [ ] **PLAY-TOOLING: Feuer-Ökonomie statt Rückzug-Trigger** (keine Freigabe nötig; ersetzt den
      toten Trigger-Ansatz). Befund 28.08.: alle 14 Baseline-Tode sind die Feuer-Versorgungsspirale
      am Waldrand (Gipfel-Trip im STORM → Feuer ohne stick-Nachschub → FIRE_OUT → bt-Kollaps);
      der Trigger war 16/20 Tode vs. 14/20 Baseline strikt schlechter. Neuer Ansatz: Versorgung
      VOR dem Trip sichern (Brennstoff-Ökonomie vor der Reise, nicht Reparatur nach dem Kollaps).
      Jeder Fix nur am kalten Ort bzw. im Warmup, gegengetestet über 20-Sweep.
      Akzeptanz: Tode/20 < 14 Baseline ODER dokumentiert nicht landbar (wie 28.08.); 20-Sweep-Pflicht;
      Messwerkzeug, keine Metrik.

- [~] *(beobachtend)* **session_depth** (v2, Probe bis 08.09.) — 54.5, Re-Baseline, kein Ziel vor Probe-Ende.
      Erster Ziel-Check beim Direktor nach Probe-Ende; Play-Lesung (echter Boredom-Punkt ~15–19)
      bleibt die ehrliche Kompass-Nadel.
- [~] *(beobachtend)* **gear_uptime** (Probe bis 11.09.) — 0.994 über Band, Erstlesung dokumentiert
      die Unsichtbarkeit. Bewerten nach Probezeit, nicht tunen.
- [~] *(beobachtend)* **forage_pressure** (Probe bis 11.09.) — 0.0 unter Band, Re-Baseline der
      Neudefinition. Band-Entscheid nach Probezeit, nicht vorher.
- [~] *(beobachtend)* **recovery_stability** (Probe bis 03.09.) — 0.375 im Band, flach. Bewertung
      nach Probe-Ende (nächster Direktor).
- [~] *(beobachtend)* **warmth_stability** — Probe 27.08. beendet, Peters Lesung: Beobachtungsgröße,
      kein Plan-Ziel. 0.46 im Band, flach.
- [x] *(erledigt)* REC-001, SPEC-003, SPEC-005, SPEC-007, SPEC-008, SPEC-009, SPEC-010, SPEC-006-Kern,
      Ehrlichmachungs-Batch, forage_pressure v2, REC-002 (+B09-Korrektur), NEAR_MISS-Volldeckung.

---

*Naechste Scorecard-Kontrolle: naechster Play-Job (Mo 31.08. 09:00). Plan-Neufassung: naechster Direktor (So 06.09.).*
