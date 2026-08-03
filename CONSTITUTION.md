# Constitution — Project Primal Process

> STATUS: Gültig — freigegeben von Peter am 2026-08-03

## Identität
Ein tiefes, tag-basiertes Primitive-Technology-Discovery-Game. Vom Steinzeit-Überleben zur Eisenzeit-Zivilisation — durch Experimentieren, nicht durch Rezeptbuch. Der Spieler entdeckt Mechaniken durch Kombinatorik, nicht durch Anleitung.
Neue Mechaniken sind ausdrücklich erwünscht, solange sie das Entdecken vertiefen statt es abzukürzen. Das Spiel darf wachsen — in Systemen, nicht nur in Inhalten.

## Nicht-Ziele
Das System soll nie in Richtungen driften, die das Entdecken ersticken: Content-Menge als Selbstzweck (mehr Items ohne das Spiel besser zu machen), Refactoring ohne Metrik-Bezug, eine GUI, die das Textinterface ersetzt, oder Kampf als Kernmechanik statt als Randphänomen.

## Harte Constraints
- Python 3, Textinterface (CLI).
- Tag-basiertes Crafting ist der Kern — bleibt erhalten.
- Keine vorgegebenen Rezepte; Entdeckung durch Experimentieren. Dass der Spieler festhält, was er **selbst** entdeckt hat — Entdeckungsjournal, Hinweise, Experimentiergedächtnis — ist ausdrücklich erlaubt und kein Widerspruch dazu.
- Spiel startet in unter einer Sekunde.
- Keine schweren Abhängigkeiten (kein numpy/torch etc.); stdlib + minimal. **Ausnahme: pydantic** (bereits von `data/loader.py` genutzt, bleibt erlaubt).

## Messung
`tools/scorecard.py`, die Metrikdefinitionen in `METRICS` und der Play-Job gehören zum unantastbaren Kern. Metriken dürfen **ergänzt**, aber nicht entfernt, umdefiniert oder in ihrer Berechnung abgeschwächt werden. Änderungen daran brauchen Peters Freigabe.
Metriken sind Indikatoren, nicht Ziele. Eine Änderung, die eine Metrik hebt, ohne das Spielerlebnis zu verändern, ist ungültig und wird zurückgerollt.
Neue Metriken müssen benennen, welche Schwäche sie erfassen, und zwei Wochen mitlaufen, bevor sie Plan-Ziele steuern dürfen.

## Änderungsregel
Nur Peter ändert diese Datei. Alle anderen Dokumente im Repo sind für Agenten frei änderbar. Jede Agenten-Änderung wird gegen diese Datei geprüft.
