# Checklist Philosophy — plain-language checklists are the alert engine

Established 2026-08-12 (founder brainstorm, CarSah). The trigger event: 38
locked-sequence build steps passed while the 3-tab bottom navigation — an
Active capability in File 24 §3.1, designed in the prototype, tested in
File 14 TC-I18N-003 — was NEVER BUILT. Long spec files hide absences. A short
plain-language checklist catches what long files hide.

## Core principle

**Checklists are the engine that alerts you to what is missing.** The build
sequence (File 18) tracks STEPS; it does not track whether the APP exists as a
whole. Every release gate and every 10 build steps, a non-technical person
must be able to answer "does the app actually exist?" by OPENING IT — not by
reading code.

## Design rules (founder-validated)

1. **Plain language, non-technical.** Questions a founder/owner answers by
   walking the app: "Can I move between Home, History and Settings from a bar
   at the bottom?" Not "NavigationBar widget present in shell". The audience
   is the human, not the engineer.

2. **Three states per item — with a mandatory reference for N/A.**
   مطبق (applied) / غير مطبق (not applied) / لا ينطبق (N/A). The N/A cell is
   a liability: without a required reference (a DEC, a spec line) it becomes
   the default answer and the checklist dies silently. Rule: every N/A MUST
   cite the decision that makes it inapplicable, or it counts as NOT applied.

3. **Multiple focused checklists, not one giant list.** At minimum four:
   - **Pre-flight (جاهزية)** — is the foundation ready BEFORE building? (3.5)
   - **Completeness (اكتمال)** — does the app exist as an app? (owner walks it)
   - **Compliance (التزام)** — did the build follow the rules? (auditor)
   - **Release (إطلاق)** — can it ship? (owner + engineer)
   One 20-item list per type. A 500-item list is not read and dies as a
   document. Each list has one owner who answers it.

4. **Pre-built general checklists + project checklists born at 3.5.**
   General lists (from accumulated experience — the lens catalog, the
   completeness template) exist BEFORE the project. Project-specific lists
   MUST be born at Stage 3.5 from the project's own specs (prototype,
   DECs, permissions) — a general list alone asks "is there a nav bar?" (the
   class); the project list asks "is the 3-tab nav (Home/History/Settings)
   matching the prototype?" (the specific). A general-only list can false-flag
   a design that intentionally has no tabs.

5. **Dedicated file, stable IDs.** A separate section or file (e.g.
   `24_active_capabilities.md §7` or a `checklists/` directory), each item
   with a stable ID (Q-01, Q-02…) so gates, reviews and commits can reference
   them. Each list ends with a "Last checked: date + who + device" line —
   accountability.

6. **Checklists themselves get audited.** A wrong checklist is worse than no
   checklist (it produces "applied" confidently forever — the STOP-28 lesson:
   a wrong rule written as doctrine spreads perfectly). The checklist set is
   reviewed periodically like the lenses: does each question measure what it
   claims? Can a violation exist while all boxes are ticked?

## The checklist → gate → guard triad

- **Checklist** detects the absent (human answers it) — but is forgettable.
- **Gate** freezes the detected (test fails the build) — but cannot detect
  what it does not know about.
- **Guard** prevents regression (permanent scan) — but only for shapes it
  knows.
- A checklist without a gate is a memory aid; a gate without a checklist is
  blind to unknown unknowns. The completeness checklist's job is to CREATE the
  gate: every "not applied" on a checklist is a candidate automated gate.
