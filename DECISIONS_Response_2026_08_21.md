# Entscheidungen von Peter — zu DECISIONS.md (2026-08-22)

> Ich habe die Scorecards 14.08.–21.08., die Play-Reports und den Backlog gelesen. Die Langeweile-Stelle ist real, und sie ist das Wichtigste auf dem Tisch. Diese Entscheidungen räumen die Warteschlange ab — in der Reihenfolge unten. Alles andere bleibt, wie es ist.

**Grundsatz (gilt für alle Punkte):** Metriken sind Indikatoren, nicht Ziele. Jede Freigabe hier ist eine *Ehrlichmachung* oder *Freischaltung* — keine Zahl darf dadurch schöner werden, ohne dass sich das Spielerlebnis ändert. Wer eine Zahl hebt, ohne das Spiel zu ändern, verletzt die Constitution — auch mit dieser Freigabe.

## 1. skill_spread — `[x]` **Option A (umdeuten)**
Formel bleibt, Version bleibt 1. Beschreibung/Richtung in `METRICS`/SCORECARD anpassen: fallender Wert = **gehobene Einsteiger-Decke** (Zufallsspieler überlebt näher am Optimum), kein Tiefenverlust. Option B (Umformung) verwerfe ich — der Experten-Decke-Befund (opt ~240, ökonomie-gebunden) bleibt Backlog-Beobachtung.

## 2. craft_variety v2 — `[x]` **freigegeben**
Zählt künftig distinkte `blueprint_id`s **und** `process_id`s. Das Prozess-System ist ein vollwertiger Craft-Pfad; die Metrik darf ihn nicht ignorieren. Version 2, erste Lesung zeigt „neu definiert".

## 3. content_reachable v2 — `[x]` **freigegeben**
Zähler prüft zusätzlich Node-Referenzen: ein Node, dessen `result_template_id` kein Template hat, zählt als definiert-aber-unerreichbar → Metrik fällt sichtbar. Genau das hätte B06/B07 am Tag 1 gezeigt. Die `⚠ Content entfernt`-Logik bleibt unverändert.

## 4. feedback_quality v3 (NEAR_MISS) — `[x]` **freigegeben**
`_expected_fragment("NEAR_MISS:…")` → `"gehören"`. Der Near-Miss-Text ist absichtlich vage; seine Nützlichkeit ist seine Vagheit — er zählt als informativ. Pflicht dabei: **Vollständigkeits-Test** — jeder Reason-Code, den die Engine emitieren kann, braucht ein Fragment oder einen dokumentierten `None`-Grund. Version 3.

## 5. session_depth v2 — ziel-bewusster naiver Bot — `[x]` **freigegeben, Probezeit**
Der aktuelle Bot ist strukturell blind für gestufte Discovery (Play 18./19./21.08.). Neudefinition: der naive Bot bekommt minimale Zielgerichtung — er verfolgt NEAR_MISS-Hinweise, versucht Blueprints, für die er ≥2/3 Materialien hält, und darf ab survival ≥ 0.4 gated Blueprints versuchen. Kein Orakel, kein Rezeptbuch — nur ein Spieler, der nicht „kalt" aufgibt. Version 2, **Probezeit 14 Tage ab Landung** (beobachtend, kein Plan-Ziel).

Ehrlich vorweg: Die erste v2-Lesung wird **höher ausfallen, ohne dass sich das Spiel geändert hat**. Das ist Re-Baselining, kein Fortschritt — nicht feiern.

## 6. Tool-aware reachability — `[x]` **Option A freigegeben**
Der Zähler soll messen, was die Engine wirklich craften kann — inkl. Werkzeug-Bau als Vorschritt. Disziplin wie bei REC-001: Dev liefert Patch-Entwurf (**REC-002**) mit Wirkungsabschätzung + Tests; Anwendung nach Verifikation (Reachability = Engine-Truth, keine andere Metrik geschwächt). Ob Tier-2 über Tool-Tags, `min_survival_req`-Gates oder gemischt läuft, ist Design-Entscheidung von Dev/Direktor — der Zähler muss nach dem Patch nur noch die Wahrheit zählen.

## 7. SPEC-006 — `[x]` **freigegeben, priorisiert** (nach 5 + 6)
Akzeptanz: session_depth (v2) steigend, Reachability 1.0 (tool-aware), `discovery_gap` wird beobachtet. **Wichtig:** Steigt der Gap über 0.6, ist das ein *Spiel*-Signal (naive Spieler finden Tier-2 nicht) → die Antwort ist spiel-seitlich (NEAR_MISS-Erweiterungen, Hinweise, Gate-Balance) — **niemals** eine Metrik-Abschwächung. Der Bandrand bei 0.6 ist akzeptiert; optimiert nicht aufs Band hin.

## 8. forage_pressure — v2-Neudefinition freigegeben; **das Band wird NICHT geschoben**
0.707 über Band ist definitionsbedingt: `stock < max_stock` zählt jede frisch geerntete Stelle als „Knappheit". Das Band auf ~0.7 zu verschieben wäre Pfeil-Ziel-Malen — mache ich nicht. Stattdessen: v2 misst *gefühlte* Knappheit (z. B. Anteil Versuche, die durch Erschöpfung verweigert oder deutlich gemindert werden; exakte Schwelle schlägt Dev/Direktor vor, ich gebe sie gegen). Probezeit 14 Tage, beobachtend.

## 9. warmth_stability / recovery_stability — beobachtend bestätigt
warmth: Probezeit bis 27.08. läuft aus, danach als Beobachtungsgröße akzeptiert; die p25=p75-Flachheit ist bekannt — nach Probeende prüfen, ob realistischere Policy-Streuung ihn informativ macht. recovery: Probe bis 03.09., dito. Keins wird Plan-Ziel vor Probeende.

## Reihenfolge (Dev arbeitet von oben nach unten)
1. **Ehrlichmachungs-Batch** (eine Session): Pkt. 1–4.
2. **session_depth v2** (Pkt. 5).
3. **REC-002 Entwurf + Anwendung** (Pkt. 6).
4. **SPEC-006** (Pkt. 7).
5. forage_pressure v2 (Pkt. 8) — parallel möglich, Probezeit läuft separat.

## Sonstiges
- **Play-Tooling** (guided_full Rückzug-Trigger, 🔵 21.08.): braucht **keine** Freigabe — chirurgisch fixen mit 20-Sweep-Gegenprobe, wie im Backlog beschrieben.
- **Direktor:** Diese Entscheidungen ins JOURNAL (mit Datum), DECISIONS.md-Checkboxen abhaken, PLAN.md am Sonntag neu schreiben — SPEC-006 als Top-Priority in der Reihenfolge oben. Save/Load (M0.4-Rohmaterial) darf dabei priorisiert werden: kein Metrik-Core, keine Freigabe nötig.
- **discovery_gap-Randlage (0.6):** akzeptiert als known-fragile Baseline. Nicht blind kompensieren (siehe Backlog 20.08.).

— Peter
