# SPEC-009 — Verletzung & Heilung: persistente Wunden als Gegen-Schleife zur Überlastung

STATUS: erledigt (Dev 20.08.) · angelegt 2026-08-20 · Quelle: Explorations-Modus (free research, nicht an eine bestehende Metrik gebunden)

## Problem

Das Spiel kennt drei Vitalgrößen — `energy`, `hp`, `body_temp` — aber **`hp` wird nur durch Hunger-Drain und Unterkühlung/Hitzschlag** reduziert (`engine/core.py:_advance_time`, Zeilen 180-214). Es gibt **keine einzige Verletzungsquelle** und **keinen einzigen persistenten Wund-Zustand**: nichts, was dem Spieler durch *Handeln* (nicht durch Verstreichenlassen) schadet und durch *Handeln* (nicht nur durch Essen) geheilt werden muss.

Konkret zusammen gehört: `eat()` (core.py:257-276) ist der **einzige** Heilungsweg (`hp += kcal/20`). Kein Item trägt einen Heilungs-Zweck. Die Rohstoffe, die eine Heilungs-Gegenmechanik tragen würden, existieren bereits und **liegen brach**:
- `plant_fiber` (FIBER) — Verband-/Bindematerial,
- `mushroom` (EDIBLE) + `clay_lump` (CLAY) — Umschlag/Paste,
- `fire` (SPEC-007) + die ruhige `hidden_cave` (exposure 0.1) — Rast/Heilung.

**Befund-Muster (analog SPEC-007):** SPEC-007 fand "Kälte-Druck existiert, Feuer-Hebel fehlt". Hier ist es grundlegender: **weder Druck (Verletzung) noch Hebel (Heilung) existiert.** Die Fundamentalschraube (thermische/witterungsbedingte Frist) ist die *einzige* Druckschraube des Spiels. Risiko, das aus *eigenem* Handeln entsteht (am exponierten `mountain_peak` sammeln, mit scharfen Materialien hantieren, überanstrengen) — und die daraus folgende *Entscheidung* (was bereite ich vor, wann raste ich) — fehlt komplett.

Warum das eine System-Schwäche ist: Die Constitution will "Wachstum in Systemen" und "Entdecken vertieft statt abgekürzt". Ein Verletzungs-/Heilungs-Layer gibt dem Spieler eine zweite, **aktive** Überlebensökonomie (Risiko eingehen vs. absichern, Heilmittel entdecken) jenseits von Kalorien und Wärme — mit echten Entscheidungen statt nur Wartungs-Loops. Rein additiv, nichts an bestehenden Metriken angetastet.

## Mechanik

Quelle: **The Long Dark** (Affliction-System — Verletzungen wie Schnittwunden/Verstauchungen sind persistent, **bluten/beeinträchtigen über Zeit** und brauchen gezielte Behandlung: Verband, Ruhe, bestimmte Gegenmittel; unbehandelt ziehen sie Substanz) und **UnReal World / Vintage Story** (Wunden an Körperteilen, Heilung über hergestellte Kräutermittel + Ruhe am warmen Ort; Behandlung ist ein Craft, keine Sofortheilung).

Kern-Idee: Verletzungen sind ein **Zustand**, nicht ein einmaliger HP-Abzug. Eine Wunde:
1. **zieht über Zeit** (Bluten: `hp`-Drain pro Tick), bis sie behandelt ist,
2. **beeinträchtigt** (Verstauchung senkt die Sammel-/Effektivität oder erhöht den Effort),
3. wird durch **Behandlung (Craft) + Ruhe** abgewendet — nicht durch Essen.

## Adaption (konkret für PPP)

Dateien: `engine/components.py`, `engine/core.py`, `data/processes.json`, `data/items.json`, `data/blueprints.json` (falls Gate), `tests/test_engine.py`. **`tools/scorecard.py` unangetastet** (Metrik-Core). Additiv, kein Rezeptbuch.

### 1. Befund: nichts zu "erfinden", nur anzubinden — Wund-Zustand (components.py)

`Player` bekommt einen persistenten Zustand `self.injuries: dict[str, dict]`, z.B.
```python
injuries = {
  "cut":  {"severity": 1.0, "ticks": 0},       # Schnittwunde → blutet über Zeit
  "strain": {"severity": 1.0, "ticks": 0},      # Verstauchung → Effort-Malus
}
```
Jede Wunde trägt `severity` (wie stark) und `ticks` (seit Entstehung). Das macht Verletzung mess- und skalierbar, ohne ein neues Ganzes einzuführen — analog `ResourceNode.stock`/`LocationDef.fire_*` als pro-Instanz-Zustand (kein Cross-Session-Bleed, da `GameEngine` frische Objekte baut).

### 2. Druck: wo Verletzungen entstehen (core.py)

Zwei ehrliche, handlungsgebundene Risiko-Quellen (Frequenz so balanciert, dass es spürbar, aber abwendbar ist — DEV/Direktor kalibriert die Wahrscheinlichkeiten, der Spec definiert das System):

- **`gather()` (core.py:217-255):** Sammeln am exponierten `mountain_peak` (exposure 1.0) oder an Verwundbar-Risiko-Nodes hat eine kleine Chance auf `strain` (Sturz/Überanstrengung). Sammeln/Bearbeiten mit scharfen Materialien (`SHARP`-Haltung, z.B. FLINT) hat eine kleine Chance auf `cut` (Schnitt). Der Spieler *spielt* das Risiko — die Frist entsteht aus eigener Orts-/Materialwahl, nicht aus einem globalen Timer.
- **`execute_experiment`/knapping-artige Prozesse (core.py):** ein harter Fehlversuch mit scharfen Bauteilen oder eine gescheiterte Verarbeitung kann minimal `cut` verursachen — wer nachlässig mit scharfen Dingen hantiert, verletzt sich. (Optional, DEV-Entscheid; Primärquelle bleibt das Sammeln.)

### 3. Hebel: Behandlung = Handeln, Heilung = Handeln + Ruhe (core.py + processes.json)

Neue, **durch Experimentieren entdeckbare** Prozesse (kein Rezeptbuch) — die Rohstoffe existieren bereits:
- **`make_bandage`** ("Verband (Fasern)") — `plant_fiber` → Verband; stoppt das **Bluten** (`cut` schadet nicht weiter). 
- **`make_poultice`** ("Umschlag (Ton+Pilz)") — `mushroom` + `clay_lump` → Umschlag; lindert `strain` (Effort-Malus weg) und beschleunigt die Regeneration. Optional mit `min_survival_req`-Gate (SPEC-008-Pfad, discovery-produces-discovery).
- **Heilung über Ruhe:** `_advance_time` heilt Restwunden, wenn die Wunde **behandelt** wurde (Verband/Umschlag angelegt) UND der Spieler an einem warmen/Ruhe-Ort rastet (`fire_active` an Location ODER `hidden_cave` exposure 0.1). Unbehandelt heilen Wunden nicht oder heilen deutlich langsamer und bluten weiter → der Spieler *muss* die Behandlung entdecken und die Ruhe organisieren.

Neue Templates in `data/items.json`: `bandage`, `poultice` (+ optional 1-2 Take-Prozesse). **`content_reachable` halten** (s. Akzeptanz): neue Items als Prozess-Outputs, nicht als Gather-Nodes; Prozess-Inputs vollständig erreichbar (plant_fiber/mushroom/clay_lump sind alle sammelbar) → Nenner steigt nur, wenn die neuen Templates auch WIRKLICH erreichbar bleiben.

### 4. Feedback

Neue Reasons/Labels analog SPEC-007: `INJURED` ("Du bist verletzt — Axis"), `BLEEDING`, `TREATED`/`HEALED` (wenn Verband wirkt / Rast geheilt). Generisch, **kein Rezept-Leak** — der Text sagt, dass eine Behandlung fehlt und was sie *im Prinzip* sein könnte, verrät aber nicht die Kombination. `TAG_LABELS` in core.py:16-37 konsistent ergänzen (Konsistenz-Wächter in Tests).

### 5. Constitution-Check

Kein vorgegebenes Rezept (Prozesse werden durch Kombinatorik entdeckt; Verletzung ist ein Spieler-Zustand, kein Hinweistext), Experimentiergedächtnis erlaubt, CLI-Text bleibt, stdlib only, **keine bestehende Metrik entfernt/umdefiniert/abgeschwächt** (additiv), das Spiel wird **vertieft** (neue aktive Überlebensökonomie), kein Metrik-Core (`tools/scorecard.py`) berührt.

## Akzeptanzkriterien

- Eine Wunde (`cut` oder `strain`) ist ein **persistenter Zustand**: unbehandelt zieht sie über Zeit (`cut` → HP-Drain/Tick; `strain` → Effort-Malus beim Sammeln), nicht nur ein einmaliger Abzug.
- Verletzungsquelle ist an **Handeln** gebunden (Sammeln am exponierten `mountain_peak` / mit scharfen Materialien); nicht an einen globalen Timer. Frequenz so, dass es auf den meisten Seeds spürbar, aber **durch Vorbereitung abwendbar** ist.
- Behandlung ist ein **entdeckbarer Prozess** (`make_bandage`/`make_poultice`), kein vorgegebenes Rezept; die Items sind ohne Rezept-Leak in der Welt auffindbar erreichbar.
- **Behandlung + Ruhe wirkt:** `cut`/`strain` verschwinden (bzw. fallen unter eine Schwelle) nur, wenn behandelt UND an warmem/Ruhe-Ort gerastet. Unbehandelt bluten/beeinträchtigen sie weiter.
- `content_reachable` bleibt **1.0** (neue Templates als Prozess-Outputs mit erreichbaren Inputs; Reachability durch Tests gesichert), `blueprint_reachability` unverändert 1.0.
- `python -m pytest` bleibt grün (neue Tests: Wunde entsteht am exponierten Ort; `cut` blutet über Zeit unbehandelt; `bandage` stoppt Bluten; `poultice` + Ruhe heilt `strain`; unbehandelt heilt nicht; kein Rezept-Leak im Text; content_reachable 1.0).
- Neue Probe-Metrik (s. `metrics/proposed/recovery_stability.md`) ist in `tools/scorecard.py` aufgenommen und liefert einen deterministischen Erstwert; zwei Wochen Probezeit.

## Erwartete Metrik-Wirkung (bestehende Metriken)

Keine bestehende Metrik ist Ziel dieses Modus; die Wirkung ist sekundär/beobachtend und **primär in der neuen Probe-Metrik** zu lesen:
- **`session_depth`**: leicht stützend aber **nicht garantiert** — neue Prozesse (`make_bandage`/`make_poultice`) sind zusätzliche Entdeckungsziele, aber der naive `session_depth`-Bot, der früher an Hunger/Kälte starb, wird durch Verletzungen *eher früher* scheitern. Netto unklar; NICHT als Session-Tiefen-Hebel designen.
- **`discovery_gap`**: leicht steigend möglich (neue, über Prozesse entdeckbare Ziele ohne Gate = mehr erreichbar aber unentdeckt). Muss im Band 0.2-0.6 bleiben; DEV prüft mit ehrlichem Zähler. Falls über Band → Gate/Score abstimmen statt Content streichen.
- **`forage_pressure` / `warmth_stability`**: unverändert in der Definition; `warmth_stability` kann durch den Ruhe-Bonus (am Feuer heilen) leicht profitieren, aber additiv gelesen.
- **`feedback_quality`**: Risiko — neue generische Wund-Meldungen (absichtlich vag) könnten wie `NEAR_MISS` als "uninformativ" zählen (bekannte `_expected_fragment`-Blindstelle). **DEV-Maßgabe:** `_expected_fragment`-Mapping für `INJURED`/`TREATED`/`HEALED` entweder ergänzen (Peter, Metrik-Kern) oder die Meldungen so fassen, dass ein ehrliches Fragment matcht — nicht still die Metrik schwächen (Constitution).
- **neu (Primär-Beweis):** `recovery_stability` — siehe `metrics/proposed/recovery_stability.md`.

## Verzichtet
- Keine bestehende Metrik angefasst. SPEC-006 bleibt blockiert (Peters Freigabe) und wird von diesem Spec nicht umgangen.
- Kein Kampf/Feind-System — Verletzung entsteht aus *Umwelt und eigenem Handeln*, nicht aus Kämpfen (Constitution: Kampf als Randphänomen).
- Kein Kommando/keine Datei im Metrik-Core geändert.