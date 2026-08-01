# Project Primal Process — Backlog

> Jede Session (Research, Dev, Review) schreibt hier rein, was ihr auffällt.
> Der Sunday Review räumt auf: promoten, verschieben, verwerfen.
> Format: `- [DATUM] (Quelle-Session) Beschreibung — einzeilig, konkret`
> Quelle-Session: Research, Dev, oder Review
> Keine Romane — das Ziel ist schnelle Triage am Sonntag.

---

## 🔴 Bugs
Dinge die kaputt sind und gefixt werden müssen.

> **Triage 2026-08-01:** Alle 5 🔴 Bugs → Sprint Tasks (KW 32) in PLAN.md promotet (je eigener Task, kein Bündeln). Nicht archivieren.

---

## 🟡 Ideas
Mechaniken, Features, Verbesserungen — nicht akut, aber wertvoll.

<!-- Session-Einträge hier drunter -->
- [2026-07-28] (Research) Body-Part-System: Lokalisierte Verletzungen pro Körperteil (URW-Referenz) — M2.4 Gesundheitssystem → **später (Phase 2)**
- [2026-07-28] (Research) Material-Quelle→Eigenschaften: Tags wie `BEAR_FUR`/`OAK_WOOD` als Qualitäts-Multiplikatoren (URW) — M1.1 Tag-Hierarchien → **nächste Woche (M1.1)**
- [2026-07-28] (Research) Skill→Qualität: Crafting-Skill modifiziert Output-Qualität, wächst auch bei Fehlschlag (URW) — M3.2 Skill-System → **später (Phase 3)**
- [2026-07-28] (Research) Multi-Faktor-Crafting: Blueprint-Conditions (Licht, Werkbank, Körperzustand, Moral) (CDDA) — M1.3 Blueprint-Upgrade → **nächste Woche (M1.3)**
- [2026-07-28] (Research) Proficiency-System: Spezifische Fertigkeiten (`prof_carving`) als Sub-Skills, gelernt durch Wiederholung (CDDA) — M3.1 Tech-Stufen → **später (Phase 3)**
- [2026-07-28] (Research) Known-Blueprints-Set: Rezepte müssen durch Experimentieren entdeckt werden (CDDA) — M3.1 Discovery-System → **später (Phase 3)**
- [2026-07-30] (Research) Tag-basierte Item-Substitution: Blueprints definieren Tag-Slots statt Item-IDs — z.B. `{head: [SHARP,STONE], handle: [LONG,RIGID]}`. Neo Scavenger beweist dass das funktioniert. — M1.2 + M1.3 → **nächste Woche (M1.2)**
- [2026-07-30] (Research) Neuronales Discovery-System: Blueprints durch wiederholte Experimente entdecken (nicht kaufen/finden). Reinforcement-Zähler pro Mechanik-Kategorie. — M3.1 → **später (Phase 3)**
- [2026-07-30] (Research) Condition-Web: HP/Energy ersetzen durch vernetzte Conditions (warmth, hydration, satiety, rest, health, morale) mit Kaskaden-Logik. Tod = Kaskade, nicht Einzelwert. — M2.4 → **später (Phase 2)**
- [2026-07-30] (Research) Biom-Vertrautheit (Fear/Dopamin): Unbekannte Biome lösen Debuff aus, erfolgreiche Aktionen bauen Familiarity auf. Kein Rush zu Endgame möglich. — M2.1 → **später (Phase 2)**
- [2026-07-30] (Research) Death-as-Legacy: Entdeckte Blueprints überleben Charakter-Tod. Inventar/Position geht verloren, Wissen bleibt. — M0.4 → **nächste Woche (M0.4)**
- [2026-07-30] (Research) Starting Scenarios: Spielstart mit permanenten Traits („Forest Child", „Coastal Wanderer"). Modifizieren Skill-Lernraten und Start-Bedingungen. — M3.2 → **später (Phase 3)**
- [2026-08-01] (QA) Crafting-Fehlschlag-Feedback: `"Nichts passiert."` uninformativ → konkreter Grund nennen (fehlende Tags, falsche Kombination, fehlendes Werkzeug). — M3.3 → **KW 33 (TASK-F01)**
- [2026-08-01] (QA) Energie-Balance: Drain aggressiv (10/gather), Start 800, keine Regeneration → Start 1000 + passive/Schlaf-Regeneration. Hypothermie-Warnung nur 1× pro Zustandsänderung. — M2.4 → **KW 33 (TASK-F02)**

---

## 🔵 Technical Debt
Code-Qualität, Architektur, Refactoring-Bedarf.

- [2026-07-27] (Dev) ~~`engine/crafting.py:create_dynamic_item` hardcoded auf `components["head"]`~~ — **✅ erledigt** in TASK-M03 (2026-07-29)
- [2026-07-29] (Dev) `data/processes.py` hat noch hartkodierte ProcessDefs — sollte analog zu items/blueprints/locations JSON-Loader bekommen → **Sprint KW 32 (TASK-R01)**
- [2026-07-29] (Dev) `engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — Fallback vorhanden aber inkonsistent mit fix in crafting.py. Sollte gleiche dynamische Slot-Erkennung verwenden → **nächste Woche (KW 33, TASK-R02)**

---

## ⚪ Research Leads
Spiele, Artikel, Mechaniken die man sich ansehen sollte.

<!-- Session-Einträge hier drunter -->
- [2026-08-01] (Review) **Valheim**: Boss-gated Biom-Progression + gestuftes primitives Crafting — Vorlage für Tech-Gating ohne Tech-Tree → M3.1
- [2026-08-01] (Review) **The Long Dark**: Kälte-/Condition-Survival mit Temperatur-Druck — Referenz für M2.4 Gesundheit & Start-Balance
- [2026-08-01] (Review) **Green Hell**: Body-Part-Schaden, Krankheiten, Erkundungs-UI ohne Minimap → M2.4/M3.3
- [2026-08-01] (Review) **Project Zomboid**: Tiefes Condition-/Crafting-/Konstruktions-System, persistente Welt → M2.2/M2.4
- [2026-08-01] (Review) **Dwarf Fortress**: Material-Komplexität, Crafting-Bäume, generierte Welt → M3.1/M4

---

## ✅ Triaged (diese Woche erledigt)
Vom Review aussortierte Einträge landen hier. Wird beim nächsten Review geleert.

<!-- Review räumt hier rein -->
- 🔴 5 Bugs → Sprint KW 32 (TASK-B01…B05), siehe PLAN.md
- 🔵 create_dynamic_item-Refactor → erledigt in TASK-M03
- 5 neue Research Leads → M0.2-Pipeline, siehe PLAN.md + ⚪ oben