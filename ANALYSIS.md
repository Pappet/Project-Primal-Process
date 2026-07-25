# Project Primal Process — Analysis

## Status
Letzter Commit: 2025-12-28. ~400 Zeilen Python. Textbasiertes CLI-Survival-Spiel.

## Architektur (IST)

```
main.py              → CLI-Game-Loop (gather/eat/experiment/travel)
engine/
  core.py            → GameEngine: Zeit, Wetter, Temperatur, Hunger
  crafting.py        → Blueprint-Matching (Permutationen, Tag-Slots)
  components.py      → Item, ToolBlueprint, Inventory, Player
data/
  items.py           → Template-DB (8 Items)
  locations.py       → 3 Orte mit ResourceNodes
  blueprints.py      → 2 Baupläne (Axt, Messer)
  processes.py       → 3 Prozesse (Knapping, Zunder, Feuer)
```

## Kernmechaniken

1. **Tag-basiertes Emergent Crafting**: Items haben Tags (HARD, SHARP, FIBER, RIGID...). Baupläne definieren Slot→Tag-Mappings. Der Spieler experimentiert mit Kombinationen. Permutation-Check findet Matches. Das ist der Diamant im Code.

2. **Thermodynamik**: body_temp, ambient_temp, exposure, insulation, Wetter-Mods. Bereits solide — Unterkühlung/Hitzschlag implementiert.

3. **Zeit/Hunger-System**: Ticks, Energie-Drain, Essens-Kalorien, Verhungern.

4. **Orte + Ressourcen**: ResourceNodes mit Perception-Gates, Tool-Requirements, Random-Chance.

5. **Wetter**: 4 Typen, alle 12 Ticks Wechsel, Tag/Nacht-Mod auf Temperatur.

## Schwachstellen

| Bereich | Problem |
|---------|---------|
| Persistenz | Kein Save/Load |
| Content | 8 Items, 2 Rezepte, 3 Orte — kaum Spieltiefe |
| UI | Rohes CLI, kein Input-Handling |
| Progression | Kein klares Ziel ausser "nicht sterben" |
| Welt | Keine persistenten Änderungen (kein Shelterbau etc.) |
| Gefahren | Keine Feinde, Krankheiten, Unfälle |
| Testing | Keine Tests |
| Balancing | Keine Daten-getriebene Konfiguration |

## Das Interessante

Der Tag-Crafting-Kern ist ein **kombinatorisches Entdeckungssystem**. Das ist das Alleinstellungsmerkmal. Statt vorgegebener Rezepte entdeckt der Spieler durch Experimentieren. Das skaliert — je mehr Tags, desto mehr emergente Möglichkeiten.

Die Frage ist: Was macht man daraus? Ein reines Survival-Spiel? Ein Technologie-Entdeckungsspiel?

## Empfehlung: "Primitive Technology Discovery Game"

Analog zu *Ancestors: The Humankind Odyssey* aber mit tieferem Crafting: Der Spieler beginnt als Frühmensch und entdeckt Technologien durch Tag-Kombinatorik neu.

**Tech-Stufen** (grobe Skizze):
1. **Steinzeit**: Schlagwerkzeuge, Feuer, einfache Waffen
2. **Neolithikum**: Töpferei, Ackerbau, Viehzucht, Textilien
3. **Kupferzeit**: Schmelzen, Gießen, erste Metallwerkzeuge
4. **Bronzezeit**: Legierungen, Räder, komplexe Architektur
5. **Frühe Eisenzeit**: Hochöfen, Stahl

Progression nicht linear sondern entdeckend — der Spieler weiss nicht, was die nächste Stufe ist.