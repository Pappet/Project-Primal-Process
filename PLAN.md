# Project Primal Process — Autonomous Work Plan

## Ziel
Ein tiefes, tag-basiertes Primitive-Technology-Discovery-Game. Vom Steinzeit-Überleben zur Eisenzeit-Zivilisation — durch Experimentieren, nicht durch Rezeptbuch.

## Arbeitsmodus
Cron-gesteuerte Sessions. Jede Session hat ein klares Ziel. Ergebnisse werden in diesem Repo dokumentiert.
Kein Overengineering — funktionierende Mechanik > perfekte Architektur. Playtestable builds bevorzugen.

---

## Phase 0: Foundation & Research (KW 30-33, 2026)

> Marker: `[ ]` = offen, `[~]` = in Arbeit, `[x]` = erledigt

### [x] M0.1 — Repo-Analyse & Plan
Status: Done. ANALYSIS.md + PLAN.md erstellt.

### [ ] M0.2 — Research: 6 Referenzspiele analysieren (2 pro Session)
Output: `research/*.md` + `research/INDEX.md` mit Takeaways.
- **UnReal World**: Deep Survival, realistische Körpersimulation, Jahreszeiten
- **Cataclysm: Dark Days Ahead**: Crafting-Tiefe, Komponenten-System
- **Ancestors: The Humankind Odyssey**: Primaten-Evolution, neuronales Entdeckungssystem
- **Neo Scavenger**: Survival-Flow, Condition-System, Crafting-als-Info
- **Don't Starve**: Technologie-Progression, Discovery durch Strukturen
- **Vintage Story**: Primitive Tech-Progression, Knapping-Mechanik, Töpferei

### [ ] M0.2b — pytest-Grundgerüst + Smoke-Tests
- `tests/`-Ordner mit pytest-Setup
- Smoke-Tests für Crafting-Kern (Blueprint-Matching, Item-Tags)
- `python -m pytest` muss laufen
- Wichtig VOR M0.3 (Refactor ohne Tests = gefährlich)

### [ ] M0.3 — Datenmodell refactorn
- JSON/YAML-basierte Daten statt hartkodierte Python-Dicts
- Item-Templates, Blueprints, Locations, Processes aus Dateien laden
- Validierung beim Laden
- Tests müssen grün bleiben

### [ ] M0.4 — Save/Load-System
- JSON-Serialisierung des GameState
- Save-Slots, Autosave
- Roundtrip-Test: save → load → state identisch

---

## Phase 1: Core Expansion (KW 32-34)

### [ ] M1.1 — Erweitertes Tag-System
- Tag-Hierarchien (SHARP → CUTTING, PIERCING)
- Material-Tags (STONE, WOOD, BONE) zusätzlich zu Funktions-Tags
- Qualitäts-Modifier auf Tags

### [ ] M1.2 — Item-Content ×5
- Von 8 auf 40+ Item-Templates
- Kategorien: Rohstoffe, Werkzeuge, Baumaterial, Nahrung, Kleidung, Medizin
- Jedes Item mit vollständigen Tags + Attributes

### [ ] M1.3 — Blueprint-System Upgrade
- Bedingungen über Tags hinaus: min_item_quality, required_skill_level
- Feste (bekannte) + emergente Blueprints
- Blueprint-Familien (z.B. alle Axt-Varianten als Familie)

### [ ] M1.4 — Prozess-System aktivieren
Das existierende process.py ist nicht eingebunden. Prozesse sind anders als Blueprints:
- Blueprint = Kombiniere X+Y+Z → neues Item
- Process = Transformiere X mit Tool Y in Umgebung Z → neues Item  
Implementieren: Prozesse als Aktionen (trocknen, kochen, brennen, fermentieren)

---

## Phase 2: World & Threats (KW 35-37)

### [ ] M2.1 — Erweiterte Weltkarte
- 10-15 Locations mit Biome-Typen
- Reisezeit, Gefahren auf Reisen
- Saisonale Änderungen (nicht nur Wetter)

### [ ] M2.2 — Persistente Welt
- Shelter bauen (Zustand über Sessions)
- Feuerstellen, Vorratslager, Werkbänke
- Gelände veränderbar

### [ ] M2.3 — Gefahren-System
- Raubtiere (Verhalten, nicht nur HP-Kampf)
- Krankheiten/Infektionen (von rohem Fleisch, Wunden)
- Wetterextreme (Blitzschlag, Überschwemmung)
- Verletzungen (Knochenbrüche, Schnitte)

### [ ] M2.4 — Gesundheitssystem
- Mehrere Vitalwerte (nicht nur HP/Energy)
- Wunden, Narben, Immunsystem
- Erste Hilfe aus Pflanzen

---

## Phase 3: Progression & Discovery (KW 38-41)

### [ ] M3.1 — Tech-Stufen-System
- Implizite Progression durch Tag-Komplexität
- Kein Tech-Tree — Entdeckung durch Verfügbarkeit neuer Tags
- "Aha-Momente" designen: z.B. erstes Mal Feuer → neue Tag-Welt öffnet sich

### [ ] M3.2 — Skill-System
- Skills entwickeln sich durch Nutzung
- Perception, Crafting, Combat, Foraging, Building
- Skills gaten Zugang zu komplexeren Blueprints

### [ ] M3.3 — UI/UX Upgrade
- Text UI mit Rich/Layout (Farben, Panels)
- Besseres Feedback bei Experimenten
- Discovery-Log (was wurde wann entdeckt)
- Tooltips für Tags

### [ ] M3.4 — Erste spielbare Alpha
- 40+ Items, 15+ Blueprints, funktionierende Prozesse
- Save/Load, erweiterte Welt
- Genug Tiefe für 2-3 Stunden Gameplay

---

## Phase 4: Depth & Polish (offen)

### Vision-Features
- **NPCs/Tribe**: Vom Einzelspieler zum Stamm
- **Generierte Welt**: Prozedurale Karte
- **Metallurgie**: Vollständige Kette Erz→Barren→Werkzeug
- **Landwirtschaft**: Domestizierung von Pflanzen/Tieren
- **Architektur**: Mehr als nur Shelter
- **Kulturelle Evolution**: Sprache, Kunst, Rituale

---

## Cron-Job-Struktur

| Job | Frequenz | Aufgabe |
|-----|----------|---------|
| primal-research | 2×/Woche (Di+Do 10:00) | Game-Analyse, Mechanik-Recherche |
| primal-dev | 3×/Woche (Mo+Mi+Fr 14:00) | Implementierung nächster Task |
| primal-review | 1×/Woche (So 18:00) | Fortschritts-Review, Plan-Update |

Outputs landen in ~/projects/primal-process/ und im Discord #general.

**Dokumente:**
| Datei | Zweck |
|-------|-------|
| `PLAN.md` | Roadmap, Milestones, Fortschritt |
| `ANALYSIS.md` | Codebase-Analyse, Architektur |
| `RESEARCH.md` | Forschungs-Zusammenfassung (nach Phase 0) |
| `research/*.md` | Einzelne Spiel-Analysen |
| `research/INDEX.md` | Destillierte Takeaways pro Spiel |
| `JOURNAL.md` | Chronologisches Session-Tagebuch (letzte 4 Wochen) |
| `archive/` | Archivierte alte Journal-Einträge |
| `BACKLOG.md` | Bugs, Ideen, Tech Debt — jede Session schreibt rein, Review triagiert |

---

## Nächste Schritte
- **Mo 27.07. 14:00** — Dev: M0.2b (pytest-Grundgerüst)
- **Di 28.07. 10:00** — Research: UnReal World + CDDA