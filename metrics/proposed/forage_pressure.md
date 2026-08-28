# Metrik-Vorschlag: forage_pressure

STATUS: Vorschlag (Explorations-Modus) · zu SPEC-004 · Probezeit ab Umsetzung
**v2 umgesetzt am 28.08. (Pkt. 8, Freigabe 27.08.): verweigert ODER erster erntbarer Node
stock/max < 0.5; Schwelle 0.5 = Dev-Vorschlag, Peters Gegen-Vorbehalt offen; Band (0.1, 0.5)
unverändert; Erstlesung 0.0 (p25 0.0, p75 0.03) — unter Band, beobachtend, kein Tuning.**

## Definition
**`forage_pressure`** misst, wie oft eine Sammel-Aktion vom **lokalen** Vorratszustand beschränkt wird — d.h. der Anteil der Gather-Versuche, die an einem nicht vollständig gefüllten Node stattfinden (`stock < max_stock` im Moment des Versuchs, also skalierte Chance oder leere Stelle). Sie quantifiziert, ob Ressourcenknappheit im Spiel **tatsächlich gefühlt** wird und Sammel-Entscheidungen (Doumt-wechseln vs. bleiben/warten) erzwungen werden.

## Was sie erfasst
- **Wirkung der Mechanik, nicht ihre Existenz:** nicht "hat ein Node einen Vorrat" (das wäre per Code-Inspektion trivial), sondern ob der Spieler im regelhaften Lauf **auf** Knappheit stößt und darauf reagieren muss.
- **Entscheidungsdruck statt Reibung:** ob Knappheit den Foraging-Rhythmus prägt (Rotieren, Rückkehr nach Regen) — oder ob Nodes faktisch unendlich / zu schnell regenerieren (Druck = 0, Mechanik tot) bzw. grundlos leeren (Druck zu hoch, Grind).

## Berechnungsskizze (stdlib only, deterministischer Seed-Satz wie `tools/scorecard.py`)
```
for seed in SEEDS:                      # z.B. 20 Seeds
    rng = random.Random(seed)
    eng = GameEngine()
    n_attempts = 0
    n_underperform = 0
    for _ in range(HORIZON_N):          # z.B. 200 Aktionen
        node = wähle nächsten erntbaren Node (fixe naive Policy, z.B. erster mit req erfüllt)
        if not node: continue
        if node.stock < node.max_stock:          # Vorrat nicht voll → Knappheit greift
            n_underperform += 1
        n_attempts += 1
        # ... Gather tatsächlich ausführen + _advance_time (Regen wirkt) ...
    ratio = n_underperform / max(1, n_attempts)
value = median(ratios); p25/p75 in Details; JSON-Ausgabe wie bestehende Metriken.

## Richtung / Zielband
**Band 0.1 – 0.5, keine Richtung** (wie `discovery_gap`).
- Unter 0.1: Knappheit verpufft (Nodes regenerieren zu schnell / Vorrat zu groß) → Mechanik unsichtbar, SPEC-004 wirkt nicht. Node-Regeneration zu hoch schrauben.
- Über 0.5: das Sammeln wird zu reiner Frustration/Grind (Spieler läuft dauernd ins Leere) → Über-Tuning, Regeneration senken.
- Im Band: Knappheit ist **spürbar** (Spieler muss wählen/rotieren) aber nicht erstickend. Das Band selbst ist der Verifikationsbeleg für "Mechanik wirkt wie entworfen".

## Warum nicht trivial zu heben
Der Wert hängt von der echten Vorrats-Dynamik über eine **Sequenz echter Agent-Harvests** ab (Seeds, Gather-Treffer, `_advance_time`-Regeneration, Ortswechsel) — nicht von einem String oder einem konstanten Parameter. Man kann ihn nur beeinflussen, indem man Depletion-/Regen-Raten real umbalanciert, was die **spielerseitig erfahrbare Knappheit** ändert. Eine String-Änderung oder interne Re-Codierung läuft ins Leere, weil der Wert die tatsächliche Denied-Erfahrung des Agenten zählt. Konform zur Constitution: Metriken sind Indikatoren, nicht Ziele; diese misst eine Spieler-Erfahrung (verweigerte/geminderte Ernte).
