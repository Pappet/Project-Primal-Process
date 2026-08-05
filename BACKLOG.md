# Project Primal Process — Backlog

> Jede Session (Research, Dev, Review) schreibt hier rein, was ihr auffällt.
> Der Direktor (So) räumt auf: zu Specs machen, verschieben, verwerfen.
> Format: `- [DATUM] (Quelle-Session) Beschreibung — einzeilig, konkret`
> Quelle-Session: Research, Dev, Play, oder Direktor
> Keine Romane — das Ziel ist schnelle Triage am Sonntag.

---

## 🗂 Rohmaterial (aus altem Plan, 2026-08-03, Umbau)
> Frühere Milestones M0.4–M3.4. Als Ideen, nicht als Struktur. Konvertiert der Direktor/Research gezielt in Specs, wenn die Metriken es verlangen.
- [2026-08-03] (Umbau) Save/Load-System: JSON-Serialisierung des GameState + Save-Slots + Autosave (war M0.4) — `session_depth`/Langzeit-Tiefe
- [2026-08-03] (Umbau) Erweitertes Tag-System: Tag-Hierarchien (SHARP→CUTTING/PIERCING), Material-Tags, Qualitäts-Modifier (war M1.1) — craft_variety
- [2026-08-03] (Umbau) Item-Content ×5: von 8 auf 40+ Templates, Kategorien Rohstoffe/Werkzeuge/Baumaterial/Nahrung/Kleidung/Medizin (war M1.2) — content_reachable
- [2026-08-03] (Umbau) Blueprint-Conditions: min_item_quality, required_skill_level, Blueprint-Familien (war M1.3) — craft_variety
- [2026-08-03] (Umbau) Erweiterte Weltkarte: 10–15 Locations, Reisezeit, Gefahren, saisonale Änderungen (war M2.1) — session_depth
- [2026-08-03] (Umbau) Persistente Welt: Shelter/Feuerstellen/Werkbänke bauen, Gelände veränderbar (war M2.2) — session_depth
- [2026-08-03] (Umbau) Gefahren-System: Raubtiere, Krankheiten, Wetterextreme, Verletzungen (war M2.3) — skill_spread
- [2026-08-03] (Umbau) Gesundheitssystem: mehrere Vitalwerte, Wunden, Immunsystem, Erste Hilfe (war M2.4) — skill_spread
- [2026-08-03] (Umbau) Tech-Stufen: implizite Progression über Tag-Komplexität, keine Tech-Tree, Aha-Momente (war M3.1) — session_depth
- [2026-08-03] (Umbau) Skill-System: Skills durch Nutzung, gaten komplexere Blueprints (war M3.2) — skill_spread
- [2026-08-03] (Umbau) UI/UX-Upgrade: besseres Feedback, Discovery-Log, Tooltips für Tags (war M3.3) — feedback_quality
- [2026-08-03] (Umbau) Spielbare Alpha: 40+ Items, 15+ Blueprints, funktionierende Prozesse (war M3.4) — Gesamtziel

---


## 🔴 Bugs
Dinge die kaputt sind und gefixt werden müssen.

> **Triage 2026-08-01:** Alle 5 🔴 Bugs → Sprint Tasks (KW 32) in PLAN.md promotet (je eigener Task, kein Bündeln). Nicht archivieren.
>
> **Triage 2026-08-02:** Keine neuen Bugs seit 01.08. — 5/5 unverändert im KW-32-Sprint (B01–B05). Bestätigt.
>
> **Triage 2026-08-03:** Alle 5 🔴 Bugs (B01–B05) in der Dev-Session vom 03.08. gefixt (siehe PLAN.md). Zu archivieren beim nächsten Review.
>
> **Triage 2026-08-05:** 2 neue 🔴 Bugs (B06–B07) aus Play-Session — beide gefühlt [Play]. Nicht gebündelt.

---

### 🔴 B06 — `log_oak` liefert "Unbekannt" (dangling Node-Template)
- [2026-08-05] (Play) **`log_oak`-Node (forest_edge, braucht CHOPPING/Axt) referenziert ein Template, das es in `items.json` nicht gibt.** Mit der frisch gebauten Axt Holz fällen → `Gefunden: 1x Unbekannt` (Müll-Item ohne Nutzen). Kernversprechen "Axt bauen, um Holz zu sammeln" bricht in der Hand. **Fix-Richtung:** `log_oak` als echtes Template anlegen oder aus dem Node entfernen.

### 🔴 B07 — `clay_lump` doppelt tot (fehlendes Werkzeug + fehlendes Template)
- [2026-08-05] (Play) **`clay_lump`-Node (hidden_cave, braucht `SHOVEL`)**: kein Item trägt das Tag `SHOVEL` → unerreichbar; zusätzlich fehlt das Template in `items.json`. Doppelt toter Content-Pfad. **Fix-Richtung:** SHOVEL-Werkzeug (z.B. Axt/Stab als Grabwerkzeug) einführen und Template anlegen, oder Node entfernen.

---

## 🟡 Ideas
Mechaniken, Features, Verbesserungen — nicht akut, aber wertvoll.

<!-- Session-Einträge hier drunter -->
- [2026-08-05] (Play) **`content_reachable` blind gegen dangling Node-Referenzen** — zählt nur TEMPLATE_DB-Keys, verpasst Nodes auf nicht-definierte Templates (`log_oak`, `clay_lump` → B06/B07). **Metrik-Änderung → braucht Peters Freigabe** (Constitution). Vorschlag: auch Nodes prüfen, deren `result_template_id` nicht in der DB existiert (würde beide Bugs sofort als Defizit sichtbar machen).
- [2026-08-05] (Play) **Craft-Bottleneck: beide Blueprints brauchen `HARD`/`SHARP`, das nur `flint_shard` trägt** — `pebble` ist STONE/PROJECTILE, nicht HARD → jeder Tool-Pfad funnelt durch den mountain_peak, ohne Leitfaden dorthin. Naive Spieler ohne flint → 0 Werkzeuge, Frust. Idee: mehr HARD/SHARP-Quellen (Knapping als handwerklicher Prozess, harter Splitter/Holz) oder `pebble` HARD geben. → trifft `discovery_gap`/`session_depth`.
- [2026-08-05] (Play) **SPEC-003-Konflikt:** `discovery_gap` ist bereits 0.25 (untere Bandkante) und `naive_p25` 0.0→0.5 — beide Effekte, die SPEC-003 liefern sollte (Gap senken, Schwanz schließen), sind **ohne** SPEC-003 schon eingetreten (von SPEC-001/Content). Setzt SPEC-003 jetzt um, droht die Gap unter 0.2 (Überführung). Vor Umsetzung neu prüfen, ob/mit welcher Kraft SPEC-003 noch gebraucht wird. → an Direktor (Plan-Neufassung So).
- [2026-08-04] (Dev) **`craft_variety` zählt Prozesse noch nicht.** Der naive Play-Bot ruft nur `execute_experiment`, nie `execute_process` → das neue Prozess-System (SPEC-001) bleibt für die Metrik unsichtbar. Prozesse als Craft-Typ zählen = Umdefinition der Metrik → **braucht Peters Freigabe** (Constitution). Dev hat Spielseite gebaut, Metrik absichtlich NICHT angefasst.
- [2026-08-03] (Direktor) **Lern-Signal messen**: steigt die Trefferquote eines naiven Spielers nach einer informativen Fehlermeldung? Misst, ob der Spieler das Feedback *versteht* — im Gegensatz zu `feedback_quality`, das nur die Konsistenz zwischen Reason-Code und Meldung prüft und konstruktionsbedingt bei 1.0 steht. **Option für den Explore-Job, kein Auftrag** — der wählt sein Thema selbst.
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
- [2026-08-01] (QA) Crafting-Fehlschlag-Feedback: `"Nichts passiert."` uninformativ → konkreter Grund nennen (fehlende Tags, falsche Kombination, fehlendes Werkzeug). — M3.3 → **KW 32 (TASK-F01)** *(Korr. 03.08.: zurückgeholt aus KW 33, füllt Do-Slot)*
- [2026-08-01] (QA) Energie-Balance: Drain aggressiv (10/gather), Start 800, keine Regeneration → Start 1000 + passive/Schlaf-Regeneration. Hypothermie-Warnung nur 1× pro Zustandsänderung. — M2.4 → **KW 32 (TASK-F02)** *(Korr. 03.08.: zurückgeholt aus KW 33, füllt Fr-Slot)*

---

## 🔵 Technical Debt
Code-Qualität, Architektur, Refactoring-Bedarf.

- [2026-07-27] (Dev) ~~`engine/crafting.py:create_dynamic_item` hardcoded auf `components["head"]`~~ — **✅ erledigt** in TASK-M03 (2026-07-29)
- [2026-07-29] (Dev) ~~`data/processes.py` hat noch hartkodierte ProcessDefs — sollte analog zu items/blueprints/locations JSON-Loader bekommen~~ — **✅ erledigt** in TASK-R01 (2026-08-03)
- [2026-07-29] (Dev) `engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — Fallback vorhanden aber inkonsistent mit fix in crafting.py. Sollte gleiche dynamische Slot-Erkennung verwenden → **KW 32 (TASK-R02)** *(Korr. 03.08.: aus KW 33 zurückgeholt, füllt Mi-Slot)*

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
- *(2026-08-02)* Keine neuen Archiveinträge — alles Backlog trägt bereits Sprint-/Phase-Ziel