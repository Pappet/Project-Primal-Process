# Entscheidungsliste für Peter — freigabepflichtige Punkte im PPP

> Stand: 2026-08-14. Diese Datei ist deine Lese-/Entscheidungshilfe.
> Haken → schreibe deine Entscheidung als `[x]`/`[ ]` mit Datum in den Punkt.
> **Peter hat am 22.08. geantwortet** — siehe `DECISIONS_Response_2026_08_21.md`. Die freigegebenen Punkte unten sind abgehakt; offene Punkte (wenn sie noch offen sind) sind markiert.

---

## ✔️ REC-001 — Reachability-Zähler kalibrieren — **FREIGEGEBEN am 14.08., angewendet**

`_pair_slots` löst Tag-Familien jetzt auf. `discovery_gap` 0.375 → ehrlich **0.625** (über Band 0.6),
`blueprint_reachability` 0.75 → **1.0**. Kein Spielverhalten geändert, nur ehrliche Zählweise.
Tests grün (192). Damit ist SPEC-003 wieder verifizierbar — vorerst bewusst **suspendiert** lassen,
weil der Gap jetzt über dem Band liegt und jede neue Discovery-Mechanik ihn Richtung Überführung drücken könnte.

---

## ⏳ SKILL-SPREAD — Neuinterpretation (fallender Wert 0.315 → 0.216)

**Befund (10.08.):** Kein Tiefen-Regress. Die Einsteiger-Decke wurde gehoben (mehr Werkzeugpfade,
erster Craft früher) → optimale vs. zufällige Überlebensspanne schrumpft. Die optimale Decke ist
ökonomie-gebunden und stabil; nur die zufällige ist gestiegen. Klar: Das Spiel gibt dem Können
weniger relativen Vorsprung, weil es den Zufallsspieler besser trägt.

**Deine Wahl:**
- [x] **A (umdeuten):** Formel behalten; Metrik neu interpretieren (fallender Wert = Kindheit der
      Einstiege, kein Tiefenverlust). Richtungs-/Beschreibungslabel in SCORECARD anpassen. — **GEWAEHLT von Peter, 22.08.**
- [ ] **B (umformen):** Statt relativer Spanne eine absolute/metrikmisch andere Definition vorschlagen — aufwendiger.
- [ ] **C (belassen + erklären):** Wert steht weiter, als "klärungsbedürftig" im Journal.

---

## ⏳ KONSOLIDIERTE METRIK-ÄNDERUNGEN (drei Punkte, gesammelt 11.08.)

Drei separate Metrik-Versionierungen (Umdefinitionen) — jedes ist ein eigener Freigabe-Entscheid.
Unabhängig voneinander möglich.

### 2a) `craft_variety` soll auch Prozesse zählen
- **Heute:** zählt nur `execute_experiment`-Crafts, nie `execute_process`. Das Prozess-System bleibt unsichtbar.
- [x] **Freigegeben von Peter, 22.08.** → craft_variety v2 (distinkte `blueprint_id`s UND `process_id`s).

### 2b) `content_reachable` ist blind gegen dangling Nodes
- **Heute:** zählt nur `TEMPLATE_DB`-Keys. Wenn eine Location-Node ein Item droppt, das kein Template hat, merkt die Metrik nichts. (B06/B07-Klasse.)
- [x] **Gewaehlt von Peter, 22.08.** → content_reachable v2 (Node-Referenzen pruefen, `⚠ Content entfernt`-Logik bleibt).

### 2c) skill_spread-Änderung (siehe oben, Punkt SKILL-SPREAD)
- Verknüpft mit der Neuinterpretation; hier nur zur Vollständigkeit gelistet.

---

## ⏳ SPEC-006 — Werkzeug als Zutat (zweite Entdeckungsschicht) — **metrik-seitig BLOCKIERT**

Tier-2-Blueprints mit `tool_tag`-Slot (`CUTTING`/`CHOPPING`) würden `blueprint_reachability`
regredieren, weil `metric_reachability` im Fresh-Gather-Lauf **nie Werkzeuge baut**. Kompensation
= "tool-aware reachability" (Zähler modelliert Werkzeug-Bau als Vorschritt) → `_pair_slots`-Erweiterung
= Constitution-Core. **Reicht über REC-001 hinaus.**

**Optionen (JOURNAL 11.08.):**
- [x] **A:** tool-aware reachability freigeben (Zähler baut Werkzeuge als Vorschritt) → SPEC-006 (REC-002). — **GEWAEHLT von Peter, 22.08.**
- [ ] **B:** SPEC-006 aufschieben.
- [ ] **C:** SPEC-006 ohne tool-aware Zähler umsetzen. **Nicht empfohlen.**

---

## ✔️ FORAGE_PRESSURE — v2 freigegeben (22.08.), Band wird NICHT geschoben
- Erstwert 0.707, Band 0.1–0.5 → **über Band**, aber definitionsbedingt (`stock < max_stock` zählt jede frisch geerntete Stelle).
- **Peter 22.08.:** Band bleibt. v2 misst **gefühlte** Knappheit (z.B. Anteil verweigerter/geminderter Versuche durch Erschöpfung). Schwelle schlägt Dev/Direktor vor. Probezeit 14 Tage, beobachtend.

---

## ✔️ WARMTH_STABILITY / RECOVERY_STABILITY — beobachtend bestaetigt (Peter, 22.08.)
- warmth: Probezeit bis 27.08., danach Beobachtungsgroesse; p25=p75-Flachheit bekannt.
- recovery: Probe bis 03.09., dito. Keins wird Plan-Ziel vor Probe-Ende.

- Aus SPEC-007 (Feuer/Wärme). Erstwert 0.460, Band 0.4–0.9 → **im Band**. Rein beobachtend.

---

## Notizen / wie entscheiden

- **Nicht dringend, kein Zeitdruck:** Es wartet nichts, das das System *anhält* — der Direktor läuft
  weiter, Dev versorgt sich, neue Metriken sind in Probezeit. Diese Liste ist für Qualitäts-Entscheide,
  nicht zum Freigeben eines Stillstands.
- Reihenfolge meiner Empfehlung: **1) REC-001 ✅**, **2) skill_spread A**, **3) 2a+2b (craft_variety,
  content_reachable)** als einfache Ehrlichmacher, **4) SPEC-006** erst, wenn Discovery-Gap stabil.
- Jede hier getroffene Entscheidung gehört ins JOURNAL (mit Datum + Begründung), damit der Direktor
  nicht dagegensteuert.
