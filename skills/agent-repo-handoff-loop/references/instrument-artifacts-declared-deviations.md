# Instrument Artifacts & Declared Deviations (2026-08-15, CarSah P1 compliance follow-up)

## The case

The P1-compliance round (see `prototype-compliance-audit.md`) had a follow-up that
exposed a NEW failure mode: **the auditor's own screenshot lied, and the
implementer's declared deviation caught it.**

- The auditor had claimed «P1's bottom bar is text-only tabs» (the sub-claim that
  justified the founder's text-only instruction for the nav bar).
- The implementer (Sulaiman) built the founder's word anyway — text-only — BUT read
  P1's raw source first, found `navDef` DOES carry 24-px stroke icons, and DECLARED
  the deviation (§16.2) in the code comment, the letter AND the artifact.
- The auditor then verified and admitted: **«I was WRONG and Sulaiman was RIGHT»** —
  the screenshot that showed no icons was itself the artifact: `innerHTML` is a
  `dc-runtime` attribute binding that the React shim (`proto_served.html` injects to
  run locally) silently drops. The auditor reported the artifact of its own
  instrument as P1's design.

## Rules

1. **When a prototype SCREENSHOT and its SOURCE disagree, the source wins.** A
   shimmed prototype can silently drop content (React dropping `dc-runtime`
   `innerHTML` bindings is the measured mechanism). Before asserting what a
   prototype shows, open the raw file — grep the element, don't trust the render.
2. **The declared deviation is the implementer's highest-value move.** When the
   founder's instruction contradicts the binding prototype, build the founder's word
   (it is their call) BUT declare the divergence in the SAME commit — code comment +
   letter + artifact. The declaration is what surfaces the conflict to the auditor;
   a silent build would have ratified the wrong design forever.
3. **The auditor must distinguish «P1 says X» from «my screenshot of P1 shows X».**
   The first is evidence; the second is an observation about the instrument. Own the
   distinction in the letter — and expect the implementer to be the one who catches
   it (they read the source to build the design; the auditor reads it to verify).
4. **Corrections are bidirectional.** Founder → implementer; auditor → itself (the
   emoji claim earlier the same day); AND implementer → auditor (the icons). A
   correction is verified by BREAKING it, not by agreement — the auditor's
   verification was reverting the thirteen clock-wiring sites and watching the guard
   go red; the implementer's icon claim was verified by opening the raw prototype.
   An uncontested claim is not a verified claim.
5. Founder decision after the correction: restore the icons (one-line change in the
   bottom-bar loop) — the recommended closure. «سطر واحد» means one code SITE (the
   tab-building loop), not one literal line.
