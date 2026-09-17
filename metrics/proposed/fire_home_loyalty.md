# Proposed Metric: `fire_home_loyalty`

> Research-Proposal, 2026-09-17 (zu SPEC-016 „Glut: der Feuerort erinnert sich").
> Falls angenommen (Constitution: Metriken dürfen ergänzt werden): Eintrag in
> `METRICS` mit `"probation_until"` = +14 Tage; Band-Spekulation während der
> Probezeit beobachtend, kein Plan-Ziel.

## Name

`fire_home_loyalty` (v1)

## Was sie erfasst

Ob die Ortsbindung-Achse tatsächlich **ankommt und trägt**: Ein lesender Bot,
der Feuer führt, verliert es irgendwann (FIRE_OUT ist im natürlichen Verlauf
real — Play 28.08., Rest-Loop-Proben). Gemessen wird, wie oft eine
**Re-Zündung am gleichen Ort** (Glut-Pfad, WOOD-only) im Vergleich zum
**Neuanfang der vollen Zünd-Kette** (tinder+stick+KINDLING-Werkzeug) gelingt —
und ob die Glut-Ökonomie die Feuer-Verfügbarkeit im Nacht-Fenster verbessert.

Gegenstück der Messphilosophie: `warmth_stability` misst Kälte-Outcome am
unterhaltenen Feuer, aber seine Policy hat nie einen Feuer-Kollaps — sie liest
nie FIRE_OUT. `rest_adoption` misst, ob Rast-Fenster Ergebnisse tragen, aber
nicht, *wozu der Spieler zurückkehrt*. Ohne diese Metrik wäre SPEC-016
unsichtbar: Scorecard-Bots berühren die Glut nie, alle 13 Werte bleiben
byte-identisch — genau die Blende, die dieses Proposal schließt.

## Definition (Präzision)

Erhoben pro Run: Ereignisse der Feuer-Bilanz eines Bots, der Feuer *braucht*
(Nacht-Fenster) aber nicht perfekt verwaltet (stoke-Guard nur bei Warnung,
keine Vorrats-Planung):

```python
fire_outs       = # FIRE_OUT-Ereignisse während des Laufs
revive_same     = # Re-Zündungen aus Glut am selben Ort (stoke_fire auf
                  # kaltem Ort mit embers >= EMBER_REVIVE_MIN + WOOD)
relight_full    = # Neuanfänge über start_fire (Prozess) am vorher
                  # befeuerten Ort oder nach Ortswechsel
night_warm      = # Nacht-Crossings (night_mod aktiv), die body_temp >= 35
                  # NACH der Nacht-Phase beenden (Outcome, wie rest_adoption)
```

```
fire_home_loyalty(seed) =
    (# Re-Zündungen am selben Ort, die zu warmem Nacht-Outcome führen)
    / (# Nacht-Fenster mit Feuer-Bedarf),  wenn # Fenster > 0, sonst None
Wert = Median über Standard-Seedsatz (n=20)
```

Nicht vermischt: die Quote bewertet nicht *dass* gezündet wird (das liest
`rest_adoption`), sondern *dass der Rückkehr-Ort den Unterschied macht* —
Fenster, die ohne jeden Feuer-Kontakt enden, zählen nicht (kein Ghosting).

## Berechnungsskizze (Determinismus-Konventionen wie scorecard.py)

Policy-Bot (lesend, seedfest, HORIZON 500): Sammel-Loop wie die v2-Runner
(`_eat_best` bei energy < 300). Feuerverhalten bewusst *unvollkommen* —
stoke nur bei FIRE_DYING-Hinweis (fuel < FIRE_LOW_FUEL), kein Vorratskauf:
so entstehen FIRE_OUTs im natürlichen Verlauf. Nach FIRE_OUT: Bot kehrt in
der Regel zur Beschaffung (gather), dann `stoke_fire()`-Versuch am selben
Ort (Glut-Pfad) — scheitert der (Glut verfallen, kein WOOD), fällt er auf
den `start_fire`-Pfad zurück. Night-Fenster wie rest_adoption (Rast bis
Morgen-Crossing, bt-Outcome nach der Phase). Kein eigenes RNG: der Bot
konsumiert den Engine-Stream deterministisch; SPEC-016 wirft keine neuen
Draws, also bleibt die Bot-Sequenz unter Glut-Patch nur dort anders, wo die
Mechanik wirklich eingreift — genau die Lesbarkeit, die man will.

```python
def run_fire_home_loyalty(seed):
    random.seed(seed)
    e = GameEngine()
    windows = scored = 0
    while e.tick_counter < HORIZON and e.player.hp > 0:
        if e.player.energy < 300:
            _eat_best(e)
        if _night_begins(e):                     # exakte Engine-Uhr-Formel
            loc = e.current_location
            if not _fire_alive(e):               # Glut-Revive zuerst versuchen
                e.stoke_fire()                   # Glut-Pfad oder MISSING_FUEL/NO_FIRE
            if not _fire_lit(e):
                _try_start_fire(e)               # volle Kette als Fallback
            t0 = e.tick_counter
            while e.tick_counter - t0 < 80 and e.player.hp > 0:
                if _fire_lit(e) and e.current_location.fire_fuel < 15:
                    e.stoke_fire()
                e.rest()
            windows += 1
            if e.player.body_temp >= 35.0:
                scored += 1
        else:
            e.gather()                           # Tag: sammeln, keine Vorrats-Planung
    return scored / windows if windows else None
```

Median über Standard-Seeds; Ausgabe analog rest_adoption (value + p25/p75 +
n_runs + Bandlage); None bei 0 Fenstern (wie alle Band-Metriken).

## Richtung/Band

**Band [0.3, 0.8], keine Richtung** (Bandmetrik).

- **Unter 0.4 (Bandunterkante):** die Rückkehr trägt nicht — Glut verfällt zu
  schnell, WOOD fehlt im natürlichen Verlauf, oder Revive gibt zu wenig Feuer
  (RESIDUE zu klein). Mechanik existiert, Antwortpfad fehlt (B10/SPEC-014-
  Klasse). Diagnose über fire_outs/revive_same-Verhältnis (Detail-Block).
- **Über 0.8 (Bandoberkante):** Glut trivial — Revive ist immer möglich und
  immer genug, die Zünd-Kette wird bedeutungslos; Ortsbindung wird Gratis.
  Auch schlecht: der discovery-Wert der Kette (Messer→Zunder→Feuer) kollabiert,
  wenn der Fallback nie mehr gebraucht wird.
- **Zielband:** Rückkehr lohnt meist, aber nicht immer — Glut-Fenster (~60
  Ticks) und WOOD-Beschaffung bleiben echte Fristen. Kalibriert gegen einen
  Bot, der unvollkommen verwaltet (keine Vorrats-Planung), also FIRE_OUTs
  real erlebt.

## Warum nicht trivial hebbar

1. **Die ganze Kette muss halten:** Zähler requires FIRE_OUT real (Ökonomie),
   Glut-Fenster lang genug (Konstanten), WOOD im Inventar (T2-Pfad) UND die
   Nacht-Rast tragbar (SPEC-015 + T1). Jede schwache Stelle drückt die Zahl.
2. **Kein Revive-Spam-Ausweg:** Revive gibt EMBER_RESIDUE (~6 Ticks), nicht
   STOKE_FUEL (8) — Glut-Spam ist strikt schlechter als Pflege des lebenden
   Feuers; der Bot, der Revive statt Nachlegen wählt, verliert das Fenster.
3. **Kein Ghosting:** Fenster ohne Feuer-Kontakt zählen nicht — man kann die
   Quote nicht mit feuerlosen Nächten verwässern (die wären ohnehin Kälte-Tod,
   wie die Play-Logs zeigen).
4. **Meter-Tuning ist verfassungs-blockiert**; spiel-seitig "lösen" (Glut-
   Fenster fluten) würde zwar heben, kollidiert aber mit der Band-Obergrenze
   (Glut wird zur Gratis-Zündung — Zünd-Kette tot) und ist genau der Lernpfad,
   dessen Wirkung gemessen wird.
5. **Wächter-Kopplung ehrlich:** steigt die Quote bei sinkender Überlebens-
   quote, wäre das Revive-als-Selbstmord-Schleife (Revive-Ticks in der Kälte);
   der Bot bricht bei hp <= 0 ab, unvollständige Fenster im p25/p75-Streuband
   lesbar.

## Beziehung zu bestehenden Metriken

Ergänzend, nicht korrigierend. `warmth_stability` misst das Kälte-Outcome
eines Bots, der sein Feuer nie verliert — sie liest strukturell nie FIRE_OUT,
die 28.08.-Versorgungsspirale ist für sie unsichtbar. `rest_adoption` misst,
ob Rast-Fenster Outcome tragen — nicht, ob der Weg zum Feuer über die
Rückkehr an einen erinnerten Ort lief. `fire_home_loyalty` misst die neue
Achse selbst: **Ortsbindung als Spieler-Nutzen** (Constitution-Schwäche:
„die Welt hat kein Gedächtnis für die Arbeit des Spielers — Ortsbindung
existiert strukturell nicht"). Erste Metrik, die eine *Welt*-Eigenschaft
liest statt einer Bot-Policy.

## Offene Fragen an Direktor/Dev (nicht Blocker)

1. **Bot-Trigger "Glut-Revive zuerst":** aktuell stoke_fire-First (Nutzt den
   bestehenden Verb-Namen, keine neue CLI-Semantik). Falls Dev Revive als
   eigenes Verb ausbaut (z. B. `[f]euern`), braucht die Metrik eine v2 —
   Erwartung: nein, der Dev-Pfad über stoke_fire ist der Spec-Weg.
2. **Band [0.3, 0.8] vs. rest_adoption [0.4, 0.85]:** bewusst etwas tiefer
   gesetzt (Glut-Fenster ist eine härtere Frist als die Rast-Bedingung);
   Kalibrierung in der Probezeit erlaubt, Version-Bump dann dokumentieren.
3. **Zähler-Baselines:** fire_outs/revive_same/relight_full als Detail-Block
   ins scorecard-JSON (wie reachable per_blueprint) — Diagnose-Wert ohne
   Metrik-Status, kein Band.

