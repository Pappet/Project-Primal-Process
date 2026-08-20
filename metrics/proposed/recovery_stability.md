# Metrik-Vorschlag: recovery_stability

STATUS: Vorschlag (Explorations-Modus) · zu SPEC-009 (Verletzung & Heilung) · Probezeit ab Umsetzung

## Definition

**`recovery_stability`** misst, ob Verletzungen („Ich wurde an meinem Tun gebremst“) durch die
**entdeckbare Gegenmechanik** (Verband stoppt Bluten, Umschlag + Ruhe heilt) tatsächlich *abwendbar*
sind — d.h. ob die neue Verletzungs-Schicht Entscheidungsdruck erzeugt, den ein handelnder Spieler
planend übersteht, statt ein unaufhaltsamer Substanz-Verlust zu sein.

Operational: Anteil der **Verletzungs-Ticks**, in denen ein Spieler eine aktive Wunde durch einen
**gültigen Heilungs-Vorgang** (Behandlung angelegt UND Ruhe am warmen/Ort-Ort) erfolgreich abwendet
oder abklingt — gemessen über eine geführte Policy, die bei Verletzung einen Verband/Umschlag nutzt
und am Feuer/der Höhle rastet (analog zur survival-sound Policy von `warmth_stability`).

```
Verletzungs-Tick = ein Tick, an dem Player.injuries nicht-leer ist (cut blutet oder strain aktiv).
recovery         = der Tick liegt im Abklingen-Regex: Wunde ist behandelt (bandage/poultice-Verb.
                   angelegt) UND Spieler rastet an wärmer/or-heits-Location (feu fait ODER cave).
recovery_stability = median über Seeds( recovery_ticks / Verletzungs-Ticks )
```

## Was sie erfasst

- **Wirkung der Mechanik, nicht ihre Existenz:** nicht „gibt es ein Bandage-Item“ (per Code-Inspektion
  trivial), sondern ob der regelhafte Lauf Verletzungen **erlebt** UND durch **entdecktes Handeln**
  (Behandlung craften, Ruhe organisieren) vom Substanz-Verlust wegkommt.
- **Abwendbar, nicht abkürzend:** niedriger Wert = Verletzung entgleist (Heilung zu schwach / Prozesse
  unerreichbar / Ruhe-Bonus wirkungslos) → Mechanik tot. Sehr hoher Wert = Verletzung ist nie eine
  echte Drohung (Verband gratis, Ruhe erzwungen frei) → kein Entscheidungsdruck.
- **Entscheidungsdruck:** ob die Verletzungs-Schicht den Rhythmus prägt (vorbereiten: Verband/Paste
  tragen; eingehen vs. vermeiden: exponiert sammeln oder nicht) statt ein statischer HP-Abzug zu sein.

## Berechnungsskizze (stdlib only, deterministischer Seed-Satz wie `tools/scorecard.py`)

```
for seed in SEEDS:                      # z.B. 20 Seeds
    rng = random.Random(seed)
    eng = GameEngine()
    inj_ticks = 0
    rec_ticks = 0
    for _ in range(HORIZON_N):          # z.B. 300 Aktionen
        policy(eng): bei cut -> craft_bandage + anwenden; bei strain -> poultice; rastet am Feuer
        eng._advance_time(1)            # Bleed/Heilung/Thermo wirken
        if injekte(eng.player) != leer:
            inj_ticks += 1
            if behandelt(eng.player) and rastet_am_warmen_ort(eng):
                rec_ticks += 1
    ratio = rec_ticks / max(1, inj_ticks)
value = median(ratios); p25/p75 in Details; JSON-Ausgabe wie bestehende Metriken.
```

## Richtung / Zielband

**Band 0.3 – 0.7, Richtung höher (aber bandgebunden, analog `warmth_stability`).**
- Unter 0.3: Verletzung überrollt den Spieler — Verband/Umschlag zu schwach, Ruhe-Bonus wirkungslos,
  Heil-Prozesse unerreichbar → SPEC-009 ist wirkungslos (Bleed dominiert).
- Über 0.7: Verletzung ist nie eine echte Frist — Behandlung zu frei, Ruhe zu erzwungen, kein
  Entscheidungsdruck (Mechanik wird Statik).
- Im Band: Verletzung ist **spürbar, aber durch Vorbereitung und Ruhe abwendbar** — der Zustand, den
  Long Dark/URW anstreben.

## Warum nicht trivial zu heben

Der Wert hängt von einer **echten Abfolge** Risiko-Exposition ab: Seeds, Orts-/Materialsicherheit
(exponiertes Sammeln), ob die Behandlung **entdeckt und gecraftet** wurde (Prozesse), und davon, dass
der Agent **aktiv rasten/behandeln** muss, um vom Bleed wegzukommen. Ein einzelner String oder
interner Parameter verschiebt nichts; man müsste Verletzungs-Wahrscheinlichkeiten, Bleed-Rate,
Heil-Prozess-Reachability oder die Ruhe-Regel real umbalancieren — was die **spielerseitig spürbare**
Verletzungs-Bedrohung ändert. Konform zur Constitution: Metriken sind Indikatoren; diese misst eine
Spieler-Erfahrung (abgewendete Verletzungs-Frist).

## Probezeit / Aufnahme

Nach Peters Freigabe (Metrik-Core) aufnehmen, offset +14 Tage (analog `warmth_stability`), Richtung
None, Band 0.3–0.7 wie oben. Erstwert deterministisch aus dem geführten Seed-Satz zu ziehen und in
`SCORECARD.md`/`metrics/proposed/` zu dokumentieren. Zwei Wochen, bevor sie Plan-Ziele steuern darf
(Constitution, §Messung).