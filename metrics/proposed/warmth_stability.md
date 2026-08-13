# Metrik-Vorschlag: warmth_stability

STATUS: Vorschlag (Explorations-Modus) · zu SPEC-007 (Feuer & Wärme) · Probezeit ab Umsetzung

## Definition

**`warmth_stability`** misst, wie gut ein Spieler Kälte-Exposition durch die *Gegenmechanik*
(aktives Feuer, Isolation/Kleidung) übersteht. Sie quantifiziert, ob die neue Wärme-Schicht
tatsächlich **Player-Experience** verändert — d.h. ob Kälte eine spürbare, aber *abwendbare*
Bedrohung ist, statt ein unaufhaltsamer Kältetod.

Operational: Anteil der **Kälte-Stress-Ticks**, in denen die Körpertemperatur **über der
Unterkühlungs-Schwelle (35°C)** gehalten wird — gemessen über eine geführte, survival-sound
Policy, die bei Kälte Feuer baut/nachlegt und Kleidung besitzt, wenn vorhanden.

```
Kälte-Stress-Tick = ein Tick, an dem die effektive Umgebung unter einer Komfortschwelle liegt
                    (z.B. ambient + fire + insulation-Effekt < 25°C), d.h. wo ohne Gegenmechanik
                    body_temp Richtung 35°C fiele.
warm = body_temp >= 35.0 in diesem Tick
warmth_stability = median über Seeds( warm_ticks / Kälte-Stress-Ticks )
```

## Was sie erfasst

- **Wirkung der Mechanik, nicht ihre Existenz:** nicht "gibt es ein Feuer-Item" (per Code-Inspektion
  trivial), sondern ob der Spieler im regelhaften Lauf Kälte-Stress erlebt UND durch eigenes
  Handeln (Feuer/Isolation) die Unterkühlung abwendet.
- **Abwendbar, nicht eingeschaltet:** niedriger Wert = Kälte dominiert und die Gegenmechanik
  verpufft (Feuer zu schwach / Brennstoff zu knapp / Isolation wirkungslos) → Mechanik tot.
  Sehr hoher Wert = Kälte ist nie eine echte Drohung (Komfortschwelle zu weich / Feuer zu frei) →
  kein Entscheidungsdruck.
- **Entscheidungsdruck:** ob Wärmemanagement den Rhythmus prägt (Holz nachlegen, am Feuer rasten,
  Kleidung bauen) statt ein statischer PNJ-Ticker zu sein.

## Berechnungsskizze (stdlib only, deterministischer Seed-Satz wie `tools/scorecard.py`)

```
for seed in SEEDS:                      # z.B. 20 Seeds
    rng = random.Random(seed)
    eng = GameEngine()
    cold_ticks = 0
    warm_ticks = 0
    for _ in range(HORIZON_N):          # z.B. 200 Aktionen
        # survival-sound Policy: bei Kälte Feuer bauen/nachlegen, Kleidung nutzen
        if ist_kalt(eng) and hat_brennstoff(eng): eng.stoke_fire(...)
        eng._advance_time(1)            # Weather/Temp/Brennstoff wirken
        amb = effektive_umgebung(eng)   # ambient + fire + insulation-Effekt
        if amb < KOMFORT (25.0):
            cold_ticks += 1
            if eng.player.body_temp >= 35.0:
                warm_ticks += 1
    ratio = warm_ticks / max(1, cold_ticks)
value = median(ratios); p25/p75 in Details; JSON-Ausgabe wie bestehende Metriken.
```

## Richtung / Zielband

**Band 0.4 – 0.9, Richtung höher (aber bandgebunden).**
- Unter 0.4: Kälte überrollt den Spieler trotz Gegenmechanik → Feuer/Isolation wirken nicht,
  SPEC-007 ist wirkungslos (Heat-Werte zu niedrig, Brennstoff zu knapp, Isolation zu schwach).
- Über 0.9: Kälte ist nie eine echte Gefahr → kein Entscheidungsdruck, die Mechanik wird zur
  Statik (Komfortschwelle zu weich, Feuer zu frei, Brennstoff unbegrenzt).
- Im Band: Kälte ist **spürbar, aber durch Planung abwendbar** — genau der Long-Dark-Zustand.
  Das Band selbst ist der Verifikationsbeleg "Mechanik wirkt wie entworfen".

## Warum nicht trivial zu heben

Der Wert hängt von einer **echten Sequenz** Kälte-Exposition ab (Seeds, Wetter-RNG, Nacht/Tag,
Location-Temperatur, Brennstoff-Drain, Feuer-Erlöschen, Kleidungs-Besitz) und davon, dass der
Agent wirklich **handeln** muss (Feuer bauen → Holz nachlegen → ggf. Kleidung bauen), um die
Schwelle zu halten. Ein einzelner String oder ein interner Parameter verschiebt den Wert nicht
handfest; man müsste Heat-Werte, Brennstoff-Dauer, Isolation-Wirkung oder die Policy real
umbalancieren — was die **spielerseitig erfahrbare** Kälte-Bedrohung ändert. Konform zur
Constitution: Metriken sind Indikatoren; diese misst eine Spieler-Erfahrung (abgewendete
Unterkühlung).
