# Proposed Metric: `rest_adoption`

> Research-Proposal, 2026-09-10 (zu SPEC-015 „Rast: Zeit als investierbare Ressource").
> Falls angenommen (Direktor/Dev nach Constitution: Metriken dürfen **ergänzt** werden):
> Eintrag in `METRICS` mit `"probation_until"` = +14 Tage; Band-Spekulation während der
> Probezeit ist beobachtend, kein Plan-Ziel.

## Name

`rest_adoption` (v1)

## Was sie erfasst

Ob die neue Zeit-Achse tatsächlich **ankommt und trägt**: Ein Akteur, der die
Rast-Mechanik nutzt (a) erreicht sie im natürlichen Verlauf (er hat Feuer/Ort — die
`_resting_warm()`-Bedingung), und (b) kauft mit Rast-Zeit ein *Ergebnis*, das ohne
Rast in derselben Zeitspanne nicht entstanden wäre. Sie misst die
**Zeit-Investment-Achse**: Rast ist nicht die Aktion, sondern das Ergebnis
(Heilung vollendet, Nacht überstanden) im gereisten Fenster.

Gegenstück der Messphilosophie: `warmth_stability` misst Kälte-Outcome, aber nicht,
ob der Weg dorthin über geplante Zeit-Investment lief; `recovery_stability` misst,
wie viele Verletzungs-Ticks abgewendet werden, aber ihre Policy behandelt "nebenbei" —
sie liest heute die Zufalls-Heilung (Probe: verheilt nach 19 gathers als Nebeneffekt),
nie eine Entscheidung. Ohne diese Metrik wäre SPEC-015 unsichtbar: Scorecard-Bots
rufen `rest()` nie, alle 12 Werte bleiben byte-identisch — genau die Blende, die das
Cron-Mandat ("jeder Spec braucht einen Metrik-Vorschlag") schließt.

## Definition (Präzision)

Rast-Fenster: jeder zusammenhängende Block von ≥ REST_TICKS Ticks, den ein lesender
Bot mit `rest()`-Aufrufen verbringt (Anzahl = ceil(BLOCK / REST_TICKS)).

Outcome je Fenster (eines genügt):
```python
healed_in_window  = any injury removed during window            # Heil-Kette vollendet
survived_night    = body_temp >= 35.0 nach der ersten Nacht-Phase im Fenster
                     (night_mod aktiv)                           # Nacht überstanden
```

```
rest_adoption(seed) = (# Rast-Fenster mit Outcome=true) / (# Rast-Fenster)
Wert                = Median über Standard-Seedsatz (n=20), Bot-Policy siehe Skizze
```

Fenster ohne potentiellen Outcome (keine Verletzung behandelt, keine Nacht im
Fenster) zählen nicht — sie sind reine Zeit-Käufe ohne Bewertung.

## Berechnungsskizze (Determinismus-Konventionen wie scorecard.py)

Policy-Bot (lesend, seedfest, HORIZON 500): Standard-Sammel-Loop wie die v2-Runner;
zusätzlich drei Rast-Anlässe — (1) nach eigenem treat_* (Verletzung behandelt →
Rast-Loop bis Heilung oder Fenster-Ende), (2) bei Nacht-Beginn mit aktivem Feuer
(Rast-Loop durch die Nacht, stoke bei FIRE_DYING-Hinweis), (3) nie ohne
`_resting_warm()`-Bedingung (Rast ohne Feuer/Ort ist kein legitimer Pfad — der
Bot reist stattdessen). Kein eigenes RNG: der Bot konsumiert den Engine-Stream
deterministisch; `rest()` selbst führt keine neuen Würfe ein (nur %-12-Crossings
des bestehenden `_advance_time`).

```python
def run_rest_adoption(seed):
    random.seed(seed)
    e = GameEngine()
    windows = scored = 0
    while e.tick_counter < HORIZON and e.player.hp > 0:
        if e.player.energy < 300:
            _eat_best(e)
        trigger = _rest_trigger(e)        # (1) treated injury, (2) night+fire
        if trigger is None:
            e.gather()
            continue
        pre_inj = set(e.player.injuries)
        pre_bt_night = trigger == "night"
        t0 = e.tick_counter
        while e.tick_counter - t0 < 40 and e.player.hp > 0:
            if e.current_location.fire_fuel < 8.0:
                e.stoke_fire()
            e.rest()
            if set(e.player.injuries) != pre_inj:
                break                     # Heilung vollendet
        windows += 1
        healed = set(e.player.injuries) != pre_inj
        warm = e.player.body_temp >= 35.0 if pre_bt_night else False
        if healed or warm:
            scored += 1
    return scored / windows if windows else None
```

Median über Standard-Seeds; Ausgabe analog warmth/recovery (value + p25/p75 +
n_runs + Bandlage). Keine Rast-Fenster (Bot erreicht nie Behandlungs- oder
Nacht-Bedingung) → None, wie andere Band-Metriken.

## Richtung/Band

**Band [0.4, 0.85], keine Richtung** (Bandmetrik).

- **Unter 0.4:** Rast kommt nicht an — Feuer/Ort-Bedingung im natürlichen Verlauf
  unerreichbar (Brennstoff-Ökonomie, BACKLOG 01.09.), Heil-Kette zu lang fürs
  Fenster, Nacht-Rast tödlich. Mechanik existiert, trägt nicht (dieselbe
  "Mechanik hält, Antwortpfad fehlt"-Klasse wie B10/SPEC-014).
- **Über 0.85:** Rast trivial — der Rast-Anlass des Bots ist immer erfüllbar, keine
  Spannung zwischen "rasten" und "weiterarbeiten". Zeit-Kauf ohne Preis.
- **Zielband:** Rast lohnt sich meist, aber nicht immer — Brennstoff-Puffer,
  Ort-Wahl und Behandlungs-Reihenfolge bleiben echte Entscheidungen. Kalibriert
  gegen einen Bot, der rastet, WENN die Bedingung steht, aber nicht optimiert
  (keine Vorrats-Planung über mehrere Nächte).

## Warum nicht trivial hebbar

1. Heben heißt: die ganze Kette muss halten — Behandlungs-Discovery (treat_*,
   SPEC-009), Feuer am Stück (SPEC-007 + Brennstoff-Ökonomie), Ort-Bedingung
   (`_resting_warm()`), Nacht-Länge (41% der Ticks). Jede schwache Stelle drückt
   die Zahl — das ist der Punkt.
2. **Kein Rast-Spam-Ausweg:** der Bot rastet nur bei legitimen Anlässen und NUR mit
   `_resting_warm()` — wer Rast spamt, verliert stattdessen Energie/HP und
   scheidet vor HORIZON aus (windows zählen nur bei hp > 0). Purer Rast-Spam
   senkt die Zahl also selbst.
3. **Kein Outcome-Ghosting:** Fenster ohne potentiellen Outcome zählen nicht —
   man kann die Quote nicht mit "nutzlosen" Rast-Fenstern verwässern, die
   einfach nur passieren.
4. Metric-Tuning ist verfassungs-blockiert; spiel-seitig "lösen" (Heilrate
   hochdrehen, Brennstoff fluten) würde zwar heben, ist aber der gewollte
   Lernpfad — die Band-Obergrenze (0.85) fängt die Gratis-Variante ab.
5. **Wächter-Kopplung ehrlich:** ein Anstieg von `rest_adoption` bei sinkender
   Überlebensquote wäre verdächtig (Rast als Selbstmord-Schleife) — der Bot
   bricht bei hp <= 0 ab, solche Läufe produzieren unvollständige Fenster
   (ehrlich lesbar im p25/p75-Streuband).

## Beziehung zu bestehenden Metriken

Ergänzend, nicht korrigierend. `recovery_stability` misst die Abwendungs-Quote der
Verletzungs-Ticks (heute: Nebenbei-Policy, p25=p75 flach) — `rest_adoption` misst,
ob die Heil-Kette als bewusster Spielerpfad funktioniert, inklusive Nacht-Achse.
`warmth_stability` misst das Wärme-Outcome, nicht den Planungsweg dorthin. Mit
SPEC-015 landet eine Spielerlebnis-Achse, die heute keiner gemessenen Achse
unterliegt (Zeit-Investment) — `rest_adoption` schließt genau diese Blende
(Constitution: neue Metriken müssen ihre Schwäche benennen; hier: „Zeit ist im
Spiel nicht investierbar, Heilung/Regeneration/Nacht sind keine Entscheidungsräume“).

## Offene Fragen an Direktor/Dev (nicht Blocker)

1. **Bot-Trigger "Nacht+Feuer":** Nacht-Erkennung über die `hour`-Formel (engine-
   intern) oder über bt-Verlauf? Die Skizze liest engine-intern (Determinismus);
   falls Dev das Rast-Verb später eine Nacht-Semantik gibt (sleep-until-dawn),
   braucht die Metrik eine v2.
2. **REST_HEAL_BONUS als Reserve:** falls Dev ihn aktiviert (Heilrate über
   INJ_HEAL_RATE), bleibt die Metrik-Definition unberührt — sie misst Outcome,
   nicht Rate. Gut so.
3. **Fenster-Länge 40 Ticks:** Willkür (≈ 6.5h Spielzeit, deckt ~2 Nachtphasen).
   Kalibrierung während der Probezeit ist erlaubt (Definitions-Feinschliff vor
   Band-Entscheid), Version-Bump dann dokumentieren.
