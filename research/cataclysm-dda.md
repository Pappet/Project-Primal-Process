# Cataclysm: Dark Days Ahead — 2026-07-28

> **Genre:** Survival Roguelike | **Setting:** Post-apokalyptisches New England | **Open Source seit:** 2013
> **Quellen:** Wikipedia, GitHub, JSON-Docs (CleverRaven/Cataclysm-DDA)

---

## Mechanik 1: Multi-Faktor-Crafting
- **Was:** Crafting erfordert gleichzeitig: (1) Rohmaterialien, (2) Equipment/Werkzeuge, (3) Skill-Level, (4) Proficiencies (spezifische Fertigkeiten), (5) Rezept-Wissen (aus Büchern), (6) äußere Bedingungen (Licht, flache Oberfläche, Werkbank, Moral, unverletzte Gliedmaßen).
- **Relevanz für PPP:** Das beste existierende Modell für Tag-basiertes Crafting. Statt einem simplen "Item A + Item B = Item C" hat CDDA ein Nested-Requirements-System: Recipes verweisen auf Requirements, Requirements auf Tool-Qualitäten und Komponenten-Gruppen. Für PPP: Blueprint-Conditions um `min_light_level`, `requires_workbench`, `requires_uninjured_hands` erweitern.
- **Umsetzbarkeit:** Mittel. Das jetzige Blueprint-System müsste um Conditions und Proficiencies erweitert werden. M1.3 plant das bereits an.

## Mechanik 2: Komponenten-basierte Fahrzeuge und Konstruktion
- **Was:** Fahrzeuge sind keine vorgefertigten Einheiten — sie bestehen aus Frames, Rädern, Motoren, Sitzen, Tanks, Waffen, Solarpanels etc. Alles einzeln platzierbar und zerstörbar. Gleiches Prinzip für Bau: von "Fenster vernageln" bis "Stahlbeton-Wand gießen".
- **Relevanz für PPP:** Ein Shelter ist kein vordefiniertes Item, sondern eine Komposition aus `WALL_WOOD`, `ROOF_THATCH`, `FIREPLACE_STONE`. Das ist radikal relevant für M2.2 (persistente Welt/Shelter). Jede Komponente hat eigene Tags und Zustände.
- **Umsetzbarkeit:** Schwer. Komponenten-System ist fundamental anders als das Item-System. Für Phase 2 einplanen, nicht jetzt.

## Mechanik 3: Proficiency-System (Skill-Subebene)
- **Was:** Neben generellen Skills (Fabrication, Survival, etc.) gibt es *Proficiencies*: `prof_carving`, `prof_welding`, `prof_fibers`. Proficiencies werden durch wiederholte Anwendung einer spezifischen Tätigkeit gelernt und reduzieren Crafting-Zeit drastisch. Sie sind das Bindeglied zwischen "kann ich generell" und "kann ich genau das".
- **Relevanz für PPP:** Genau das braucht das Discovery-System: Du entdeckst nicht einfach "Feuer machen", sondern baust Proficiency in `fire_bow_drill`, `tinder_preparation`, `fire_tending` auf. Wenn alle drei hoch genug sind, wird Feuer machen zuverlässig. Fehlschläge werden durch niedrige Proficiency erklärbar.
- **Umsetzbarkeit:** Einfach-Mittel. Ist im Kern ein `Dict[str, float]` auf dem Player. Integration in Blueprint-Conditions ist straightforward.

## Mechanik 4: Rezept-Erwerb durch Bücher (Gated Discovery)
- **Was:** Rezepte werden nicht automatisch freigeschaltet — sie müssen in Büchern gefunden werden. Bücher haben `required_intelligence` und `skill_level`-Anforderungen. Höhere Skill-Level erlauben das Verstehen komplexerer Rezepte. Ohne das richtige Buch: kein Rezept.
- **Relevanz für PPP:** Mäßig relevant. PPP will *Entdeckung durch Experimentieren*, nicht durch Lesen. Aber das Konzept "Rezept ist nicht automatisch bekannt" bleibt zentral. In PPP wäre das Pendant: Du kannst nur craften, was du durch vorherige Experimente entdeckt hast — ein `known_blueprints: set` auf dem Player.
- **Umsetzbarkeit:** Einfach. Ein `known_blueprints`-Set, das bei erfolgreichem Experimentieren befüllt wird.

## Mechanik 5: Farming mit realistischer Pflanzenphysiologie
- **Was:** Pflanzen haben Wachstumsraten, Temperaturabhängigkeit, Saisonalität (später Frühling bis früher Herbst), Dünger-Effekte, und yield skaliert mit Survival-Skill. Verschiedene Pflanzen wachsen unterschiedlich schnell. Geerntete Pflanzen sind "tot" und hinterlassen Stroh/welke Reste + Samen.
- **Relevanz für PPP:** Wenn PPP später Landwirtschaft bekommt (Phase 4), ist das das Referenzmodell: kein "pflanze Samen → warte 3 Tage → ernte", sondern `plant_growth_rate * temperature_modifier * fertilizer_bonus * skill_yield_multiplier`. Für jetzt: als Design-Vorlage notieren.
- **Umsetzbarkeit:** Schwer (Phase 4).

---

## Fazit
Top-3-Adaptionen für PPP:
1. **Nested Requirements System** → Blueprints mit Tool-Gruppen + Conditions (Licht, Werkbank, Körperzustand)
2. **Proficiency-System** → spezifische Fertigkeiten als Sub-Skills, gelernt durch Wiederholung, reduzieren Fehlschlag-Rate
3. **Known-Blueprints-Set** → Rezepte werden nicht geschenkt, sondern durch Experimentieren entdeckt