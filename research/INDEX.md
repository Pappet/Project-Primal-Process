# Research Index — Project Primal Process

> Destillierte Takeaways aus analysierten Referenzspielen.
> Jede Research-Session (2 Spiele) schreibt hier ihre Funde rein.

---

## Analysierte Spiele

### UnReal World (2026-07-28)
- **Body-Part-Schaden:** Lokalisierte Verletzungen (Frostbite pro Körperteil) statt globaler HP — macht Survival physisch greifbar
- **Material-Herkunft → Eigenschaften:** Bärenfell > Fuchsfell — Tags wie `BEAR_FUR` als Qualitäts-Multiplikatoren, emergente Vielfalt ohne Template-Explosion
- **Skill-durch-Nutzung:** 28 Skills wachsen durch Ausführung (auch bei Fehlschlag), modifizieren Output-Qualität, Hardcap bei 95%

### Cataclysm: Dark Days Ahead (2026-07-28)
- **Nested Requirements:** Crafting braucht Rohstoffe + Tools + Skill + Proficiencies + Rezeptwissen + Umweltbedingungen (Licht, Werkbank) — das Multi-Faktor-Modell für PPP-Blueprints
- **Proficiency-System:** Spezifische Fertigkeiten (`prof_carving`) separat von generellen Skills, gelernt durch Wiederholung, reduzieren Fehlschlag-Rate
- **Known-Blueprints-Set:** Rezepte werden nicht geschenkt, sondern durch Experimentieren/Finden entdeckt — `known_blueprints: set` auf dem Player

### Ancestors: The Humankind Odyssey (2026-07-30)
- **Neuronales Entdeckungssystem:** Fähigkeiten werden durch Handlungen entdeckt und verstärkt, nicht durch Punkte gekauft — verstärkte Neuronen vererben sich auf nächste Generation
- **Angst/Dopamin-Pacing:** Unbekannte Biome lösen Fear aus, erfolgreiche Aktionen bauen Dopamin auf — natürliches Pacing ohne künstliche Gates
- **Sensorische Discovery-UI:** Keine Minimap, keine Marker — Intelligenz und Sinne ersetzen das HUD, Objekte müssen erst identifiziert werden

### Neo Scavenger (2026-07-30)
- **Substitutions-Crafting:** Rezepte definieren Kategorien (CONTAINER, SHARP), nicht Item-IDs — beweist dass Tag-basiertes Crafting im Survival-Genre funktioniert
- **Condition-Web:** Nicht HP/Energy, sondern Multi-Condition-Metabolismus (Hunger, Durst, Fatigue, Hypothermie, Krankheit, Schmerz) mit Kaskaden-Interaktionen
- **Permadeath + Spieler-Progression:** Kein XP, kein Leveling — Fortschritt ist ausschließlich Spieler-Wissen, der beste Beweis für PPPs Discovery-Philosophie

---

## Querverweise

| Mechanik | Spiele | PPP-Relevanz |
|----------|--------|--------------|
| Body-Part-Schaden | URW | M2.4 Gesundheitssystem |
| Material-Herkunft | URW | M1.1 Tag-Hierarchien |
| Skill-Qualitäts-Modulation | URW | M3.2 Skill-System |
| Multi-Faktor-Crafting | CDDA | M1.3 Blueprint-Upgrade |
| Proficiency/Sub-Skills | CDDA | M3.1 Tech-Stufen |
| Known Blueprints | CDDA | M3.1 Discovery-System |
| Komponenten-Konstruktion | CDDA | M2.2 Persistente Welt |
| Neuronale Entdeckung | Ancestors | M3.1 Discovery-System |
| Angst/Dopamin-Pacing | Ancestors | M2.1 Weltkarte |
| Sensorische Discovery-UI | Ancestors | M3.3 UI/UX |
| Tag-Substitution-Crafting | Neo Scavenger | M1.2 Item-Content, Kernsystem |
| Condition-Web | Neo Scavenger | M2.4 Gesundheitssystem |
| Spieler-Progression (kein XP) | Neo Scavenger | M3.1 Discovery, Kernphilosophie |

---

*Stand: 2026-07-30 — 4/6 Spiele analysiert. Nächste Session: Don't Starve + Vintage Story.*