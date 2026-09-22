# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.
> Stand: 2026-09-20, Lesung = Scorecard 18.09. (+ SPEC-016-Landung 19.09., metrik-neutral verifiziert).

## Aktueller Zustand

Die Nacht ist überlebbar: T1 (Komfort-Cutoff) und T2 (stick→WOOD) sind Play-verifiziert — Rest-Loop 0/20 Tode, Nacht-Fenster 20/20 überlebt, verweigerte Stokes 194→0. Die Scorecard (18.09., 13 Metriken) ist stabil: alle 12 Alt-Metriken byte-identisch, Wächter 1.0/1.0/1.0, `discovery_gap` 0.545 in der Bandmitte, `rest_adoption` Erstlesung 1.0 (flach, Probe bis 24.09.). SPEC-016 (Glut) ist am 19.09. sauber gelandet (`compute_all` 13× byte-identisch) — seine Wirkung im Spielverlauf ist aber noch ungelesen, und die Leere nach dem Tier-1-Tree bleibt die offene Stelle (guided last_new median 26, `session_depth` 52.5).

## Was als nächstes besser werden muss

1. **Die Discovery-Tiefe über den Tier-1-Tree hinaus heben.** Metrik: `session_depth` (52.5 — guided last_new median ~26; Struktur unverändert: nach 11 Blueprints + 6 Prozessen passiert nichts Neues). Träger ist die Glut (SPEC-016) als erste Ortsbindungs-Achse im Spielverlauf — mit `discovery_gap` im Band (0.2–0.6) als Nebenbedingung, nicht als Opfer.

2. **Glut in die Messung nehmen — die erste Welt-Eigenschaft statt Bot-Policy.** `fire_home_loyalty` ist heute angenommen (Triage im JOURNAL 20.09.); Aufnahme durch Dev, danach 14 Tage Probezeit. Metrik: `fire_home_loyalty` (Band 0.3–0.8, keine Richtung) — bis Probe-Ende beobachtend, kein Plan-Ziel.

3. **Die Wächter halten durch jede weitere Änderung.** Metriken: `blueprint_reachability` 1.0 (11/11), `content_reachable` 1.0 (18/18), `feedback_quality` 1.0; jede Engine-/Data-Änderung mit vollständiger `compute_all()`-Delta-Tabelle, Stream-Shift dokumentiert, nicht kompensiert (31.08.-Präzedenz).

## Tasks

> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.

- [x] **T1 — fire_home_loyalty in METRICS aufnehmen** (angenommen, Direktor 20.09.). ✅ 21.09. Dev
      **Akzeptanz:** additiver METRICS-Eintrag am Ende der Liste (Dict-Order = Präzedenz, wie `rest_adoption`), v1, Band [0.3, 0.8], keine Richtung, `probation_until: 2026-10-04`; Runner-Policy folgt dem Proposal (Bot mit unvollkommener Feuer-Policy — stoke nur beim FIRE_DYING-Hinweis, keine Vorrats-Planung; FIRE_OUTs im natürlichen Verlauf; Detail-Zähler fire_outs/revive_same/relight_full als Diagnose-Block). Pflicht-Delta-Tabelle `compute_all()` vor/nach: alle 13 Alt-Metriken byte-identisch. pytest grün (+Runner-Tests). Constitution: Ergänzen erlaubt, nichts entfernt/umdefiniert. Details: `metrics/proposed/fire_home_loyalty.md`.
      **Priorität: 1** — der Probezeit-Zähler sollte früh laufen.

- [x] **T2 — Play-Gegenprobe Glut: FIRE_OUT → Revive am selben Ort im natürlichen Verlauf.** ✅ 21.09. Play (74/74 Revive) FIRE_OUT ist real (Play-Spirale 28.08., Feuer-Ausfälle 09.09.). **Akzeptanz:** Lesung in `play/` — Quote der FIRE_OUTs, wie oft Glut-Rest beim nächsten Feuer-Besuch noch ≥ `EMBER_REVIVE_MIN`, Revive-Kosten (1× WOOD) vs. voller start_fire-Kette; 20-Sweep; read-only Probes, kein Patch. Erwartung: Wächter unberührt (Bots rasten/glut nie — sonst Delta-Tabelle + Ursachen-Lesung).

- [x] **T3 — Menü-Pfad-Lesung post T1/T2/SPEC-014/SPEC-016 (B10-Menürest).** ✅ 21.09. Play (20/20 Tode, B10-Wurzel neu gelesen) Play 18.09. ruft `stoke_fire()` direkt — der Menü-Spieler (`[w]ärmen`-Label, kein Prozess, keine Hinweis-Kategorie) ist von allen Fixes unberührt ungelesen. **Akzeptanz:** Profil C (Menü-naiv, 200 Aktionen, 20 Seeds) re-lesen; Ziel explorativ: Kälte-Tode deutlich unter 20/20 (Vor-Befund 14.09.: 20/20); `last_new` + Erschöpfung im Menü-Profil lesen. Falls 20/20 Tode halten: B10-Wurzel neu lesen — dann ist die Menü-Sichtbarkeit von stoke das eigene Problem, nicht die Ökonomie.

- [x] **T4 — `play/naive_menu.py` als Repo-Datei** (Play-Messwerkzeug, kein Scorecard-Eingriff). ✅ 21.09. Play Zum vierten Mal war das Profil /tmp-Wegwerfcode (07.09., 09.09., 14.09., 18.09.). **Akzeptanz:** Datei committet, deterministisch, reproduziert die letzte Menü-Lesung (20 Seeds), von T3 genutzt; Play-Job-Prompt unangetastet.

- [ ] **T5 — SPEC-017 Subset-Echo implementieren** (`specs/SPEC-017-subset-echo.md`, Research 22.09.). Befund: die Aritäts-Gate-Zeile in `execute_experiment`/`_no_match_reason` macht alle 6 2-Slot-Blueprints stumm, wenn der Spieler 3 Items hält — Probe 22.09.: 521 voll feasible 2-Slot-Teilnahmen in 3-Item-Selektionen über 20 Seeds, 0 Echos. **Akzeptanz:** Teilmengen-bewusster One-Shot-Hint `SUBSET_HINT` (Block 2c), Craft bleibt exakt-arity (kein Auto-Craft), `Player.subset_hints_seen` + 4 Tests; read-only Profil-C-Probe nach Landing: Echo-Zähler > 0, Blueprints entdeckt > 0/20, Kältetode < 20/20; pytest grün, compute_all-Delta-Tabelle geführt, kein scorecard-Touch.

## Verworfen / beobachtend (bewusst keine Tasks)

- **rest_adoption als Plan-Ziel:** gesperrt bis Probe-Ende 24.09. — Band-Lesung (1.0 über Obergrenze 0.85, Kalibrierungs-Ware) beim nächsten Direktor nach 24.09.
- **WARMTH_SEEDS toter Code** (tools/scorecard.py:836): Löschung metrik-neutral, aber scorecard.py-Anfassung liegt außerhalb des Direktor-Mandats (alles, was zur Messung gehört, unantastbar) — bleibt notiert, Peters Freigabe nötig.
- **Tier-2-Anschluss-Andeutung** (cord_spear 0/20): bleibt verworfen — Andeutung an einem Grundpfad, der im natürlichen Verlauf tot ist, ist Reihenfolge-falsch. Erst T3-Lesung, dann neu bewerten.
- **Energie-Regen / Condition-Web / Jahreszeiten** (SPEC-013-Präzedenz): größere Achsen, später; Jahreszeiten-Neuanlauf nur mit Peters Mess-Systems-Freigabe.

---

*Scorecard-Lesung: nächster Play-Job (Mo 21.09.). Plan-Neufassung: nächster Direktor (So 27.09. 18:00) — dann fallen die Probezeit-Entscheide rest_adoption (24.09.) und die erste fire_home_loyalty-Lesung.*
