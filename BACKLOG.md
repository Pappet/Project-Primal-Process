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