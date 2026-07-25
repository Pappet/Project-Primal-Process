# Project Primal Process — Autonomous Work Plan

## Ziel
Ein tiefes, tag-basiertes Primitive-Technology-Discovery-Game. Vom Steinzeit-Überleben zur Eisenzeit-Zivilisation — durch Experimentieren, nicht durch Rezeptbuch.

## Arbeitsmodus
Cron-gesteuerte Sessions. Jede Session hat ein klares Ziel. Ergebnisse werden in diesem Repo dokumentiert.
Kein Overengineering — funktionierende Mechanik > perfekte Architektur. Playtestable builds bevorzugen.

---

## Phase 0: Foundation & Research (KW 30-31, 2026)

### [x] M0.1 — Repo-Analyse & Plan (heute)
Status: Done. ANALYSIS.md + PLAN.md erstellt.

### [ ] M0.2 — Research: Ähnliche Spiele analysieren
Ziel: Mechaniken aus 5-6 Referenzspielen extrahieren.
Referenzen:
- **UnReal World**: Deep Survival, realistische Körpersimulation, Jahreszeiten
- **Cataclysm: Dark Days Ahead**: Crafting-Tiefe, Komponenten-System
- **Ancestors: The Humankind Odyssey**: Primaten-Evolution, neuronales Entdeckungssystem
- **Neo Scavenger**: Survival-Flow, Condition-System, Crafting-als-Info
- **Don't Starve**: Technologie-Progression, Discovery durch Strukturen
- **Vintage Story**: Primitive Tech-Progression, Knapping-Mechanik, Töpferei
Output: RESEARCH.md mit extrahierten Mechaniken + Bewertung.

### [ ] M0.3 — Datenmodell refactorn
- JSON/YAML-basierte Daten statt hartkodierte Python-Dicts
- Item-Templates, Blueprints, Locations, Processes aus Dateien laden
- Validierung beim Laden

### [ ] M0.4 — Save/Load-System
- JSON-Serialisierung des GameState
- Save-Slots, Autosave

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

---

## Nächster Schritt (M0.2 Research)
Di 29.07.2026: Erste Research-Session — UnReal World + CDDA analysieren.