# Project Primal Process — Backlog

> Jede Session (Research, Dev, Review) schreibt hier rein, was ihr auffällt.
> Der Sunday Review räumt auf: promoten, verschieben, verwerfen.
> Format: `- [DATUM] (Quelle-Session) Beschreibung — einzeilig, konkret`
> Quelle-Session: Research, Dev, oder Review
> Keine Romane — das Ziel ist schnelle Triage am Sonntag.

---

## 🔴 Bugs
Dinge die kaputt sind und gefixt werden müssen.

<!-- Session-Einträge hier drunter -->
- [2026-08-01] (QA) 🔴 plant_fiber und reeds in keiner Location — kein FIBER/RIGID-FIBER droppbar, beide Blueprints uncraftbar → M1.2 Content
- [2026-08-01] (QA) 🔴 pebble-Template fehlt in items.json — mountain_peak-Node referenziert nicht existierendes Template, Spieler sammelt "Unbekannt" → M1.2 Content
- [2026-08-01] (QA) 🔴 Perception-Startwert (1.0) zu niedrig — flint_shard (1.5), berries (2.0), mushroom (2.0) alle unerreichbar → M2.1/M3.2 Balancing
- [2026-08-01] (QA) 🔴 Condition=0 Items craftbar — kaputte Items ergeben Werkzeug mit condition=1.0, Exploit → M0.3/M1.3
- [2026-08-01] (QA) 🔴 Spieler startet bei Nacht (tick_counter=0 → hour=0 → night_mod=-10) — effektive Starttemp 5°C statt 15°C, Hypothermie fast instant → M2.4

---

## 🟡 Ideas
Mechaniken, Features, Verbesserungen — nicht akut, aber wertvoll.

<!-- Session-Einträge hier drunter -->
- [2026-07-28] (Research) Body-Part-System: Lokalisierte Verletzungen pro Körperteil (URW-Referenz) — M2.4 Gesundheitssystem
- [2026-07-28] (Research) Material-Quelle→Eigenschaften: Tags wie `BEAR_FUR`/`OAK_WOOD` als Qualitäts-Multiplikatoren (URW) — M1.1 Tag-Hierarchien
- [2026-07-28] (Research) Skill→Qualität: Crafting-Skill modifiziert Output-Qualität, wächst auch bei Fehlschlag (URW) — M3.2 Skill-System
- [2026-07-28] (Research) Multi-Faktor-Crafting: Blueprint-Conditions (Licht, Werkbank, Körperzustand, Moral) (CDDA) — M1.3 Blueprint-Upgrade
- [2026-07-28] (Research) Proficiency-System: Spezifische Fertigkeiten (`prof_carving`) als Sub-Skills, gelernt durch Wiederholung (CDDA) — M3.1 Tech-Stufen
- [2026-07-28] (Research) Known-Blueprints-Set: Rezepte müssen durch Experimentieren entdeckt werden (CDDA) — M3.1 Discovery-System
- [2026-07-30] (Research) Tag-basierte Item-Substitution: Blueprints definieren Tag-Slots statt Item-IDs — z.B. `{head: [SHARP,STONE], handle: [LONG,RIGID]}`. Neo Scavenger beweist dass das funktioniert. — M1.2 + M1.3
- [2026-07-30] (Research) Neuronales Discovery-System: Blueprints durch wiederholte Experimente entdecken (nicht kaufen/finden). Reinforcement-Zähler pro Mechanik-Kategorie. — M3.1
- [2026-07-30] (Research) Condition-Web: HP/Energy ersetzen durch vernetzte Conditions (warmth, hydration, satiety, rest, health, morale) mit Kaskaden-Logik. Tod = Kaskade, nicht Einzelwert. — M2.4
- [2026-07-30] (Research) Biom-Vertrautheit (Fear/Dopamin): Unbekannte Biome lösen Debuff aus, erfolgreiche Aktionen bauen Familiarity auf. Kein Rush zu Endgame möglich. — M2.1
- [2026-07-30] (Research) Death-as-Legacy: Entdeckte Blueprints überleben Charakter-Tod. Inventar/Position geht verloren, Wissen bleibt. — M0.4
- [2026-07-30] (Research) Starting Scenarios: Spielstart mit permanenten Traits („Forest Child", „Coastal Wanderer"). Modifizieren Skill-Lernraten und Start-Bedingungen. — M3.2

---

## 🔵 Technical Debt
Code-Qualität, Architektur, Refactoring-Bedarf.

- [2026-07-27] (Dev) `engine/crafting.py:create_dynamic_item` hardcoded auf `components["head"]` — crasht bei Blueprints ohne "head"-Slot. M0.3 beheben.
- [2026-07-29] (Dev) `data/processes.py` hat noch hartkodierte ProcessDefs — sollte analog zu items/blueprints/locations JSON-Loader bekommen
- [2026-07-29] (Dev) `engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — Fallback vorhanden aber inkonsistent mit fix in crafting.py. Sollte gleiche dynamische Slot-Erkennung verwenden

---

## ⚪ Research Leads
Spiele, Artikel, Mechaniken die man sich ansehen sollte.

<!-- Session-Einträge hier drunter -->

---

## ✅ Triaged (diese Woche erledigt)
Vom Review aussortierte Einträge landen hier. Wird beim nächsten Review geleert.

<!-- Review räumt hier rein -->