# Entscheidungsliste für Peter — freigabepflichtige Punkte im PPP

> Stand: 2026-08-14. Diese Datei ist deine Lese-/Entscheidungshilfe.
> Jeder Punkt braucht eine Metrik-bezogene Freigabe (Constitution: `tools/scorecard.py`,
> `METRICS`, Scorecard-Dateien = unantastbar → Änderungen brauchen dich).
> **Frei gegeben (zur Info):** REC-001 wurde von dir am 14.08. freigegeben und angewendet.
> Haken → schreibe deine Entscheidung als `[x]`/`[ ]` mit Datum in den Punkt.

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
- [ ] **A (umdeuten):** Formel behalten; Metrik neu interpretieren (fallender Wert = Kindheit der
      Einstiege, kein Tiefenverlust). Richtungs-/Beschreibungslabel in SCORECARD anpassen. **Empfohlen** —
      minimal, ehrlich, keine Berechnung angefasst.
- [ ] **B (umformen):** Statt relativer Spanne eine absolute/metrikmisch andere Definition vorschlagen —
      aufwendiger, betrifft Metrik-Berechnung, mehr Tests nötig.
- [ ] **C (belassen + erklären):** Wert steht weiter so, als "klärungsbedürftig" im Journal; keine
      Änderung. Erst entscheiden, wenn ein neuer Mechanik-Zyklus das Verhältnis verschiebt.

---

## ⏳ KONSOLIDIERTE METRIK-ÄNDERUNGEN (drei Punkte, gesammelt 11.08.)

Drei separate Metrik-Versionierungen (Umdefinitionen) — jedes ist ein eigener Freigabe-Entscheid.
Unabhängig voneinander möglich.

### 2a) `craft_variety` soll auch Prozesse zählen
- **Heute:** zählt nur `execute_experiment`-Crafts, nie `execute_process`. Das neue Prozess-System
  (Feuer, Wärme, Kochen, Werkzeugbau) bleibt für diese Metrik unsichtbar.
- **Wirkung:** Prozesse werden als "Craft-Typ" mitgezählt → breiteres Bild der Craft-Vielfalt.
- [ ] **Geben?** (Umdefinition → `craft_variety` v2, Alt-Pfad konkurriert nicht mehr.)

### 2b) `content_reachable` ist blind gegen dangling Nodes
- **Heute:** zählt nur `TEMPLATE_DB`-Keys. Wenn eine Location-Node ein Item droppt, das gar kein
  Template hat (oder umgekehrt), merkt die Metrik nichts.
- **Wirkung:** entweder passend zählen (Node-Items einbeziehen) oder als bewusste Grenze dokumentieren.
- [ ] **Geben?** (Umdefinition → `content_reachable` v2.)

### 2c) skill_spread-Änderung (siehe oben, Punkt SKILL-SPREAD)
- Verknüpft mit der Neuinterpretation; hier nur zur Vollständigkeit gelistet.

---

## ⏳ SPEC-006 — Werkzeug als Zutat (zweite Entdeckungsschicht) — **metrik-seitig BLOCKIERT**

Tier-2-Blueprints mit `tool_tag`-Slot (`CUTTING`/`CHOPPING`) würden `blueprint_reachability`
regredieren, weil `metric_reachability` im Fresh-Gather-Lauf **nie Werkzeuge baut**. Kompensation
= "tool-aware reachability" (Zähler modelliert Werkzeug-Bau als Vorschritt) → `_pair_slots`-Erweiterung
= Constitution-Core. **Reicht über REC-001 hinaus.**

**Optionen (JOURNAL 11.08.):**
- [ ] **A:** tool-aware reachability freigeben (Zähler baut Werkzeuge als Vorschritt) → SPEC-006
      umsetzbar, `discovery_gap` bleibt ehrlich.
- [ ] **B:** SPEC-006 aufschieben; nur Mechaniken, die ohne `tool_tag`-Slots auskommen.
- [ ] **C:** SPEC-006 als "Metriken kümmern sich später" umsetzen (Zähler bleibt ohne Tool-Bau,
      reachability `discovery_gap` wird temporär unrealibel). **Nicht empfohlen** — verfälscht die Steuerung.

---

## 👁️ FORAGE_PRESSURE — (Probezeit bis 20.08., derzeit KEIN Plan-Ziel)

- Erstwert 0.707, Band 0.1–0.5 → **über Band**. `stock < max_stock` als Schwellenwert ist sensibel.
- **Nach 20.08.** entscheiden: Willst du Definition/Band ändern (dann Freigabe nötig) oder das Spiel
  "reiben lassen" und das Band als Draft sehen? Bis dahin nur Beobachtung, kein Ziel.

---

## 🔥 WARMTH_STABILITY — (Probezeit bis 27.08., derzeit KEIN Plan-Ziel)

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
