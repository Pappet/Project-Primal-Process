# SPEC-007 — Feuer & Wärme: Gegen-Schleife zur Unterkühlung (System-Tiefe)

STATUS: offen · angelegt 2026-08-13 · Quelle: Research (Explorations-Modus, kein Metrik-Anker)

## Problem

**Befund (empirisch verifiziert):** Das Spiel hat ein vollständiges, aber *totes* Thermodynamik-System.
`engine/core.py` berechnet Umgebungstemperatur (`_get_ambient_temp`), Körper-Wärme-Verlust
(`temp_loss`) und bestraft Unterkühlung/Hitzschlag mit HP-Schaden in `_advance_time`. Kalte
Location + Wetter + Nacht = unaufhaltsamer Kältetod:

```
Ort= mountain_peak (base_temp 2.0), Wetter=STORM, Nacht → ambient ≈ -18°C
body_temp sinkt ~1.6°C/tic → ab <35°C HP -1/tic → Tod nach ~80 Ticks, ohne jede Gegenwehr.
```

Das ist keine Randnotiz, sondern eine **System-Schwäche**: Die Druck-Schraube existiert, aber es
gibt **keinen Hebel**. Konkret:

- `engine/components.py::get_total_insulation()` summiert `insulation` aller Items mit `CLOTHING`-Tag —
  aber **kein Item im Spiel trägt `CLOTHING`**. Die Isolation ist also dauerhaft 0. Der Test
  `test_components.py::test_total_insulation` konstruiert ein Fell (`Item(name="Fell", tags={"CLOTHING": True})`),
  das real nicht herstellbar ist.
- `fire_pit` (Template) trägt nur `KINDLING` — er **wärmt nicht**. `start_fire` erzeugt einen
  Inventar-Gegenstand, keine Wärmequelle an der Location.
- `cook_meat.required_tag_in_env: "HEAT_SOURCE"` (processes.json) ist **weich/nicht umgesetzt**
  (Kommentar in `execute_process`: "harte Standort-Gates folgen später"). Das System `required_tag_in_env`
  existiert als Feld, das nie greift.

**Warum das System-Tiefe vertieft (kein Metrik-Anker nötig):** Die Constitution will "Entdecken
vertieft statt abkürzt" und "Wachstum in Systemen, nicht nur in Inhalten". Hier gibt es eine ganze
Überlebens-Schicht (Kälte/Feuer/Wärme), die **kodiert, aber unspielbar** ist. Sie lebendig zu machen
gibt dem Spieler Entscheidungen — Feuer bauen, Brennstoff nachlegen, Schutz suchen — die über das
reine Kombinations-Crafting hinausgehen: ein Rast-/Wärmemanagement, das bestehende Items und
Prozesse (Feuer, Knochen, Fasern → Kleidung) mit neuem Zweck verknüpft. Kein einziger neuer
Content-Balloon, sondern tote Systemteile werden verdrahtet.

## Mechanik

Aus **The Long Dark** (Feuer + Brennstoff als zentrale Wärme-Druck-Schraube: ein Feuer brennt nur
so lange, wie man Holz nachlegt; Kälte ist ein Dauergegner, der Planung erzwingt) und
**UnReal World / Vintage Story** (Kleidung/Isolation als passive Gegenschicht: Rüstung gegen die
Umwelt, herstellbar aus Beute wie Fell; Feuer als aktive Wärmequelle am Standort).

Adaptierte Kernidee: **Ein aktives Feuer an der aktuellen Location hebt die effektive
Umgebungstemperatur** (bzw. senkt den Wärmeverlust), braucht aber **Brennstoff**, der über Zeit
verbrennt. Dazu **tragbare Isolation** (Kleidung aus vorhandenen Materialien), die den
Wärmeverlust dauerhaft senkt.

## Adaption (konkret für PPP)

Dateien: `engine/core.py`, `engine/components.py`, `data/items.json`, `data/processes.json`,
`data/blueprints.json`, `tests/test_engine.py`, `tests/test_components.py`.

1. **Location-Feuer-Zustand (`engine/components.py`):** `LocationDef` oder Engine erhält einen
   veränderlichen Feuerzustand pro Instanz (analog `ResourceNode.stock` — kein Cross-Session-Bleed):
   - `LocationDef.fire_active: bool = False`, `LocationDef.fire_fuel: float = 0.0`
     (Brennstoff in Ticks), `LocationDef.fire_heat: float` (Wärmebeitrag, aus dem `fire_pit`-Item
     bzw. unterstützend aus einem `HEAT_SOURCE`-Wert).
   - `engine/core.py::__init__`: frischer Zustand pro `LocationDef` (wie `_node_from_data`).

2. **Wärme-Ausgabe in der Thermodynamik (`engine/core.py::_advance_time`):** Vor der
   `temp_loss`-Berechnung die effektive Umgebungstemperatur anpassen:
   ```python
   ambient = self._get_ambient_temp()
   fire_warmth = 0.0
   if self.current_location.fire_active and self.current_location.fire_fuel > 0:
       fire_warmth = self.current_location.fire_heat
       self.current_location.fire_fuel -= ticks          # Brennstoff verbraucht sich
       if self.current_location.fire_fuel <= 0:
           self.current_location.fire_active = False     # Feuer erlischt
   effective_ambient = ambient + fire_warmth
   temp_loss = (self.player.body_temp - effective_ambient) * 0.01 * exposure \
               * (1.0 - min(0.9, insulation))
   ```
   Das aktive Feuer hebt die effektive Umgebung in Richtung Komfort → `temp_loss` sinkt/kehrt um,
   bevor die Unterkühlungs-Schwelle (35°C) erreicht wird. `insulation` kommt aus `get_total_insulation()`
   (unten).

3. **Feuer entzünden / nachlegen (`engine/core.py`):**
   - `_advance_time` verliert nach Erlöschen nie still — Log in `logs` (Reason `FIRE_OUT`,
     "Dein Feuer erlischt."), damit `feedback_quality`-Konsistenz getragen bleibt.
   - `execute_process("start_fire", ...)`: setzt zusätzlich den Location-Zustand
     `fire_active=True`, `fire_fuel = berechnet aus Inputs` (z.B. `stick`, `tinder`), damit das
     Feuer **an der Location** existiert, nicht nur als Inventar-Item.
   - Neue Methode `stoke_fire(item)` / CLI-Action `[w]ärmen` o.ä.: verbraucht einen Brennstoff-Item
     (Tag `KINDLING` oder `WOOD`), erhöht `fire_fuel`; nur möglich bei `fire_active`. Härter:
     ohne Feuer keine Wärme — man muss Holz sammeln und es nachlegen (Long-Dark-Zyklus).

4. **Tragbare Isolation — Kleidung herstellbar (`data/*`):**
   - Neues Template `fur_cloak` o.ä. (`data/items.json`) mit `CLOTHING`-Tag + `insulation`-Attribut,
     herstellbar über einen neuen Blueprint/Prozess aus vorhandenen Materialien (z.B. `bone`+`plant_fiber`
     oder Fell-aus-`raw_meat`-Quelle). Das verdrahtet den bereits getesteten, aber unerreichbaren
     `get_total_insulation()`-Pfad. **Achtung Dev-Pitfall:** neues Template/Blueprint verschiebt
     `len(items)`/`blueprint_reachability`-Denominatoren → `tests/test_loader.py` (harte Counts)
     und die Scorecard-Expecteds mitziehen; `content_reachable` muss 1.0 bleiben (Template existiert).

5. **`required_tag_in_env` hart machen (`engine/core.py::execute_process`):** Für `cook_meat`
   `HEAT_SOURCE` gegen den Location-Feuerzustand prüfen (aktives Feuer ⇒ `HEAT_SOURCE` vorhanden).
   Kocht erst, wenn ein Feuer brennt. Das aktiviert das tote `required_tag_in_env`-Feld.

6. **Constitution-Check:** kein Rezeptbuch (Feuerlogik ist Mechanik, keine Rezept-Liste; Kleidung
   folgt dem bestehenden Blueprint-Discovery-Prinzip), CLI-Text bleibt, stdlib only, keine Metrik
   entfernt/abgeschwächt (additiv). Vertieft Entdecken (Rast-/Wärmemanagement als neue
   Entscheidungsschicht) statt es abzukürzen. **Berührt keinen Metrik-Core** (`scorecard.py`/`METRICS`
   unangetastet) — anders als die Discovery-Specs braucht das keine tool-aware-reachability-Freigabe.

## Akzeptanzkriterien

- **Unterkühlung abwendbar:** Ein Spieler am `mountain_peak` bei STORM/Nacht mit aktivem Feuer
  verliert deutlich weniger / kein HP durch Unterkühlung; ohne Feuer stirbt er (Kontroll-Test).
- **Feuer brennt nur mit Brennstoff:** `fire_fuel` sinkt pro `_advance_time`; bei 0 erlischt das
  Feuer (`fire_active=False`) mit Meldung `FIRE_OUT` (Reason↔Label-Konsistenz-Test grün).
- **Nachlegen:** `stoke_fire`/CLI mit Brennstoff-Item erhöht `fire_fuel`; ohne aktives Feuer
  scheitert es ehrlich.
- **Isolation wirksam:** ein herstellbares `CLOTHING`-Item (z.B. Fell-Umhang) senkt den
  `temp_loss`; `get_total_insulation() > 0` bei Besitz. Test: `_advance_time` am kalten Ort mit
  Kleidung → geringerer HP-/Temp-Verlust als ohne.
- **`required_tag_in_env`:** `cook_meat` (HEAT_SOURCE) klappt nur bei aktivem Feuer an der Location;
  sonst ehrlicher Reason/Label.
- **Feedback-Labels:** neue Reasons (`FIRE_OUT`, ggf. `NO_FIRE`) haben Labels in `_feedback_message`;
  `feedback_quality`-Konsistenz bleibt grün.
- `content_reachable` bleibt 1.0 (neue Templates existieren real, keine dangling refs).
- `python -m pytest` bleibt grün (neue Tests: Feuer-Wärme-Kontrast, Brennstoff-Verbrauch/Erlöschen,
  Stoke, Isolation-Effekt, cook_meat-Gate; `test_loader.py`-Counts aktualisiert).

## Erwartete Metrik-Wirkung

- **`session_depth`:** Nebeneffekt leicht **steigend** — der Spieler hat nach der Discovery-Leere
  (alle Blueprints/Prozesse/Templates geleert, ~Aktion 28) ein neues, *fortlaufendes* Ziel
  (überleben: Feuer hüten, Holz nachlegen, Kleidung bauen). Das verschiebt den Stall-Punkt vom
  reinen Content-Ceiling zu einem Rast-Zyklus. Kein hartes Band versprochen.
- **`skill_spread`:** kann **steigen** — wer die Wärme-Mechanik beherrscht (Feuer+Kleidung)
  überlebt kalte Abschnitte länger → optimale Überlebensspanne wächst über die zufällige. Ehrlich
  als Möglichkeit notiert, nicht garantiert.
- **`feedback_quality`:** bleibt 1.0 (neue Reasons sind gelabelt).
- **Keine Metrik wird gesenkt/umdefiniert.** Das ist bewusst eine **System**-Mechanik: Ihr
  Primär-Beweis ist die neue Metrik (unten), nicht das Verschieben einer bestehenden.

## Hinweis an Direktor/Dev

Detail-Balance (Feuer-Heat-Werte, Brennstoffdauer, Kleidungs-Rezept) liegt bei Dev während der
Umsetzung. Der Spec legt das **System** fest: aktives Location-Feuer + Brennstoff-Entkopplung +
tragbare Isolation, die die bestehende, tote Thermodynamik zu einer spielbaren Gegenschicht macht.
Kein Metrik-Freigabe-Gate nötig (additiv, kein Metrik-Core).
