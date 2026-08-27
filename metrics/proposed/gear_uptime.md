# Proposed Metric: `gear_uptime`

> Research-Proposal, 2026-08-27 (zu SPEC-011 „Werkzeugverschleiß sichtbar machen").
> Falls angenommen (Direktor/Dev nach Constitution: Metriken dürfen **ergänzt** werden):
> Eintrag in `METRICS` mit `"probation_until"` = +14 Tage; Spekulationen über Bandposition
> während der Probezeit sind beobachtend, kein Plan-Ziel.

## Name

`gear_uptime` (v1)

## Was sie erfasst

Wie verlässlich die eigene Ausrüstung nutzbar bleibt, solange echtes Werkzeugbedürfnis
im Spiel existiert. Sie misst die **Verschleiß-Antwort-Achse**: ob ein Spieler (bzw.
Mess-Bot) Attrition bemerkt und beantwortet (nachschärfen, neu bauen, Ersatz führen) —
oder ob der Werkzeugzustand als Nebensache verkommt und erst mit dem Bruch stillsetzt.

Gegenstück der Messphilosophie: dieselbe Struktur wie `warmth_stability`
(Kälte = RAW-Stress, Körper warm = Outcome) und `recovery_stability`
(Verletzung = Stress, behandelt+ruhig = Outcome) — jetzt:
**Werkzeugbedarf = Stress, benutzbares Werkzeug ≥ Warnschwelle = Outcome.**

## Definition (Präzision)

Stress-Tick (RAW-Umfeld, unabhängig vom Besitz): pro gather-Tick jede erntbare
werkzeugpflichtige Node-Ebene — Node mit `req_tool_tag != None`, `req_perception` erfüllt,
`stock > 0`, `depleted == False`. Der Bedarf existiert im Terrain, egal was man besitzt.

Outcome je Stress-Tick: `find_item_by_tag(node.req_tool_tag)` liefert ein Item
und dessen `condition >= 0.25` (WEAR_WARN_THRESHOLD).

```
gear_uptime(seed) = (# Stress-Ticks mit Outcome=true) / (# Stress-Ticks)
Wert              = Median über den Standard-Seedsatz (n=20), Policy wie scorecard-Bots
```

Alle Nach-Bruch-gathers an erntbaren Tool-Nodes zählen als 0 (downtime). Keine
Fehlversuch-Bewertung von Experimenten — rein gather-seitig.

## Berechnungsskizze (Determinismus-Konventionen wie scorecard.py)

Policy-Bot (naiv, seedfest): deterministische Rotation der Locations (forest_edge →
mountain_peak → hidden_cave, Wechsel alle ~40 Ticks), reines `gather()`, Horizon 150 Ticks.
Kein eigenes neues RNG: gleicher Stream-Vertrag wie die anderen Runner (global seeded);
falls SPEC-011-Zugänge RNG mit neuen Würfen einführen sollte (Graduierung der Chance nutzt
bestehende Draws — kein neuer Stream nötig).

Skelett:

```python
def run_gear_uptime(seed):
    random.seed(seed)
    e = GameEngine()
    # Werkzeug erst via Discovery beschaffen lassen? NO — RAW-Definition: Bot darf craften,
    # aber keine Spezial-Versorgung (kein Häufen von Reservewerkzeugen).
    stress = uptime = 0
    for tick in range(150):
        if tick and tick % 40 == 0: _rotate_location(e)
        logs = e.gather()
        for node in e.current_location.nodes:
            if node.req_tool_tag and node.stock > 0 and not node.depleted \
               and e.player.stats["perception"] >= node.req_perception:
                stress += 1
                t = e.player.inventory.find_item_by_tag(node.req_tool_tag)
                if t is not None and t.condition >= 0.25:
                    uptime += 1
    return uptime / stress if stress else None
```

Median über die Standard-Seeds; Ausgabe analog warmth/recovery (value + p25/p75 + n_runs +
Bandlage). Ohne Stress-Ticks → None (wie andere Band-Metriken handhaben).

## Richtung/Band

**Band [0.70, 0.95], keine Richtung** (Bandmetrik).

- **Über 0.95** (inkl. exakt 1.0): Attrition spürt nie — Werkzeuge faktisch unsterblich im
  Spielerlebnis. **Genau das liest der Mechanik-Stand VOR SPEC-011** (Probe C: 13
  werkzeugpflichtige Erfolge in 3×120 Aktionen, 0 Brüche, 0 Warnungen) — die Probezeit-Erstlesung
  dokumentiert also ehrlich die heutige Lücke statt eine gesunde Zahl zu suggerieren.
- **Unter 0.70**: Mechanik straft — Werkzeugverlust zwingt in Downtime zu oft; Spiel fühlt sich
  unfaire Grindfalle an (SUU-per-Session wird zur Pflicht).
- **Zielband**: Verschliss macht Aufwand, ist aber planbar; Downtime selten. Kalibriert gegen
  dem naiven Bot, der NICHT aktiv instandhält (der Wert misst sogar Untergrenze ohne Spielerreife).

## Warum nicht trivial hebbar

1. Heben heißt: nutzbares Werkzeug ≥ Schwelle halten, WÄHREND jeder Einsatz verbraucht. Das
   braucht Nachschubplanung — Flint-/Bone-/Stone-Reisen (regen-limierte Nodes, SPEC-004),
   sharpen_tool-Eingaben oder Redundanzkapazität im Inventar (Traglast 20 kg!).
2. Spam-Craften allein hebt ihn nicht: outcome akzeptiert nur condition ≥ 0.25 — wer Werkzeuge
   kauft/baut und dann liegen lässt, deren Zustand fällt, verliert weiterhin Punkte am selben
   Node.
3. Anders als Re-Craft-Zählungen misst gear_uptime KEINE Klickmenge, sondern Verfügbarkeit im
   realen Bedarfsfenster — auf der RAW-Site definiert (Bedarf des Terrains). Eine bekannte
   Ausweichlücke bleibt: wer Tool-Nodes bewusst meidet, senkt Stress und Downtime gemeinsam.
   Gegenmittel vor Registrierung klären (z.B. Stress auch über passierte Locations bei Rotation
   erzwingen — die fixe Rotation oben nimmt genau das weg, weil sie Locations ungefragt
   durchläuft; ausdrücklich KEEP als feste Konvention dokumentieren).

## Beziehung zu bestehenden Metriken

Ergänzend, nicht korrigierend. `session_depth`/`discovery_gap` bleiben discovery-lastig;
`forage_pressure` misst Rohstoffknappheit, nicht Ausstattungsverlässlichkeit. Mit SPEC-011
landet ein Spielerlebnis, das heute **keiner** gemessenen Achse unterliegt — gear_uptime schließt
genau diese Blende (Constitution: neue Metriken müssen ihre Schwäche benennen; hier:
„Attrition war für den Spieler unsichtbar/unwirksam“).
