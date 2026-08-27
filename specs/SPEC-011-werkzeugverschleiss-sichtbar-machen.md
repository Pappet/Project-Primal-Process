# SPEC-011 — Werkzeugverschleiß sichtbar machen (Attrition wird zum System)

> Research (free-exploration Modus), 2026-08-27. Feldliste-Kandidat „Werkzeugverschleiß".
> Constitution-Check: bestehende Werkzeuge/Materialien bleiben; **kein** neues Template,
> **keine** neuen Reason-Codes, **kein** Metrik-Eingriff — der Code-Pfad existiert bereits
> (`core.py:329-334`); diese Spec verdrahtet ihn in Wahrnehmung und Hebel.
> Sie ist das dritte gefundene „totkodierte System" nach SPEC-007 (Thermodynamik ohne Gegenhebel)
> und SPEC-009 (Verletzungen ohne Material-Gegenstück) — diesmal: Druck vorhanden,
> aber niemals als Information oder Entscheidung beim Spieler angekommen.

## Problem

**Befund (empirische Probes, 2026-08-27, Seeds 20260827/101/20260826/404):**

Der Verschleiß-Code läuft seit Anfang an und wird in `gather()` benutzt:

```python
# engine/core.py:329-334
if used_tool:
    wear = 0.05 / used_tool.get_attr("durability", 0.5)
    used_tool.condition = max(0, used_tool.condition - round(wear, 2))
    if used_tool.condition <= 0:
        self.player.inventory.items.remove(used_tool)
        logs.append(f"!!! {used_tool.name} zerbrochen !!!")
```

Vier Verdrahtungslücken machen daraus ein Phantom-System:

1. **Stummer Verschleiß.** Die Axt fällt von condition 1.0 → 0.88 → 0.76 → … mit **null**
   Logzeile (Probe A). Der Spieler sieht zu keinem Zeitpunkt, dass sein Werkzeug altert.
2. **Cliff statt Kurve.** Jedes Werkzeug mit `condition > 0` erntet mit voller
   Wahrscheinlichkeit (`eff_chance = node.chance * (node.stock/max_stock)` betrachtet die
   Condition überhaupt nicht). Ein Werkzeug bei cond 0.08 arbeitet exakt wie ein frisches —
   bis es spurlos verschwindet. Keine absehbare Entscheidung „noch einmal nutzen oder schonen".
3. **Post-break: totale Stille.** Nach dem Bruch schweigt `gather()` komplett:
   `core.py:296-297` — `if not used_tool: continue` wirft für werkzeugpflichtige Nodes
   **nicht eine Zeile**, keine Funde und keine Meldung. Probe B: Nach Bruch, Oak-Node voll
   (`chance 1.0`, stock max) — vier gathers liefern nur Äste/Beeren/Kiesel, kein Wort über
   fehlendes Werkzeug. Der Spieler kann den Verlust nicht einmal benennen. Nur das Zerbrechen
   selbst meldet sich genau einmal („zerbrochen"), danach Funkstille.
4. **Kein Instandhaltungshebel.** `data/processes.json` enthält nichts zu Schärfen/Reparieren
   (Prozesssuche leer). Recraft von Grund auf (neue Flint-Reise) ist die einzige Lösung —
   vom Spieler unentdeckt, weil nichts hin führt.

**Quantitative Unsichtbarkeit (Probe C):** 3 × 120-Aktions-Läufe mit Axt ab Start:
insgesamt **13** werkzeugpflichtige Erfolgsernten (oak/hunt), **0** Brüche, **0** Warnungen.
Selbst im obersten Nutzungsband tritt Attrition nie als Erlebnis auf — es sei denn, man fegt
gezielt ~9 Eichenstämme durch eine einzige Axt, um dann undurchsichtig stillzusetzen.

**Randbefund im selben Pfad (betrifft PEBBLE/Munition):** Jagd nutzt `find_item_by_tag("PROJECTILE")`
— Kieselstein-Stacks mergen zu einem Objekt, der Wear-Pfad (Punkt oben) wascht den **gesamten Stack**
kollektiv; bei cond ≤ 0 verschwindet die komplette Munitionsration (~4 Jagderfolge) ohne Vorwarnung.
Verbrauchslogik („ein Kiesel fliegt") fehlt vollständig. *Aus Scope dieser Spec* — hier nur als
direkte Folge des selben Wear-Pfads dokumentiert, Fix später separat.

**Systemische Diagnose:** Genau die Klasse „Druck ohne Wahrnehmung, Hebel oder Abstufung"
(SPEC-007-/SPEC-009-Muster): Das Spiel rechnet ein echtes System aus (Durability aller
Blueprints = min der Komponenten-Durabilities, z.B. Flint-Axt min(0.8 Stiel, 0.4 Kopf, 0.5 Faser)
= 0.4 ≈ 9 Nutzungen), doch kein Spielerisches Signal, keine graduelle Wirkung und kein Heilweg
macht es erfahrbar. Folge: Werkzeuge sind faktisch unsterblich — bis sie mit einem Schlag
spurlos verschwinden; die Material-Dreieinigkeit FLINT/BONE/STONE hat nach einmaliger Nutzung
keinen laufenden Sinn mehr, und Holz/Ton/Jagd bleiben ohne Nachschubökonomie gekoppelt.

## Mechanik

Drei Gegen-Spiele, alle mit derselben Struktur — Zustand ist Information, wirkt graduell vor
dem Ausfall und hat einen Weg zurück statt nur Neubau:

- **UnReal World:** Schneidige Werkzeuge stumpfen durch Arbeit; stumpfe Äxte schlagen schneller
  kaputt/weniger gut; Wetzsteine (whetstones) schärfen sie wieder her. Der Zustand ist am
  Objekt sichtbar und entscheidend, lange bevor das Werkzeug auseinanderfällt.
- **Don't Starve:** Durability als sichtbarer Ring am Item; unterhalb voller Wirksamkeit sinkt
  der Nutzen stetig, bei null zerbricht das Item. Man *plant* Ersatzbeschaffung statt vom
  Ausfall überrascht zu werden.
- **The Long Dark:** Werkzeuge tragen eine sichtbare Condition %, Ernteergebnis skaliert damit;
  total verbrauchte Werkzeuge werden unbrauchbar aber bleiben (oder sind reparierbar).

Gemeinsamer Kern: **Abnutzung ist lesbar** (Warnung + Graduierung), **wirkt spürbar**
(weniger Chance) und **ist heilbar** (Schärfen/Nachlegen aus Vorrat).

## Adaption

Alles additive Engine- und Prozessarbeit; am Tag-Blueprints-System, an den Blueprints/Daten und
an Metriken wird nichts geändert.

### A. Graduelle Wirkung (engine/core.py::gather)

Vor der Erfolgsentscheidung eines werkzeugpflichtigen Nodes:

```python
eff_chance = node.chance * (node.stock / node.max_stock)          # Bestand (SPEC-004)
if node.req_tool_tag and used_tool is not None:
    eff_chance *= max(WEAR_MIN_FACTOR, used_tool.condition)       # NEU: Attrition-Graduierung
```

Konstanten oben in core.py: `WEAR_WARN_THRESHOLD = 0.25`, `WEAR_MIN_FACTOR = 0.25`
(gleiche Form wie `chance * stock/max` in SPEC-004 — ein Muster, zwei Achsen).

### B. Vor-Warnung (einmalig pro fallender Durchgang)

Nach dem Wear-Decrement in `core.py:329-334`: falls die Condition dieses Mal
(erstmals wieder) unter `WEAR_WARN_THRESHOLD` rutscht, zusätzlich:

```python
logs.append(f"!!! {used_tool.name} ist stark abgenutzt !!!")
```

Einmaligkeit pro Durchgang implizit: die Warnung feuert nur an dem gather-Tick, der die
Schwelle unterschreitet (vorher ≥ Schwelle, danach < Schwelle) — kein Dauerspam bei jedem
weiteren Einsatz. Route **über gather-Zeit-Logs**, nicht über Experiment-Reasons
(SPEC-009-Pattern, `_expected_fragment`-Maschine bleibt unberührt).

### C. Post-break-Feedback (die Stillstell-Falle schließen)

Analog STRUKTUR einer Zeit-Log-Meldung: falls ein werkzeugpflichtiger Node diesen Tick
ernten wäre (perception passierbar, `stock > 0`, `depleted False`) aber
`find_item_by_tag` liefert None → ergänze

```python
logs.append(_feedback_message("MISSING_TOOL"))  # generisch, ohne Tool-Tag-Nennung
```

Textvorschlag (in `_feedback_message` ergänzen, dezent): `„Du brauchst ein Werkzeug dafür."`
**Kein neuer Experiment-Reason** — EMITTABLE_REASONS-Lock der Metrik bleibt unangetastet;
die Meldung lebt ausschließlich im gather-Logstream. Häufigkeitsdämpfung: Die Meldung erscheint
nur wenn der Node wirklich erntbar wäre (stock + perception geprüft), also Nodegebunden statt
jedes Leerlaufs — der Altpfad „teilweise Nodes leer" spammt weiter nichts neu.

### D. Instandhaltungshebel — Prozess `sharpen_tool`

Neuer Apply-only-Prozess in `data/processes.json` (Behandlungs-Muster SPEC-009):

- Eingabe: **1× flint_shard** (bestehendes Template — kein content_reachable-Effekt),
- Wirkung (special-case Block in `execute_process`, analog `start_fire`/Bandage):
  das am meisten abgenutzte getragene Werkzeug mit
  `tool_tags ∩ {CUTTING, CHOPPING, PIERCE}` (`condition < 1.0`) wird geschärft:
  `condition = min(1.0, condition + SHARPEN_RESTORE=0.5)`; consume des Splitters
  erst NACH Erfolg — scheitert es (kein verschlissenes Werkzeug da), nichts konsumieren
  und Meldung „Nichts hier, das zu schärfen wäre." (`NO_WORN_TOOL` intern als bestehender
  Verbandstext? Nein — kein neuer Reasoncode: Ergebnis via Standardprozesse mit generischem
  Text wie die Behandlung, siehe Dev-Pattern „Reveal an SUCCESS hängen").
- Flint gewinnt dadurch eine zweite Rolle: Klinge-Quelle UND Schleifmaterial — die knappe
  Node-Ökonomie (SPEC-004, kleine Stockwerte bei Flint) zahlt direkt in die Wartungsschicht
  hinein.

### E. Bewusst NICHT in dieser Spec

- Pebble-Munitionsverbrauch (Randbefund oben) — separates Design: „Projektil = Consumable".
  → BACKLOG-Idee parallel angelegt (Format wie üblich).
- Condition-Anzeige im Inventar-CLI — bleibt beim CLI-Display unverändert; die Log-Meldungen
  (B/C) tragen die Wahrnehmung.

## Tests / Akzeptanzkriterien

Jede zur Verifikation gebunden — pytest-Datei z.B. `tests/test_wear.py`:

1. **Warnung feuert einmal:** Axt synthetisch auf cond >0.26 setzen, oak-reich, mehrere
   gathers — exakt **eine** `abgenutzt`-Zeile an dem Tick, der die Schwelle kreuzt; weitere
   gathers danach zeigen keine neue Warnung mehr.
2. **Post-break Meldung:** Axt manuell entfernen (`inventory.items.remove`), Nodes voll,
   `gather()` liefert mind. eine Meldung mit `Werkzeug`-Subtext beim CHOPPING-Pfad; ohne
   mindestens einen erntbaren Tool-Node (z.B. anderem Ort) keine Meldung.
3. **Graduelle Wirkung:** deterministisch (seeded): 50 wood-gathers mit condition 1.0 vs
   0.25 → Erfolgssumme(cond 0.25, floor Faktor ~0.25*) signifikant kleiner (approx-Bounds);
   Mantisse: chance 1.0 * stockmax * floor = gedämpft.
4. **sharpen_tool:** Erfolg konsumiert flint_shard, Condition steigt (+0.5, cap 1.0);
   zweiter Aufruf ohne verschlissenes Werkzeug: **kein** Verbrauch.
5. **Suite-Invariante:** `feedback_quality` bleibt 1.0 (inline-probe), `blueprint_reachability`
   1.0, `content_reachable` 1.0; python `-c compute_all()` — **vollständige Delta-Tabelle**
   vor/nach im JOURNAL dokumentiert (RNG-Strom-Klasse SPEC-009/SPEC-010 verpflichtend prüfen).
   Falls discovery_gap > 0.65 (hot edge, BACKLOG Direktor-Flag 26.08.): Direktor-Flag im
   selben Commit, NICHT still tunen.

## erwartete Metrik-Wirkung

Ehrlich gesagt — **primär keine**: `session_depth` misst Discovery-Novelty, keinen
Wartungsloop; ein Pflegezyklus schiebt den Erschöpfungspunkt weder materiell noch messbar
für den Bot. Genau deshalb trägt diese Spec ihren eigenen Proposed-Metric
(`metrics/proposed/gear_uptime.md`, Probeband [0.70, 0.95]) — die Lücke, die Attrition bisher
nicht zeigen kann (Wartung als gelebte Entscheidungsachse), ist in keiner heutigen Messgröße
enthalten. Der neue Wert soll genau das benennen können (probation-style).

Indirekte Seiteneffekte (bei der vollständigen Suite-Probe auszuweisen, nur dokumentiert,
nie ans Band getunt — Stream-Klasse SPEC-009/SPEC-010): `craft_variety` könnte leicht steigen
(Recraft + Schärfen = neue Aktionsmuster); `forage_pressure` reagiert eher auf Verschiebungen
der Node-Sequenz. Alles wie immer: **Metrik = Indikator. Diese Spec verändert das
Spielerlebnis (Abnutzung als lesbarer Zustand + Instandhaltung als Hebel), nicht die
Zielstellen des Scorecards.**
