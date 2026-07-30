# Neo Scavenger — Research Notes

> Blue Bottle Games, 2014. Post-apokalyptisches Survival, Single-Player.
> Turn-basiert, hex-basierte Weltkarte, Permadeath. Michigan, Near-Future.
> Analysiert: 2026-07-30

---

## 5 Kernmechaniken

### 1. Permadeath mit Spieler-Progression (No XP, No Grind)

**Wie es funktioniert:** Es gibt keine Erfahrungspunkte. Kein Leveling. Kein „Grinden" für Stats. Der Fortschritt kommt ausschließlich vom *Spieler*, der das Spiel besser versteht. Stirbt der Charakter → Save wird gelöscht. Punkt. Aber der Spieler weiß beim nächsten Run mehr — das ist die eigentliche Progression.

**Konkretes Beispiel:**
- Run 1: Spieler isst unbekannte Beeren → vergiftet → stirbt
- Run 2: Spieler weiß: „Blaue Beeren = tödlich, rote = essbar"
- Run 3: Spieler weiß: „Mit Botany-Skill kann ich Beeren identifizieren"
- Kein Charakter-Wert hat sich geändert — nur das Wissen des Spielers

**Warum relevant für PPP:** Das ist die philosophische Grundlage für PPPs Discovery-System. Wissen = Progression. Der Spieler entdeckt Mechaniken, nicht der Charakter skillt auf. PPPs Tag-System muss dieses „Aha"-Gefühl replizieren: „Ah, SHARP + WOOD = Werkzeug" ist die Belohnung, nicht eine Level-Up-Animation.

### 2. Fähigkeiten & Makel (Abilities & Flaws)

**Wie es funktioniert:** Bei Charaktererstellung wählt der Spieler Fähigkeiten und Makel — permanente Eigenschaften, die den gesamten Run definieren. Kombinationen schalten einzigartige Optionen und Quest-Zweige frei. Kein „später umskillen" möglich.

**Konkretes Beispiel:**
- Wählt „Botany" + „Trapping" → Kann Pflanzen identifizieren UND Fallen bauen → starker Forager-Build
- Wählt „Hacking" + „Lockpicking" → Kann Laptops/Datapads knacken → Story-Fortschritt durch Datenfunde
- Wählt „Myopia" (Kurzsichtigkeit) als Makel → Sieht keine Details auf Distanz → andere Spielerfahrung
- Wählt „Insomniac" → Braucht weniger Schlaf, aber Fatigue baut sich schneller auf

**Warum relevant für PPP:** Startbedingungen als Replayability-Multiplikator. PPP könnte Runs variieren durch: Start-Biom (Wald vs. Steppe vs. Küste), Start-Saison (Winter härter), Tribe-Größe (solo vs. kleine Gruppe). Jede Kombination = andere optimale Strategie.

### 3. Multi-Condition-Metabolismus

**Wie es funktioniert:** Nicht nur HP und Energy. Der Charakter hat einen komplexen Zustands-Vektor. Jede Condition tickt pro Runde, jede hat eigene Konsequenzen, und sie interagieren:

| Condition | Effekt bei niedrig | Quelle |
|-----------|-------------------|--------|
| Hunger | Geschwächt, langsamer | Zeit ohne Essen |
| Durst | Desorientierung, Tod | Zeit ohne Wasser |
| Fatigue | Aktionen kosten mehr AP | Zeit ohne Schlaf |
| Hypothermie | Frostbeulen, Organversagen | Kälte ohne Shelter |
| Krankheit | Alle Stats reduziert | Infizierte Wunden, rohes Fleisch |
| Schmerz | Aktionen fehlschlag-anfällig | Unbehandelte Wunden |
| Intoxikation | Halluzinationen | Alkohol, verdorbene Nahrung |

**Konkretes Beispiel:**
- Verwundet → unbehandelt → Infektion → Fieber → kann nicht schlafen → Fatigue → kann nicht jagen → Hunger → Tod
- Die Todesursache ist fast nie eine einzelne Condition — es ist die Kaskade
- Shelter schützt vor Hypothermie, aber nicht vor Hunger. Man braucht immer mehrere Lösungen parallel.

**Warum relevant für PPP:** Das ist die Vorlage für M2.4 (Gesundheitssystem). PPPs aktuelles HP/Energy-Modell ist zu simpel. Eine Condition-Web — wo Bedingungen sich gegenseitig beeinflussen — erzeugt emergente Dramatik ohne geskriptete Events. Kein „Script: Tag 5 passiert X" nötig — die Mechanics erzeugen die Geschichte.

### 4. Substitutions-Crafting

**Wie es funktioniert:** Rezepte spezifizieren **Kategorien**, nicht spezifische Items. Ein Gewehrzielfernrohr kann aus einem halben Fernglas gebaut werden. Eine Lärmfalle aus einer Pillendose + Kieselsteinen. Das System checkt: „Hat das Item die benötigten Eigenschaften?" statt „Ist es Item-ID 47?"

**Konkretes Beispiel:**
- Rezept „Noise Trap": braucht CONTAINER + NOISEMAKER
- CONTAINER = Pillendose ODER Blechdose ODER Plastikflasche
- NOISEMAKER = Kieselsteine ODER Kronkorken ODER Glassplitter
- 3 × 3 = 9 verschiedene Kombinationen für EIN Rezept
- Ergebnis-Qualität variiert je nach verwendeten Materialien

**Warum relevant für PPP:** Das ist **exakt**, was PPPs Tag-System erreichen will — und Neo Scavenger beweist, dass es funktioniert. PPPs Blueprints müssen Item-ID-unabhängig sein. Ein Blueprint sagt: „SHARP + HANDLE + BINDING", und der Spieler experimentiert mit: Flint + Ast + Gras vs. Obsidian + Knochen + Sehne. Beide ergeben eine Axt — mit unterschiedlicher Qualität.

### 5. Detailliertes Wundensystem

**Wie es funktioniert:** Wunden sind nicht „-10 HP". Jede Wunde hat:
- **Lokalisation:** Kopf, Torso, linker/rechter Arm/Bein
- **Typ:** Schnitt, Prellung, Bruch, Verbrennung, Biss
- **Zustand:** Blutet, infiziert, behandelt (Bandage), unbehandelt
- **Konsequenzen:** Kopfwunde → Desorientierung. Beinwunde → langsamere Bewegung. Armwunde → Crafting erschwert.

**Konkretes Beispiel:**
- Kampf mit Wolf → Biss am linken Arm → „Blutende Bisswunde, linker Unterarm"
- Ohne Behandlung → Blutung → Blutverlust → Fatigue
- Nach 12h unbehandelt → „Infizierte Bisswunde" → Fieber
- Mit sauberem Tuch + Alkohol behandelt → „Verbundene, saubere Wunde" → heilt in 3 Tagen
- Narbe bleibt → +1% Infektionsresistenz an dieser Stelle (positive Narbe!)

**Warum relevant für PPP:** Das erweitert URWs Body-Part-System um systemische Konsequenzen. Nicht nur „Arm gebrochen = kann nicht kämpfen", sondern eine Wund-Kaskade mit Zeitdruck. Infektion ist ein Timer, der den Spieler zu Entscheidungen zwingt: „Suche ich Heilkräuter oder riskiere ich es?"

---

## Top 3 Adaptionen für Project Primal Process

### 1. Tag-basierte Item-Substitution im Crafting

**PPP-Adaption:**
- Blueprints definieren Slots mit Tag-Anforderungen, nicht Item-IDs
- `Blueprint("Axe", slots={"head": ["SHARP", "STONE"], "handle": ["LONG", "RIGID"], "binding": ["FLEXIBLE", "FIBER"]})`
- Der Spieler kann beliebige Items mit passenden Tags in jeden Slot legen
- Unterschiedliche Kombinationen → unterschiedliche Qualität und Haltbarkeit
- Das ist das Kernversprechen von PPPs Tag-System — Neo Scavenger validiert den Ansatz

**Umsetzung:** `Blueprint.slots: dict[str, list[Tag]]`. `try_combine()` matched Tags, nicht Item-Namen.

### 2. Condition-Web statt HP/Energy

**PPP-Adaption:**
- Ersetze/statt `Player.hp, Player.energy` durch `Player.conditions: dict[str, float]`
- Conditions: `warmth, hydration, satiety, rest, health, morale`
- Jede Condition 0.0–1.0, tickt pro Zeiteinheit
- Interaktionen: `warmth < 0.2 → rest` sinkt schneller. `health < 0.3 → morale` sinkt
- Bei `health = 0.0` → Tod. Aber der Spieler stirbt fast nie direkt an einer Condition

**Umsetzung:** `engine/conditions.py` — ConditionWeb-Klasse. Getter/Setter mit Kaskadenlogik.

### 3. Starting Scenario Traits

**PPP-Adaption:**
- Spielstart wählt ein „Scenario" mit permanenten Traits
- „Forest Child": +foraging, +stealth, -cold_resistance, startet im Wald
- „Coastal Wanderer": +fishing, +swimming, -plant_knowledge, startet an Küste
- „Exiled Hunter": +combat, +tracking, -social, startet allein in Steppe
- Traits modifizieren Skill-Lernraten, Start-Bedingungen, verfügbare frühe Blueprints

**Umsetzung:** `data/scenarios.json` — definiert Start-Traits, Inventar, Location. `Player.traits: set[Trait]`.

---

## Was PPP *nicht* übernehmen sollte

- **Permadeath:** Neo Scavenger's striktes Permadeath (Save gelöscht) ist zu hart für ein Entdeckungsspiel. PPP sollte Wissen erhalten (entdeckte Blueprints bleiben) aber Ressourcen/Position zurücksetzen. „Soft Permadeath".
- **Hex-Karte:** Taktische Hex-Map ist Overkill für PPP Phase 0-3. Abstrakte Locations mit Reisezeit reichen. Kann in Phase 4 evaluiert werden.
- **Hacking/Story:** Neo Scavenger's Cyberpunk-Story-Elemente (Laptops knacken, Daten-Mining) sind genre-fremd für PPP. Discovery kommt aus der Welt, nicht aus Datapads.