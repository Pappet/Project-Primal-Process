# Ancestors: The Humankind Odyssey — Research Notes

> Panache Digital Games, 2019. Survival/Evolution, Single-Player.
> Désilets (Assassin's Creed). 10M → 2M Jahre, Hominiden-Evolution in Afrika.
> Analysiert: 2026-07-30

---

## 5 Kernmechaniken

### 1. Neuronales Entdeckungssystem (Neural Evolution)

**Wie es funktioniert:** Es gibt keinen klassischen Tech-Tree. Fähigkeiten werden durch Handlungen in der Welt *entdeckt*, nicht durch Punkte gekauft. Wiederholte Aktionen „verstärken" (reinforce) Neuronen. Einmal verstärkt, sind sie permanent — und werden durch Fortpflanzung an die nächste Generation weitergegeben.

**Konkretes Beispiel:**
- Hominide schlägt wiederholt Steine → entdeckt „Alteration" (Bearbeitung)
- Hominide benutzt scharfen Stein auf Holz → entdeckt „Tool Use"
- Erst nach mehreren Generationen → komplexe Werkzeuge möglich

**Warum relevant für PPP:** Das ist die pure Form des emergenten Discovery-Systems, das PPP anstrebt. Kein Rezeptbuch, kein „kaufe Skill für 3 Punkte". Entdeckung durch Tun.

### 2. Angst- und Dopamin-System (Fear & Dopamine)

**Wie es funktioniert:** Unbekannte Gebiete lösen Angst (Fear) aus. Angst wird durch Dopamin kontrolliert — Dopamin kommt von erfolgreichen Aktionen (essen, craften, Ort erobern). Sinkt Dopamin auf Null → Hysterie (Kontrollverlust). Das System zwingt den Spieler, in bekanntem Terrain Kompetenz aufzubauen, bevor er expandiert.

**Konkretes Beispiel:**
- Betritt Dschungel → Fear-Balken erscheint
- Findet Nahrung, craftet Werkzeug → Dopamin ↑, Fear ↓
- Bleibt zu lange ohne Erfolg → Hysterie, Clan-Mitglied läuft panisch weg
- „Conquer"-Aktion auf neuem Ort → Ort wird „bekannt", löst nie wieder Fear aus

**Warum relevant für PPP:** Organisches Pacing. Verhindert Rush zu Endgame-Gebieten. Erzwingt Kompetenzaufbau in jedem Biom. Besser als künstliche Level-Gates.

### 3. Generationen-Lineage (Clan & Legacy)

**Wie es funktioniert:** Der Spieler steuert einen Clan, nicht einen Charakter. Tod → Kontrolle wechselt zu anderem Clan-Mitglied. Alle tot → Extinction, Neustart. Kann zwischen Säugling, Erwachsenem, Ältestem wechseln. Verstärkte Neuronen vererben sich auf die nächste Generation.

**Konkretes Beispiel:**
- Erwachsener stirbt bei Jagd → Spieler übernimmt Jugendlichen
- Verstärkte Neuronen bleiben erhalten (Tool Use, Communication)
- Aber: Inventar des Toten ist verloren
- Fortpflanzung nötig, um Generation voranzutreiben und neue Neuronen zu „locken"

**Warum relevant für PPP:** Death-as-Legacy statt Death-as-Failure. Entdecktes Wissen überlebt den Tod des Charakters. Für M0.4: Save/Load könnte Generationen modellieren — nicht der Charakter speichert, sondern das Wissen des Clans.

### 4. Sensorische Entdeckung (Sensory Intelligence)

**Wie es funktioniert:** Keine Minimap. Keine Quest-Marker. Kein HUD-Kompass. Stattdessen: „Intelligence" (aktiver Scan-Modus) und „Senses" (Hören/Riechen). Hominide ortet Ressourcen, Gefahren, Clan-Mitglieder durch Echoortung-ähnliche Pulse. Neue Objekte müssen zuerst „identifiziert" werden, bevor sie benutzbar sind.

**Konkretes Beispiel:**
- Hominide betritt neues Gebiet → hört unbekanntes Geräusch
- Aktiviert Senses → sieht grüne (Nahrung) / rote (Gefahr) / gelbe (unbekannt) Auren
- Fokussiert auf gelbe Aura → identifiziert „Termitenhügel"
- Nach Identifikation → kann Termiten als Nahrung nutzen, Werkzeug bauen

**Warum relevant für PPP:** Discovery-UI ohne GUI. Die Welt kommuniziert über Sinne, nicht über Icons. PPPs Text-UI könnte Sensorik als Wahrnehmungs-System modellieren: „Du hörst Rauschen im Osten" → Spieler entscheidet zu untersuchen.

### 5. Evolutionäre Physiologie (Physical Evolution)

**Wie es funktioniert:** Evolution ist nicht nur Skill-Fortschritt, sondern physische Veränderung. Bipedalismus wird „entdeckt" und verstärkt → Hominide läuft aufrecht → Hände frei → kann tragen. Hirnvolumen wächst → mehr neuronale Kapazität. Die Spielmechanik ändert sich buchstäblich mit der Biologie des Avatars.

**Konkretes Beispiel:**
- Früher Hominide: Vierbeiner, kann nichts tragen, klettert gut
- Nach Bipedalismus-Verstärkung: Läuft aufrecht, Hände frei, trägt 2 Items
- Nach Hirnwachstum: Mehr aktive Neuronen gleichzeitig, komplexere Werkzeuge
- Nach Daumen-Entwicklung: Präzisionsgriff, feinere Werkzeuge

**Warum relevant für PPP:** Physiologische Änderungen als Mechanik-Gates. Nicht nur „du hast Skill 5, also kannst du Item X craften", sondern „dein Charakter kann physisch noch nicht präzise genug greifen". Für PPP: Skill ≠ Permission — Physiologie kann Permission sein.

---

## Top 3 Adaptionen für Project Primal Process

### 1. Neuronales Entdeckungssystem → Blueprint-Discovery durch Wiederholung

**PPP-Adaption:**
- Blueprints werden nicht gefunden/gekauft, sondern durch wiederholte Experimente entdeckt
- Beispiel: 5× „SHARP + WOOD kombinieren" → Neuron „Tool Use" verstärkt → Axe/Knife-Blueprints freigeschaltet
- „Reinforcement"-Zähler pro Blueprint-Familie statt binärem bekannt/unbekannt
- Entdeckte Blueprints bleiben über Charakter-Tode erhalten (Clan-Wissen)

**Umsetzung:** `Player.blueprint_reinforcement: dict[str, int]` — zählt Experimente pro Mechanik-Kategorie. Bei Schwellwert → Blueprint freigeschaltet.

### 2. Angst/Dopamin → Biom-basierte Erkundungshemmung

**PPP-Adaption:**
- Jedes Biom hat einen `fear_threshold` — bei Unterschreitung → Debuffs (Panik, verirren)
- Erfolgreiche Aktionen im Biom bauen `familiarity` auf
- `familiarity >= fear_threshold` → Biom „erobert", keine Angst mehr
- Neue, gefährlichere Biome haben höhere Fear-Thresholds → erfordern mehr Vorbereitung

**Umsetzung:** `Player.biom_familiarity: dict[str, int]`. `Location.fear_threshold: int`. Jede erfolgreiche Aktion → +1 familiarity. Verhindert Rush zu Endgame-Gebieten.

### 3. Sensorische Entdeckung → Wahrnehmungs-basierte UI

**PPP-Adaption:**
- Statt `print("Du siehst: Stein, Ast, Beeren")` → gestaffelte Wahrnehmung
- „Du hörst ein Rascheln im Osten. Willst du untersuchen?" → Spieler-Aktion
- `Perception`-Skill moduliert, was der Spieler wahrnimmt
- Unbekannte Objekte müssen identifiziert werden („Etwas Rundes, Rötliches am Boden")
- Nach Identifikation → Name und Eigenschaften bekannt

**Umsetzung:** `Location.perception(perception_skill: int) → list[str]` — gibt gestaffelte Beschreibungen je nach Skill-Level. Niedrig: vage, Hoch: präzise.

---

## Was PPP *nicht* übernehmen sollte

- **3D-Perspektive:** Ancestors' Stärke liegt in physischer Immersion (Animationen, Bewegung). PPP ist Text — braucht andere Stärken.
- **Stammes-Management:** Ancestors' Clan-Mechanik (mehrere steuerbare Charaktere) ist überkomplex für PPP Phase 0-3. Reicht als Phase-4-Vision.
- **Realtime-Combat:** Action-basierter Kampf passt nicht zu PPPs textuellem, deliberativem Stil. Turn-basierte Konflikte (wie Neo Scavenger) besser geeignet.