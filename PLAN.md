# Project Primal Process — Plan

> Lebendes Dokument: wird vom Direktor (So 18:00) neu geschrieben.
> Grenze: CONSTITUTION.md.

## Aktueller Zustand

Peter hat am 22.08. alle offenen Entscheidungen gefällt (siehe `DECISIONS_Response_2026_08_21.md`).
Er hat freigegeben: skill_spread umdeuten (Option A), craft_variety v2, content_reachable v2,
feedback_quality v3, session_depth v2 (Probezeit 14 Tage), tool-aware reachability (REC-002),
SPEC-006 (priorisiert) und forage_pressure v2. Damit ist die Mess-Blockade des Nordsterns aufgelöst.
`session_depth` (25, flach) kann jetzt bewegt werden. Das Spiel ist messgesund: `blueprint_reachability`
1.0, `content_reachable` 1.0, `discovery_gap` 0.6 (im Band, known-fragile), `craft_variety` 3.5.

## Was als nächstes besser werden muss

1. **Die zweite Discovery-Schicht liefern** — Metrik: `session_depth` (hoeher = besser).
   Mit dem ziel-bewussten v2-Bot und tool-aware reachability ist SPEC-006 nicht mehr blockiert.
   Reihenfolge: Ehrlichmachungs-Batch, dann REC-002, dann SPEC-006.
   Erst eine Ehrlichmachung, sonst misst man die Schicht falsch.
   Die erste v2-Lesung liest hoeher, ohne dass sich das Spiel aendert — das ist Re-Baselining, kein Fortschritt (Peter).

2. **Die Zahlen ehrlich machen.**
   skill_spread: Label umdeuten. craft_variety v2: zaehlt auch Prozesse.
   content_reachable v2: dangling Node-Referenzen zeigen sich. feedback_quality v3: NEAR_MISS ist informativ.
   Metriken sind Indikatoren, keine Ziele.

3. **discovery_gap nachhaltig im Band halten.**
   Den Bandrand 0.6 akzeptieren, nicht aufs Band optimieren.
   Steigt der Gap ueber 0.6: das ist ein Spiel-Signal (naive finden Tier-2 nicht).
   Antwort ist spiel-seitig: NEAR_MISS erweitern, Hinweise, Gate-Balance. Niemals eine Metrik abschwaechen.
   Konkreter Hebel heute: NEAR_MISS auf 2-Slot-Blueprints erweitern (spear, spear_bound koennen nie near-missen).

## Tasks

> Offene Aufgaben mit Akzeptanzkriterien. Dev arbeitet von oben nach unten.

- [x] **Ehrlichmachungs-Batch** (Freigabe 22.08., Pkt. 1-4, eine Session). Vier Metrik-Korrekturen:
      skill_spread Option A (Formel bleibt, Label umdeuten); craft_variety v2 (Prozesse zaehlen);
      content_reachable v2 (dangling Nodes pruefen); feedback_quality v3 (NEAR_MISS maplen, plus Vollstaendigkeit).
      Gross testen. Keine andere Metrik ungewollt schwaechen. — **umgesetzt 24.08.** (228 Tests gruen,
      erste Lesung craft_variety 3.5→5.0, feedback_quality 0.916→1.0, content_reachable 1.0/keine dangling,
      skill_spread Formel unveraendert, Richtung auf niedriger)

- [x] **session_depth v2 — ziel-bewusster Bot** (Freigabe 22.08., Pkt. 5). Probezeit 14 Tage, beobachtend.
      Bot verfolgt NEAR_MISS, versucht BPs mit >= 2/3 Materialien, ab survival >= 0.4 auch gated BPs.
      Erste v2-Lesung als neue Baseline dokumentieren, nicht feiern. — **umgesetzt 25.08.** (v2-Bot öffnet
      Tier-2: rope/cord_spear erreicht, Erst-Lesung 64.5 als höhere Re-Baseline — kein Fortschritt, Peter;
      231 Tests grün)

- [x] **REC-002 — tool-aware reachability** (Freigabe 22.08., Pkt. 6). Zähler misst, was die
      Engine craften kann, inkl. Werkzeug-Bau als Vorschritt. — **umgesetzt 26.08.** (Fixpunkt-
      Oracle `_reachable_blueprints`: baut rope zuerst, nutzt dessen CORD-Tag als Zutat;
      ordnungsunabhängig statt Listenkopplung; reachability 1.0 + gap 0.6 unverändert — keine
      andere Metrik gesenkt; Patch-Entwurf + Tests in `proposals/REC-002-tool-aware-reachability.md`)

- [x] **SPEC-006 — Werkzeug als Zutat** (priorisiert, nach Ehrlichmachung + REC-002). Die
      Tier-2-Layer existiert seit SPEC-008 (`rope`→`cord_spear`, cord_spear konsumiert rope-CORD als
      Zutat); REC-002 (26.08.) macht den Zähler tool-aware — was fehlte war der Einmal-Reveal. —
      **Kern umgesetzt 26.08.** (`Player.known_components` + generischer Einmal-Hinweis nach erstem
      Werkzeugbau, kein Rezept-Leak; als Zusatz-Meldung am SUCCESS, kein Metrik-Kern; 240 Tests grün,
      alle Metrikwerte unverändert). Numerische Akzeptanz (`session_depth` steigend) prüft die nächste
      Play-Scorecard — nicht vom Dev zu erzwingen, siehe Dev-Pitfall.
      Akzeptanz: session_depth (v2) steigend (bei unveränderten Seeds), blueprint_reachability 1.0,
      discovery_gap beobachtet. Steigt der Gap über 0.6: Spiel-Signal, Antwort spiel-seitig. Kein Rezept-Leak.

- [ ] **forage_pressure v2** (Freigabe 22.08., Pkt. 8). Gefuehlte Knappheit, nicht stock < max_stock.
      Das Band wird NICHT geschoben. Schwelle schlaegt Dev/Direktor vor. Probezeit 14 Tage.

- [ ] **PLAY-TOOLING: guided_full Rueckzug-Trigger** (keine Freigabe noetig). Jeder Fix nur am kalten Ort,
      gegengetestet ueber 20-Sweep. Messwerkzeug, keine Metrik.

- [ ] **SPEC-010 — Kaltstart-Bruecke (actions_to_first_craft)** (Research 25.08.). Ein knappbarer
      `pebble`-Node im Start-Biome `forest_edge` (STONE+PROJECTILE, max_stock 8, regen 0.04, chance 0.6),
      damit der erste Craft nicht länger den kalten `mountain_peak`-Trip erzwingt. Kein neuer Blueprint,
      kein FLINT-Node. Akzeptanz: `actions_to_first_craft` 34.5 → <20 (Probe: 12.5), reachability/
      content_reachable bleiben 1.0, p75 < 40, pytest gruen. Kein Rezept-Leak.

- [~] *(beobachtend)* **warmth_stability** (Probe bis 27.08.) — 0.460 im Band, flach. Kein Ziel.
- [~] *(beobachtend)* **recovery_stability** (Probe bis 03.09.) — 0.375 im Band, flach. Kein Ziel.
- [x] *(erledigt)* REC-001, SPEC-003, SPEC-005, SPEC-007, SPEC-008, SPEC-009.

---

*Naechste Scorecard-Kontrolle: naechster Play-Job. Plan-Neufassung: naechster Direktor (So).*