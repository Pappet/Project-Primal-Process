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
>
> **Triage 2026-08-09 (Direktor):** ✅ B06 + B07 in Dev 07.08. gefixt (Template + Axt trägt SHOVEL) → nach "✅ Triaged". 🟡 Stack-Verschmelzung → **zu SPEC-005 promotet** (PLAN.md). Metrik-Änderungen (Reachability-Blindspot, craft_variety-zählt-Prozesse, content_reachable-blinde-Nodes) → konsolidiert als **Metrik-Anfrage an Peter** (REC-001, PLAN.md) — brauchen Freigabe, bleiben 🔴-frei notiert. forage_pressure / SPEC-003-Konflikte bleiben in Probezeit bzw. suspendiert.
>
> **Triage 2026-08-16 (Direktor):** ✅ REC-001 freigegeben+angewendet (14.08.) → `discovery_gap` ehrlich 0.625 über Band. 🟡 **SPEC-003 REAKTIVIERT** (16.08.): das Über-Band-Gap ist jetzt verifizierbar; SPEC-003 ist die einzige Discovery-Mechanik, die die Lücke *schließt* statt sie zu vergrößern, kein Metrik-Gate → PLAN.md-Task. 🟡 SPEC-006 bleibt auf Peters Freigabe (tool-aware reachability) zurückgestellt — mit Gap über Band würde eine Tier-2-Schicht ihn weiter anheben. skill_spread-Deutung weiter bei Peter (DECISIONS A/B/C). Backlog-Ideen bzgl. Energie-Okonomie-Decke (10.08.) bleiben als ⚪/🔵-Kandidat für spätere Specs notiert; mit Blick auf Discovery-Tiefe PRIORISIERT, nicht verworfen.

---

### 🔴 B06 — `log_oak` liefert "Unbekannt" (dangling Node-Template)
- ~~[2026-08-05] (Play) **`log_oak`-Node (forest_edge, braucht CHOPPING/Axt) referenziert ein Template, das es in `items.json` nicht gibt.** Mit der frisch gebauten Axt Holz fällen → `Gefunden: 1x Unbekannt` (Müll-Item ohne Nutzen). Kernversprechen "Axt bauen, um Holz zu sammeln" bricht in der Hand. **Fix-Richtung:** `log_oak` als echtes Template anlegen oder aus dem Node entfernen.~~ — **✅ erledigt** in Dev-Session 2026-08-07 (Template "Eichenstamm" angelegt, RIGID+WOOD; Axt fällt echten Stamm).

### 🔴 B07 — `clay_lump` doppelt tot (fehlendes Werkzeug + fehlendes Template)
- ~~[2026-08-05] (Play) **`clay_lump`-Node (hidden_cave, braucht `SHOVEL`)**: kein Item trägt das Tag `SHOVEL` → unerreichbar; zusätzlich fehlt das Template in `items.json`. Doppelt toter Content-Pfad. **Fix-Richtung:** SHOVEL-Werkzeug (z.B. Axt/Stab als Grabwerkzeug) einführen und Template anlegen, oder Node entfernen.~~ — **✅ erledigt** in Dev-Session 2026-08-07 (Template "Tonklumpen" + Axt trägt jetzt SHOVEL → Ton erreichbar).

---

## 🟡 Ideas
Mechaniken, Features, Verbesserungen — nicht akut, aber wertvoll.

<!-- Session-Einträge hier drunter -->
- [2026-08-14] (Play) **Naive Spieler sterben jetzt an Unterkühlung statt nur an Hunger — die Kälte ist ein Wartungsloop, kein Entdeckungsziel.** Gegen-Schleife (Feuer+Umhang+Höhle) hält body_temp bei 37 (verifiziert, STORM/SNOW), aber nur mit vollem Set + ständigem Nachlegen alle ~8 Ticks. Nach Entleerung der Entdeckung ist Wärme-Frieren das einzige verbleibende Ziel. Kälte als neue Überlebensschicht gut, aber sie beantwortet nicht die Langeweile-Stelle (`session_depth` 25). Beobachten, ob Wärme-Haltung in fertige Spielziele einmündet, sonst bleibt es Friktion ohne Entdeckung. — warmth_stability/session_depth.
- [2026-08-13] (Dev) **SPEC-007 warmth_stability-Probe: Erstwert 0.460 im Band, aber p25=p75=0.46 (extrem stabil).** Die Metrik unterscheidet aktuell kaum zwischen Seeds — nach der Probezeit (27.08.) prüfen, ob die Streuung mit realistischerem Policy-Verlauf (Feuer bauen muss Material gesammelt/gearbeitet werden statt geführter Ausstattung) informativer wird. Alternativ Band bewerten. — warmth_stability.
- [2026-08-13] (Dev) **Extrem-Kälte (mountain_peak + STORM + Nacht ≈ −18°C) bleibt auch mit Feuer+Umhang tödlich — der Ausweg ist Shelter (hidden_cave, exposure 0.1), nicht das Feuer.** Funktioniert als "Kälte zwingt zur Planung", aber es gibt keine mechanische/erkennbare Andeutung, dass man Schutz suchen soll. Idee: Shelter-Wärmebonus sichtbarer machen oder Kälte-Warnhinweis im CLI bei niedriger Umgebungstemperatur. — session_depth/skill_spread.
- [2026-08-11] (Dev) **SPEC-006 blockiert: Tool-gated Tier-2 regrediert `blueprint_reachability`.** Spec-Annahme „reachability bleibt 1.0" ist gegen die Implementierung falsch: `metric_reachability` sammelt nur Rohstoffe, baut nie Werkzeuge; ein Tier-2-Slot mit `CUTTING`/`CHOPPING` ist im Fresh-Gather-Lauf nie erfüllbar → unreachable. Messung: 0.75 → 0.667/+1, 0.600/+2, 0.545/+3 BPs. Kompensation = `_pair_slots` anfassen = **Peters Freigabe** (gleiche Gate-Familie wie REC-001, aber breiter: auch mit Familien-Fix braucht es „tool-aware reachability"). **Nicht implizit implementieren** — auf Freigabe-Entscheidung (A/B/C in JOURNAL 11.08.) legen. — `session_depth`/`blueprint_reachability`.
- [2026-08-10] (Dev) **skill_spread 0.216 ist kein Tiefen-Regress, sondern gehobene Einsteiger-Decke.** opt (240.5) und rnd (189) sind beide Erstversorgungs-Oekonomie-gebunden und SPEZ-004-Depletion-unabhängig (Harness: Max_Stock=1e9 ändert weder). Fallender Wert = Naive-Spiel überlebt näher an optimal (leichte Einstiege), Experten-Decke unverändert. **Empfehlung an Peter:** Entweder Metrik umdeuten (A) oder opt als Experten-Decke separat ausweisen statt Ratio (B, Metrik-Version-Bump). Braucht Freigabe — Dev hat nichts angefasst. — skill_spread.
- [2026-08-10] (Dev) **Survival-Decke kappt auch das Optimum bei ~240 Ticks (~HORIZON 500).** Optimal-Spiel (beste Location, essen, sammeln) verhungert wegen Energie-/Hungerwirtschaft (Sammel-Energiekosten > Kalorien-Ertrag), unabhängig von Ressourcen-Menge. Zusammen mit `session_depth`~25: die „Langeweile-Stelle" ist nicht nur Discovery-Leere, sondern auch niedrige Ökonomie-Obergrenze. Energie-Balance (passive/Schlaf-Regen) wäre hier Hebel — deckt sich mit älterem BACKLOG-Eintrag „Energie-Balance: drain 10/gather, Start 800, kein Regen". — session_depth/skill_spread.
- [2026-08-07] (Play) **`blueprint_reachability` kann Tag-Familien nicht auflösen — `discovery_gap` untertrieben.** `_pair_slots` matcht Slot-Tags literal (`by_tag.get("SHARP_OR_RIGID")` → leer), kennt `TAG_FAMILIES` nicht → `spear`/`spear_bound` als unreachable gemeldet, obwohl die Engine beide craftet (alle 8 Blueprints SUCCESS, verifiziert). Gemeldet reachability 0.75, wahr 1.0 → wahrer Gap ≈ 0.625 (über Band 0.6), nicht 0.375. **Kein Spiel-Bug, Zählfehler; Metrik-Berechnung ändern → braucht Peters Freigabe** (Constitution). Kalibrierung hat Vorrang vor neuer Discovery-Mechanik (SPEC-003-Grund neu bewertet). **→ Patch-Entwurf + Wirkung geliefert 12.08. (`proposals/REC-001-pair-slots-reachability-fix.md`); Anwendung wartet auf Freigabe.**
- [2026-08-07] (Play) **forage_pressure 0.707 — Probezeit-Kalibrierung bestätigt.** `stock < max_stock` als Schwellenwert zählt jeden Teilerfolg als Knappheit → definitionsbedingt hoch, kein Grind-Gefühl im Kurztest. Band/Definition offen → Direktor-Review bis 20.08.
- [2026-08-06] (Dev) **`forage_pressure` Erstwert 0.71 — über Band 0.1–0.5.** Definition `stock < max_stock` ist ein sehr sensibler Schwellenwert: zählt schon jeden Teilerfolg einer Ernte als "Knappheit", nicht nur echten Entscheidungsdruck. Zwei Lesarten offen: (a) Depletion/Regen über-reibend (Grind), (b) Schwellenwert/Kalibrierung zu grob (der Wert ist teilweise definitionsbedingt hoch). **In Probezeit (bis 20.08.) unter feinerer Policy messen; Band oder Definition braucht Direktor-Review.** — forage_pressure.
- [2026-08-05] (Dev) **Stack-Verschmelzung vs. Mehrfach-Slot-Crafting:** `Inventory.add` verschmilzt gleichnamige Items → Zwei-Slot-Blueprints, die 2× dasselbe Material brauchen, sind nur über zwei DISTINKTE Materialien erreichbar (Speer = reeds+Ast statt 2×Ast; 2× Stick ist im CLI nie als zwei separate Items auswählbar). **→ zu SPEC-005 promotet (Direktor 09.08.)**; mengenbasiertes Matching in `execute_experiment` (Stack mit quantity N kann N Slots füllen). — `craft_variety`/`session_depth`.
- [2026-08-05] (Dev) **SPEC-002 half den Craft-Bottleneck aus BACKLOG 05.08. (Play):** `HARD/SHARP` ist nicht mehr auf `flint_shard` beschränkt — `bone` (BONE+HARD) und `sharp_stone` (STONE+HARD) geben weitere Werkzeug-Pfade (Knochen-/Stein-Variante, Speer via Schilfrohr). Keep-Monitoring, ob der mountain_peak-Funnel entfällt.
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

- [2026-08-14] (Play) **`play/guided_full.py` ist seit SPEC-007 veraltet — friert sich tot und unterschätzt die Erschöpfung.** ~~Prozessliste kennt `make_fur_cloak` nicht (→ Stopp bei 4 statt 5 Prozessen) und der Bot legt nie Feuer nach (`stoke_fire`) → in vielen Runs HP-negativ, Ketten brechen ab, Entdeckungsdecke wird falsch-gemessen (Erschöpfung 28→31 quer über 10 Seeds verrauscht). Fix-Richtung: Prozessliste um `make_fur_cloak` ergänzen + Wärme-Halte-Loop einbauen (Feuer nachlegen, wenn `fire_fuel < 8`, Shelter suchen), sonst misst der rekommendierte Guided-Bot die Discovery-Decke nicht mehr sauber.~~ — **✅ erledigt** in Dev-Session 2026-08-14: `_warmup` baut am warmen Waldrand Knochen-Messer→Zunder→Feuer und holt kurz einen Kiesel (PROJECTILE) für rohes Fleisch + Fell-Umhang (Isolation 0.6); Discovery-Suche hält Feuer am Arbeits-Ort + isst gezielt gegen HP-Blut; 12/15 Seeds leeren jetzt volle 8/8 Blueprints (vorher meist Erfrier-Tod bei 4–5), `make_fur_cloak`/`start_fire` werden entdeckt. — (Play-Messwerkzeug, keine Metrik).
- [2026-07-27] (Dev) ~~`engine/crafting.py:create_dynamic_item` hardcoded auf `components["head"]`~~ — **✅ erledigt** in TASK-M03 (2026-07-29)
- [2026-07-29] (Dev) ~~`data/processes.py` hat noch hartkodierte ProcessDefs — sollte analog zu items/blueprints/locations JSON-Loader bekommen~~ — **✅ erledigt** in TASK-R01 (2026-08-03)
- [2026-07-29] (Dev) ~~`engine/core.py:_create_tool` hat `comp.get("head") or comp.get("blade")` — Fallback vorhanden aber inkonsistent mit fix in crafting.py. Sollte gleiche dynamische Slot-Erkennung verwenden → **TASK-R02**~~ — **✅ erledigt** in Dev-Session 2026-08-15: dynamische Schärfe-Scan (kein hartkodierter Slot-Name mehr), Ein-Slot-Blueprints brechen nicht mehr an `list()[1]`; identisches Verhalten für alle 8 Blueprints (reachability 1.0, discovery_gap 0.625 unverändert).

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
- 🔴 B06 (`log_oak` dangling Template) → erledigt in Dev 2026-08-07 (Template + Axt fällt Holz)
- 🔴 B07 (`clay_lump` doppelt tot) → erledigt in Dev 2026-08-07 (Template + Axt trägt SHOVEL)
- 🟡 (Direktor 09.08.) Stack-Verschmelzung vs. Mehrfach-Slot-Crafting → **SPEC-005** (PLAN.md)