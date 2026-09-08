# SPEC-014 — Feuer-Wartung lesbar machen: Kälte- und Brennstoff-Signale

**Problem** (Metrik-Ebene: Play-Lesung 07.09., Befund 3 = BACKLOG 🔴 B10; betroffene
Metriken: warmth_stability / session_depth / skill_spread über die Profil-Tode): Alle
20 Lang-Runs des Menü-naiven Profils (200 Aktionen, 20 Seeds) sterben an Unterkühlung
(bt 3.7–23.3 am Ende, Energie 125–332, keine Wunden, kein Hunger) — 16/20 haben
`start_fire` entdeckt, alle sterben NEBEN tonnenweise sammelbarem Brennstoff. Ursache
ist nicht Balance, sondern Präsentation: `stoke_fire` ist als Wartungs-Verb unsichtbar —
kein Prozess (nicht im [p]-Menü), kein Eintrag in `PROCESS_HINT_CATEGORY`, kein
Blueprint, kein Knowledge-Panel-Eintrag; der einzige Kontakt ist das unkommentierte
Menü-Label `[w]ärmen`. Der Spieler lernt aus der Prozess-Ebene das Muster „Feuer =
einmal gelernter Prozess" und hat kein Muster für „Feuer braucht dauerhaftes Nachlegen".
Der Scorecard-Bot liest das nicht (er managt Wärme im guided-Stil — warmth_stability
0.46, p25=p75 flach); das Signal lebt in den Play-Profilen: der Menü-Spieler-Erschöpfungspunkt
(~110 Aktionen) wird nicht durch Discovery-Leere gekappt, sondern durch einen nicht
learnbaren Wartungs-Loop. Gleiche Signal-Klasse wie sharpen_tool 0/20 (13.08./04.09.):
Mechanik vorhanden, für Spieler praktisch unentdeckbar.

**Mechanik** (Quell-Spiele): The Long Dark — der Freezing-Status meldet sich deutlich
VOR dem lethal point und benennt die Gegenrichtung; Feuer-Wartung (Nachlegen) ist der
Kern-Survival-Loop, den das Spiel über Zustands-Signale beibringt, nicht über Rezepte.
(Im Repo bereits referenziert: BACKLOG ⚪ 01.08., „Kälte-/Condition-Survival mit
Temperatur-Druck".) Don't Starve — das Feuerobjekt selbst zeigt seinen Brennstoff-Zustand
(Flackern kurz vorm Erlöschen): die Wartungspflicht wird am Objekt sichtbar, BEVOR sie
tödlich wird. Gemeinsame Klasse: die Maintenance-Loop wird über crossing-basierte
Zustands-Meldungen learnbar gemacht — Richtung ja, Rezept nein. Der `stoke_fire`-Docstring
nennt den Zyklus längst „Long-Dark" — es fehlt nur die Sichtbarkeit.

**Adaption** (konkret, kein Daten-Touch, kein Reason-Code-Eingriff, KEINE neuen
RNG-Würfe — alle Meldungen sind Konstanten an bestehenden Crossing-Bedingungen, exakt
die Ziel-2-Klasse der Wear-Andeutung, core.py:419-425):

1. `engine/core.py`, Konstanten-Block bei `WEAR_HINT_TEXT`/`STOKE_FUEL` (~Zeile 49-91):
   NEU im selben Stil (Block-Kommentar: B10 / Ziel-3-Hebel, kein-Leak-Rationale):

   ```python
   COLD_WARN_THRESHOLD = 36.0   # 1° über der Schmerzgrenze 35.0 → Lead-Zeit
   COLD_HINT_TEXT = ("Die Kälte nagt. Ein Feuer würde hier Wärme geben.")
   FIRE_LOW_FUEL = 8.0          # weniger als ein Nachlegen (STOKE_FUEL) übrig
   FIRE_DYING_HINT_TEXT = ("Das Feuer wird schwach. Es ließe sich wohl "
                           "am Leben halten.")
   ```

2. `_advance_time` (engine/core.py:288-308), Feuer-Block: `prev_fuel` VOR dem
   Dekrement sichern, nach `fire_fuel -= ticks` (vor dem FIRE_OUT-Zweig):

   ```python
   if (loc.fire_active and prev_fuel >= FIRE_LOW_FUEL
           and loc.fire_fuel < FIRE_LOW_FUEL):
       logs.append(FIRE_DYING_HINT_TEXT)
   ```

   Das ist die Don't-Starve-Adaption: das Feuer selbst meldet seinen Zustand,
   ~8 Ticks vor FIRE_OUT (Lead-Zeit = FIRE_LOW_FUEL bei 1.0 Brennstoff/Tick).

3. `_advance_time`, Kälte-Block: `prev_bt` VOR der temp_loss-Update-Zeile sichern,
   nach der Aktualisierung (bei/nach den bestehenden bt-Auswirkungen):

   ```python
   if (not loc.fire_active and prev_bt >= COLD_WARN_THRESHOLD
           and self.player.body_temp < COLD_WARN_THRESHOLD
           and self.player.body_temp >= 35.0):
       logs.append(COLD_HINT_TEXT)
   ```

   Gate `not loc.fire_active`: der Text muss wahr sein — brennt Feuer und bt fällt
   trotzdem (Extrem-Kälte, 13.08.-Befund: Shelter-Klasse), spricht die
   Feuer-schwach-Meldung bzw. gar nichts, nicht eine Lüge. Guard `>= 35.0`: springt bt
   in einem Tick unter die Schmerzgrenze, spricht UNTERKÜHLUNG (kein Doppel).

   Beide Meldungen sind Kreuzungs-basiert wie die Wear-Warnung: einmal pro fallendem
   Durchgang (Kein Spam — Wiederholung erst nach Re-Wärmen/Neu-Auffüllen), plain
   Log-Zeile (kein !!!-Alarm — kein Schaden, ein Hinweis).

4. Bewusst NICHT gewählt (B10-Alternative „stoke_fire in die Prozess-Hinweise"):
   `take_process_hints` iteriert `self.processes` — stoke_fire ist dort nicht, und das
   Prozess-Schema (inputs als `template_id: quantity`) kann „irgendein WOOD/KINDLING-Item"
   nicht ausdrücken. Pseudo-Prozess = falsches Datenmodell. `stoke_fire` bleibt Verb.

5. Tests (TDD, Dev wählt Datei — Vorschlag `tests/test_cold_hints.py`): Crossing feuert
   einmal / kein Spam unterhalb bis Re-Warm / Fire-Gate (mit aktivem Feuer keine
   Kälte-Warnung) / Feuer-schwach feuert, FIRE_OUT nicht verdrängt / Leak-frei (exakter
   Text + Assert: kein template_id und kein Prozess-Name ist Substring der Texte).

**Akzeptanzkriterien** (jedes verifizierbar):
1. Konstanten exakt im Stil des WEAR_HINT_TEXT-Blocks (Kommentar: B10/Ziel-3, kein-Leak-Rationale).
2. Kälte-Warnung: genau am fallenden Crossing < 36.0, nur bei `not loc.fire_active`,
   einmal pro Durchgang, konstanter Text, kein RNG-Wurf (Wurf-Sequenz byte-identisch).
3. Feuer-schwach: am fallenden Crossing fire_fuel < 8.0 bei aktivem Feuer, einmal pro
   Durchgang, kein RNG; FIRE_OUT-Meldung unverändert.
4. Kein Leak: Texte nennen kein Item-Template, keine Menge, keine Prozess-ID
   (Vokabelklasse wie die Wear-Andeutung); Regressionstests.
5. compute_all()-Delta-Tabelle im JOURNAL: alle 12 Metriken **byte-identisch** auf den
   20 Scorecard-Seeds (keine neuen Würfe; Bots reagieren nicht auf Log-Zeilen —
   SPEC-012-Probe-Befund; es gibt keinen Grund für eine Verschiebung).
6. `feedback_quality` 1.0 unverändert; `EMITTABLE_REASONS` unangetastet (Log-Zeilen im
   _advance_time-Pfad, keine Experiment-Reasons).
7. pytest grün (Crossing-/No-Spam-/Fire-Gate-/Leak-Tests).
8. Play-Gegenprobe nach Landing: Profil C (oder etabliertes naive_menu-Profil) erneut —
   Kälte-Tode < 20/20 UND natürliche `[w]`-Nutzung in der Mehrzahl der Runs; Zielwert
   explorativ, kein harter Gate (kein Overfitting am Profil-Bot).
9. Kein Touch an `data/*.json`, `PROCESS_HINT_CATEGORY`, `tools/scorecard.py`;
   session_depth-Probe (endet 08.09., Direktor-Lesung) unberührt — keine Bot-Sequenz-Änderung.

**Erwartete Metrik-Wirkung** (Primär-Messung ist Play, nicht die Scorecard):
- Scorecard: alle 12 byte-identisch (Delta-Tabelle-Pflicht). warmth_stability bleibt
  bot-gelesen (guided-Stil managt Wärme) — die Änderung zielt auf die naive Menü-Realität;
  falls ein künftiges naives Mess-Profil Standard wird, fallen deren Tode, nicht der Wert.
- Play: Profil-C-Kälte-Tode 20/20 → deutlich weniger; FIRE_OUT→Nachlegen-Zyklen erscheinen;
  die Menü-Erschöpfung (~110) wird durch gelernte Wartung verlängert statt durch Tod gekappt.
- session_depth: keine Bot-Verhaltensänderung → kein Shift; Re-Baseline-Lesung ist
  Direktor-Sache (Probe-Ende 08.09.), hier nichts behaupten.
- discovery_gap: unberührt (kein Content, kein Kombinations-Hinweis).
- forage_pressure / gear_uptime (Probe bis 11.09.): unberührt — kein Sammel- oder
  Wear-Pfad angefasst; Meldungen würfeln nicht.

**Constitution-Check:** Tag-Crafting-Kern unangetastet; kein Rezeptbuch/Leak (die
Richtung benennt die Verb-Klasse, nicht Item/Menge/Prozess — der Spieler muss Brennstoff,
Werkzeug-Klasse und den Zünd-Pfad weiterhin selbst finden); stdlib only; keine Metrik
entfernt, umdefiniert oder abgeschwächt; das Entdecken wird vertieft — der Wartungs-Loop
wird als learnbares Objekt sichtbar, nicht abgekürzt. CLI-Text bleibt.
