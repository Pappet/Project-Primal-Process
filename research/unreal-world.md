# UnReal World — 2026-07-28

> **Genre:** Roguelike Survival | **Setting:** Eisenzeit-Finnland | **Entwickelt seit:** 1992
> **Quellen:** Wikipedia, offizielles Wiki (unrealworld.fi)

---

## Mechanik 1: Ganzkörper-Schadensmodell
- **Was:** Jeder Körperteil (Kopf, Arme, Beine, Torso) hat eigene Zustände. Frostbite, Wunden, Brüche werden pro Körperteil simuliert. Kleidung schützt pro bedecktem Körperteil.
- **Relevanz für PPP:** Lokalisierte Verletzungen statt globaler HP — ein gebrochener Arm verhindert beidhändiges Crafting, ein erfrorener Fuß verlangsamt Bewegung. Gibt physische Konsequenzen ohne abstrakte Werte.
- **Umsetzbarkeit:** Mittel. Braucht ein Body-Part-System mit Zuständen pro Part. Aber bereits das jetzige Tag-System (`body_part: hand`, `body_part: head`) könnte die Basis sein.

## Mechanik 2: Skill-basiertes Crafting mit Qualitätsstufen
- **Was:** 28 Skills (13 Crafting, 4 Physical, 11 Combat). Jeder Skill verbessert sich durch Nutzung — auch bei Fehlschlägen. Skills modifizieren die Qualität des Outputs (z.B. Hideworking → Fell-Qualität). Attribute beeinflussen Lernrate und Basiswert.
- **Relevanz für PPP:** Direkt adaptierbar: Ein `crafting_skill`-Tag auf Items, das die Qualität des Outputs bestimmt. Skill wächst durch Nutzung, nicht durch XP-Punkte. "Learning from failure" als Kernprinzip.
- **Umsetzbarkeit:** Einfach. Skill-System existiert konzeptionell schon in M3.2 — nur die Qualitätsmodulation muss ins Blueprint-System integriert werden.

## Mechanik 3: Material-Herkunft bestimmt Eigenschaften
- **Was:** Ein Fell vom Bären ist wärmer und schützender als ein Fuchsfell. Gleiches Tier → unterschiedliche Qualität je nach Hideworking-Skill. Die Herkunft des Materials (Tierart, Pflanzentyp) bestimmt die Basis-Werte, der Skill die finale Qualität.
- **Relevanz für PPP:** Tags wie `BEAR_FUR` vs `FOX_FUR` könnten unterschiedliche Basis-Attribute haben — gekoppelt mit dem Skill entsteht ein emergent vielfältiges System ohne hunderte harte Item-Templates.
- **Umsetzbarkeit:** Einfach. `material_source: bear` als Tag, Attribut-Multiplikatoren pro Quelle. Passt perfekt zum Tag-System.

## Mechanik 4: Jahreszeiten-getriebene Welt
- **Was:** Klimazyklus mit echten Konsequenzen: Pflanzen nur in bestimmten Monaten verfügbar, Gewässer frieren zu, Tiere migrieren. Überleben im Winter ist fundamental anders als im Sommer. Kleidung muss saisonal angepasst werden.
- **Relevanz für PPP:** Saisonale Availability-Tags auf Ressourcen und Prozessen. `available_in: [spring, summer]` auf Pflanzen, `process: hide_drying` nur bei `temperature > 5°C` oder in der Nähe von Feuer.
- **Umsetzbarkeit:** Mittel. Braucht ein Kalender-/Klimasystem. M2.1 hat saisonale Änderungen geplant — das hier ist die Mechanik dahinter.

## Mechanik 5: Selbstversorger-Ökonomie (kein Geld)
- **Was:** Kein Geldsystem. Tauschhandel mit Dorfbewohnern. Der Fokus liegt auf Selbstversorgung: jagen, sammeln, bauen, kleidung herstellen. Fortschritt kommt durch eigene Produktion, nicht durch Kauf.
- **Relevanz für PPP:** Kein Shop-System. Fortschritt durch Entdeckung und Eigenproduktion, nicht durch Händler. Das passt zur "Discovery by doing"-Philosophie. Trading kann optionaler Tausch sein, nie zentral.
- **Umsetzbarkeit:** Einfach (weglassen). Kein Economy-System bauen, sondern Item-getriebene Progression.

---

## Fazit
Top-3-Adaptionen für PPP:
1. **Body-Part-Schaden** → lokalisierte Konsequenzen statt globaler HP (macht Survival greifbar)
2. **Material-Herkunft → Eigenschaften** → emergente Item-Vielfalt durch Quell-Tags
3. **Skill-durch-Nutzung mit Qualitätsoutput** → natürliche Progression ohne Tech-Tree